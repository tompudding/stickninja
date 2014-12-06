from globals.types import Point
import globals
import drawing
import math

class ends:
    START = 0
    END   = 1

class Bone(object):
    def __init__(self,parent,length,end=ends.END):
        self.children = []
        self.line                 = drawing.shapes.Line(Point(0,0),Point(0,0),globals.line_buffer)
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

    def set_key_frame(self,pos,angle,duration):
        if not duration:
            #This is instant so just set them
            self.pos = pos
            self.angle = angle
            self.keyframe_end = self.keyframe_start = None
            return
        self.keyframe_end   = globals.t + duration
        self.keyframe_start = globals.t
        self.frame_duration = float(duration)
        self.target_pos     = pos
        self.target_angle   = angle
        self.start_pos      = self.pos
        self.start_angle    = self.angle
        self.pos_change     = self.target_pos - self.pos
        self.angle_change   = self.target_angle - self.angle

    def Update(self):
        if self.keyframe_end:
            if globals.t >= self.keyframe_end:
                self.angle = self.target_angle
                self.pos = self.target_pos
                self.keyframe_end = self.keyframe_start = None
            else:
                partial = (globals.t - self.keyframe_start)/self.frame_duration
                self.angle = self.start_angle + (self.angle_change*partial)
                self.pos = self.start_pos + (self.pos_change*partial)
        self.set_pos()
        for child in self.children:
            child.Update()

    def set_pos(self):
        #Update the vertices from parents position and our current angle and position
        if self.end == ends.START:
            self.start_pos_abs = self.parent.start_pos_abs + self.pos
        else:
            self.start_pos_abs = self.parent.end_pos_abs + self.pos

        self.end_pos_abs = self.start_pos_abs + (Point(math.cos(self.angle),math.sin(self.angle))*self.length)
        self.line.set_pos(self.start_pos_abs, self.end_pos_abs)

