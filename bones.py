from globals.types import Point
import globals
import drawing
import math

class ends:
    START = 0
    END   = 1

class Bones:
    TORSO         = 0
    NECK          = 1
    HEAD          = 2
    LEFT_BICEP    = 3
    LEFT_FOREARM  = 4
    RIGHT_BICEP   = 5
    RIGHT_FOREARM = 6
    LEFT_THIGH    = 7
    LEFT_CALF     = 8
    #LEFT_FOOT     = 9
    RIGHT_THIGH   = 10
    RIGHT_CALF    = 11
    #RIGHT_FOOT    = 12

    all_bones = [TORSO,
                 NECK,
                 HEAD,
                 LEFT_BICEP,
                 LEFT_FOREARM,
                 RIGHT_BICEP,
                 RIGHT_FOREARM,
                 LEFT_THIGH,
                 LEFT_CALF,
                 RIGHT_THIGH,
                 RIGHT_CALF]
    right_arm = [RIGHT_BICEP, RIGHT_FOREARM]
    left_arm  = [LEFT_BICEP,  LEFT_FOREARM]
    both_arms = right_arm + left_arm
    damageable = [TORSO, LEFT_THIGH, LEFT_CALF, RIGHT_THIGH, RIGHT_CALF]

def angle_difference(start, end):
    change   = end - start
    if change > math.pi:
        change -= math.pi*2
    elif change < -math.pi:
        change += math.pi*2
    return change

def bone_difference(start, end):
    try:
        start_pos, start_angle = start
        end_pos,   end_angle = end
        return end_pos - start_pos,angle_difference(start_angle, end_angle)
    except TypeError:
        return angle_difference(start, end)

def bone_add(start, end):
    try:
        start_pos, start_angle = start
        end_pos,   end_angle = end
        return end_pos + start_pos,start_angle + end_angle
    except TypeError:
        return start + end


def bone_multiply(data, amount):
    try:
        pos,angle = data
        return pos*amount,angle*amount
    except TypeError:
        angle = data
        return angle*amount

def reflect_item(data):
    try:
        pos,angle = data
        return Point(1-pos.x,pos.y),math.pi-angle
    except TypeError:
        angle = data
        return math.pi-angle

def add(a,b):
    return {bone:bone_add(value, b[bone]) for (bone, value) in a.iteritems()}


def reflect(keyframe):
    return {bone:reflect_item(data) for (bone,data) in keyframe.iteritems()}


class FrameDifference(object):
    def __init__(self,start,end):
        self.data = {}
        for bone in start.viewkeys() & end.viewkeys():
            self.data[bone] = bone_difference(start[bone],end[bone])

    def __mul__(self,other):
        return {bone:bone_multiply(value,other) for (bone,value) in self.data.iteritems()}


class Bone(object):
    def __init__(self,parent,length,end=ends.END):
        self.children = []
        self.end = end
        self.parent               = parent
        self.length               = length
        self.pos = Point(0,0)
        self.angle                = 0
        self.target_pos           = None
        self.target_angle         = None
        self.keyframe_end         = None
        self.keyframe_start       = None
        self.frame_duration       = None
        self.parent.add_child(self)

    def add_child(self,child):
        self.children.append(child)

    def set_key_frame(self,pos,angle,duration,damping=1.0):
        if not duration:
            #This is instant so just set them
            if damping == 1.0:
                self.pos = pos
                self.angle = angle
            else:
                #1.0 is entirely the request, 0.0 is entirely the current
                self.pos = self.pos + (pos-self.pos)*damping
                angle_change = angle_difference(self.angle,angle)
                self.angle = self.angle + angle_change*damping
                self.keyframe_end = self.keyframe_start = None
            return
        self.keyframe_end   = globals.time + duration
        self.keyframe_start = globals.time
        self.frame_duration = float(duration)
        self.target_pos     = pos
        self.target_angle   = angle
        self.start_pos      = self.pos
        self.start_angle    = self.angle
        self.pos_change     = self.target_pos - self.pos
        self.angle_change   = (self.target_angle - self.angle)
        if self.angle_change > math.pi:
            self.angle_change -= math.pi*2
        elif self.angle_change < -math.pi:
            self.angle_change += math.pi*2
        #if self.angle_change > math.pi:
        #    self.angle_change = math.pi*2-self.angle_change

    def Update(self):
        if self.keyframe_end:
            if globals.time >= self.keyframe_end:
                self.angle = self.target_angle
                self.pos = self.target_pos
                self.keyframe_end = self.keyframe_start = None
            else:
                partial = (globals.time - self.keyframe_start)/self.frame_duration
                self.angle = self.start_angle + (self.angle_change*partial)
                self.pos = self.start_pos + (self.pos_change*partial)
        self.set_pos()
        for child in self.children:
            child.Update()

class LineBone(Bone):
    def __init__(self, *args, **kwargs):
        self.line = drawing.shapes.Line(Point(0,0),Point(0,0),globals.line_buffer)
        super(LineBone,self).__init__(*args, **kwargs)

    def set_pos(self):
        #Update the vertices from parents position and our current angle and position
        if self.end == ends.START:
            self.start_pos_abs = self.parent.start_pos_abs + self.pos
        else:
            self.start_pos_abs = self.parent.end_pos_abs + self.pos

        self.end_pos_abs = self.start_pos_abs + (Point(math.cos(self.angle),math.sin(self.angle))*self.length)
        self.line.set_pos(self.start_pos_abs, self.end_pos_abs)

    def collides(self,missile):
        vector = self.end_pos_abs - self.start_pos_abs
        diff = self.start_pos_abs - missile.pos
        a = float(vector.dot_product(vector))
        b = float(2*diff.dot_product(vector))
        c = float(diff.dot_product(diff) - (missile.radius*0.9)**2)
        disc = b*b-4*a*c
        if disc < 0:
            return False
        disc = math.sqrt(disc)
        t1 = (-b - disc)/(2*a)
        t2 = (-b + disc)/(2*2)

        if t1 >= 0 and t1 <= 1:
            return True

        if t2 >= 0 and t2 <= 1:
            return True

        return False

class CircleBone(Bone):
    def __init__(self,parent,length,end=ends.END):
        self.circle = drawing.shapes.Circle(Point(0,0),length, globals.line_buffer)
        super(CircleBone,self).__init__(parent,length,end)

    def set_pos(self):
        if self.end == ends.START:
            self.contact = self.parent.start_pos_abs + self.pos
        else:
            self.contact = self.parent.end_pos_abs + self.pos
        self.centre = self.contact + (Point(math.cos(self.angle),math.sin(self.angle))*self.length)
        self.circle.set_pos(self.centre)

    def collides(self,missile):
        diff = missile.pos - self.centre
        if diff.SquareLength() < ((self.length + missile.radius)**2):
            return True
        return False
