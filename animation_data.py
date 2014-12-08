from globals.types import Point
import globals
import bones
from bones import Bones
import copy
import math
import cmath
import random
import copy

standing_frame = {Bones.TORSO : (Point(0.5,0.4),math.pi*0.5),
                  Bones.NECK  : math.pi*0.5,
                  Bones.HEAD  : math.pi*0.5,
                  Bones.LEFT_BICEP : 0,
                  Bones.LEFT_FOREARM : 0,
                  Bones.RIGHT_BICEP : math.pi,
                  Bones.RIGHT_FOREARM : math.pi,
                  Bones.LEFT_THIGH : -math.pi*0.45,
                  Bones.LEFT_CALF : -math.pi*0.45,
                  Bones.RIGHT_THIGH : -math.pi*0.55,
                  Bones.RIGHT_CALF : -math.pi*0.55}

walk1 = {Bones.TORSO : (Point(0.5,0.4),math.pi*0.48),
         Bones.NECK  : math.pi*0.48,
         Bones.HEAD  : math.pi*0.5,
         Bones.LEFT_BICEP : -math.pi*0.45,
         Bones.LEFT_FOREARM : -math.pi*0.3,
         Bones.RIGHT_BICEP : math.pi*1.25,
         Bones.RIGHT_FOREARM : math.pi*1.48,
         Bones.LEFT_THIGH : math.pi*1.35,
         Bones.LEFT_CALF : math.pi*1.15,
         Bones.RIGHT_THIGH : -math.pi*0.30,
         Bones.RIGHT_CALF : -math.pi*0.25}

walk2 = {Bones.TORSO : (Point(0.5,0.35),math.pi*0.48),
         Bones.NECK  : math.pi*0.48,
         Bones.HEAD  : math.pi*0.5,
         Bones.LEFT_BICEP : -math.pi*0.35,
         Bones.LEFT_FOREARM : -math.pi*0.25,
         Bones.RIGHT_BICEP : math.pi*1.15,
         Bones.RIGHT_FOREARM : math.pi*1.3,
         Bones.LEFT_THIGH : math.pi*1.30,
         Bones.LEFT_CALF : math.pi*1.05,
         Bones.RIGHT_THIGH : -math.pi*0.15,
         Bones.RIGHT_CALF : -math.pi*0.45}

walk3 = {Bones.TORSO : (Point(0.5,0.4),math.pi*0.48),
         Bones.NECK  : math.pi*0.48,
         Bones.HEAD  : math.pi*0.5,
         Bones.LEFT_BICEP : -math.pi*0.49,
         Bones.LEFT_FOREARM : -math.pi*0.45,
         Bones.RIGHT_BICEP : math.pi*1.49,
         Bones.RIGHT_FOREARM : -math.pi*0.48,
         Bones.LEFT_THIGH : -math.pi*0.45,
         Bones.LEFT_CALF : math.pi*1.1,
         Bones.RIGHT_THIGH : -math.pi*0.53,
         Bones.RIGHT_CALF : -math.pi*0.55}

walk4 = {Bones.TORSO : (Point(0.5,0.45),math.pi*0.47),
         Bones.NECK  : math.pi*0.47,
         Bones.HEAD  : math.pi*0.5,
         Bones.LEFT_BICEP : math.pi*1.4,
         Bones.LEFT_FOREARM : -math.pi*0.42,
         Bones.RIGHT_BICEP : -math.pi*0.4,
         Bones.RIGHT_FOREARM : -math.pi*0.35,
         Bones.LEFT_THIGH : -math.pi*0.25,
         Bones.LEFT_CALF : math.pi*1.4,
         Bones.RIGHT_THIGH : math.pi*1.25,
         Bones.RIGHT_CALF : math.pi*1.25}

walk_cycle_right = [walk1,walk2,walk3,walk4]

standing_right = {Bones.TORSO : (Point(0.5,0.45),math.pi*0.5),
                  Bones.NECK  : math.pi*0.5,
                  Bones.HEAD  : math.pi*0.5,
                  Bones.LEFT_BICEP : -math.pi*0.25,
                  Bones.LEFT_FOREARM : math.pi*0.25,
                  Bones.RIGHT_BICEP : -math.pi*0.1,
                  Bones.RIGHT_FOREARM : math.pi*0.1,
                  Bones.LEFT_THIGH : -math.pi*0.48,
                  Bones.LEFT_CALF : -math.pi*0.5,
                  Bones.RIGHT_THIGH : -math.pi*0.52,
                  Bones.RIGHT_CALF : -math.pi*0.5}

standing_left = bones.reflect(standing_right)

crouch_right = {Bones.TORSO : (Point(0.4,0.15),math.pi*0.4),
                Bones.NECK  : math.pi*0.375,
                Bones.HEAD  : math.pi*0.5,
                Bones.LEFT_BICEP : -math.pi*0.27,
                Bones.LEFT_FOREARM : math.pi*0.23,
                Bones.RIGHT_BICEP : -math.pi*0.12,
                Bones.RIGHT_FOREARM : math.pi*0.08,
                Bones.LEFT_THIGH : -math.pi*0.1,
                Bones.LEFT_CALF : -math.pi*0.9,
                Bones.RIGHT_THIGH : -math.pi*0.1,
                Bones.RIGHT_CALF : -math.pi*0.9}

crouch_left = bones.reflect(crouch_right)

crouch_right_walk1 = {Bones.TORSO : (Point(0.4,0.25),math.pi*0.4),
                      Bones.NECK  : math.pi*0.375,
                      Bones.HEAD  : math.pi*0.5,
                      Bones.LEFT_BICEP : -math.pi*0.45,
                      Bones.LEFT_FOREARM : math.pi*0.1,
                      Bones.RIGHT_BICEP : math.pi*1.4,
                      Bones.RIGHT_FOREARM : -math.pi*0.1,
                      Bones.LEFT_THIGH : -math.pi*0.4,
                      Bones.LEFT_CALF : math.pi*1.25,
                      Bones.RIGHT_THIGH : -math.pi*0.1,
                      Bones.RIGHT_CALF : -math.pi*0.9}

crouch_right_walk2 = {Bones.TORSO : (Point(0.4,0.16),math.pi*0.4),
                      Bones.NECK  : math.pi*0.375,
                      Bones.HEAD  : math.pi*0.5,
                      Bones.LEFT_BICEP : -math.pi*0.45,
                      Bones.LEFT_FOREARM : math.pi*0.1,
                      Bones.RIGHT_BICEP : math.pi*1.4,
                      Bones.RIGHT_FOREARM : -math.pi*0.1,
                      Bones.LEFT_THIGH : -math.pi*0.4,
                      Bones.LEFT_CALF : math.pi*1.25,
                      Bones.RIGHT_THIGH : -math.pi*0.1,
                      Bones.RIGHT_CALF : -math.pi*0.9}

crouch_right_walk3 = {Bones.TORSO : (Point(0.4,0.25),math.pi*0.4),
                      Bones.NECK  : math.pi*0.375,
                      Bones.HEAD  : math.pi*0.5,
                      Bones.LEFT_BICEP : -math.pi*0.45,
                      Bones.LEFT_FOREARM : math.pi*0.1,
                      Bones.RIGHT_BICEP : math.pi*1.4,
                      Bones.RIGHT_FOREARM : -math.pi*0.1,
                      Bones.LEFT_THIGH : -math.pi*0.1,
                      Bones.LEFT_CALF : -math.pi*0.9,
                      Bones.RIGHT_THIGH : -math.pi*0.4,
                      Bones.RIGHT_CALF : math.pi*1.25}

crouch_right_walk4 = {Bones.TORSO : (Point(0.4,0.16),math.pi*0.4),
                      Bones.NECK  : math.pi*0.375,
                      Bones.HEAD  : math.pi*0.5,
                      Bones.LEFT_BICEP : -math.pi*0.45,
                      Bones.LEFT_FOREARM : math.pi*0.1,
                      Bones.RIGHT_BICEP : math.pi*1.4,
                      Bones.RIGHT_FOREARM : -math.pi*0.1,
                      Bones.LEFT_THIGH : -math.pi*0.1,
                      Bones.LEFT_CALF : -math.pi*0.9,
                      Bones.RIGHT_THIGH : -math.pi*0.4,
                      Bones.RIGHT_CALF : math.pi*1.25}

bow_right_1 = {Bones.TORSO : (Point(0.5,0.4),math.pi*0.5),
               Bones.NECK  : math.pi*0.5,
               Bones.HEAD  : math.pi*0.5,
               Bones.LEFT_BICEP : -0.15*math.pi,
               Bones.LEFT_FOREARM : math.pi*0.25,
               Bones.RIGHT_BICEP : -0.25*math.pi,
               Bones.RIGHT_FOREARM : math.pi*0.25,
               Bones.LEFT_THIGH : -math.pi*0.45,
               Bones.LEFT_CALF : -math.pi*0.45,
               Bones.RIGHT_THIGH : -math.pi*0.55,
               Bones.RIGHT_CALF : -math.pi*0.55}

bow_right_2 = {Bones.TORSO : (Point(0.5,0.4),math.pi*0.15),
               Bones.NECK  : math.pi*0.4 ,
               Bones.HEAD  : math.pi*0.5 ,
               Bones.LEFT_BICEP : -0.05*math.pi,
               Bones.LEFT_FOREARM : math.pi*0.4,
               Bones.RIGHT_BICEP : -0.15*math.pi,
               Bones.RIGHT_FOREARM : math.pi*0.4,
               Bones.LEFT_THIGH : -math.pi*0.45,
               Bones.LEFT_CALF : -math.pi*0.45,
               Bones.RIGHT_THIGH : -math.pi*0.55,
               Bones.RIGHT_CALF : -math.pi*0.55}

bow_cycle_right = [bow_right_1,bow_right_2,bow_right_1]
bow_cycle_left  = [bones.reflect(wc) for wc in bow_cycle_right]

for i in xrange(len(walk_cycle_right)):
    walk = dict(walk_cycle_right[i])
    for (a,b) in ( (Bones.RIGHT_CALF, Bones.LEFT_CALF),
                   (Bones.RIGHT_BICEP, Bones.LEFT_BICEP),
                   (Bones.LEFT_THIGH, Bones.RIGHT_THIGH),
                   (Bones.LEFT_FOREARM, Bones.RIGHT_FOREARM)):
        walk[a],walk[b] = walk[b],walk[a]
    walk_cycle_right.append(walk)

walk_cycle_left = [bones.reflect(wc) for wc in walk_cycle_right]

crouch_cycle_right = [crouch_right_walk1,crouch_right_walk2,crouch_right_walk3,crouch_right_walk4]
crouch_cycle_left = [bones.reflect(wc) for wc in crouch_cycle_right]


class FrameTransition(object):
    def __init__(self,start,end,duration):
        self.start = start
        self.end = end
        self.duration = float(duration)
        self.change = bones.FrameDifference(self.start,self.end)

    def get_frame(self,t):
        return bones.add((self.change*(t/self.duration)),self.start)

class Animation(object):
    position_based = True
    def __init__(self,frames,durations):
        self.frames = []
        self.startx = 0
        self.total_duration = 0
        for i in xrange(len(frames)):
            start_frame = frames[i]
            end_frame = frames[(i+1)%len(frames)]
            duration = durations[i]
            self.total_duration += duration
            self.frames.append(FrameTransition(start_frame,end_frame,duration))

    def get_frame(self,tim,x):
        if self.position_based:
            t = x
        else:
            t = tim - self.startx
        self.num_done = t/self.total_duration
        t %= self.total_duration
        orig = t
        for frame in self.frames:
            if frame.duration > t:
                return frame.get_frame(t)
            t -= frame.duration
        raise Bobbins

class TimeBasedAnimation(Animation):
    position_based = False

class StaticFrame(object):
    def __init__(self,frame):
        self.frame = copy.deepcopy(frame)

    def get_frame(self,t,x):
        return self.frame

walk_right_anim = Animation(walk_cycle_right, (100,300,300,200,100,300,300,200))
walk_left_anim = Animation(walk_cycle_left[::-1], (100,300,300,200,100,300,300,200))
crouch_right_anim = Animation(crouch_cycle_right, (200,200,200,200))
crouch_left_anim = Animation(crouch_cycle_left[::-1], (200,200,200,200))
bow_right_anim = TimeBasedAnimation(bow_cycle_right, (500,500,500))
bow_left_anim = TimeBasedAnimation(bow_cycle_left[::-1], (500,500,500))


class Punch(Animation):
    damping_duration = float(100)
    def __init__(self,player,duration,diff):
        self.duration = duration
        self.player_bones = player.bones
        self.start = globals.time
        self.damping = self.duration + self.damping_duration
        #The final frame will be the right arm pointing directly at it
        distance,angle = cmath.polar(complex(diff.x,diff.y))
        r = cmath.rect(random.random()*5 + 8, angle)
        self.extra_speed = Point(r.real, r.imag)
        self.extra_rotation = (random.random()-0.5) * 0.1

        final = {bone : angle for bone in bones.Bones.right_arm}
        start = {bone : self.player_bones[bone].angle for bone in bones.Bones.both_arms}
        torso_start_pos = self.player_bones[bones.Bones.TORSO].pos/player.size
        torso_start_angle = self.player_bones[bones.Bones.TORSO].angle
        start[bones.Bones.TORSO] = (torso_start_pos,torso_start_angle)
        adjust = math.pi*0.9
        if abs(angle) > math.pi*0.5:
            adjust *= -1

        middle = {bones.Bones.RIGHT_BICEP : (angle + adjust)%(math.pi*2),
                  bones.Bones.RIGHT_FOREARM : angle,
                  bones.Bones.TORSO : (torso_start_pos,torso_start_angle + adjust*0.1)}
        final[bones.Bones.TORSO] = (torso_start_pos, torso_start_angle - adjust*0.1)

        frames = [start,middle,final,final]
        for frame in frames[1:]:
            if abs(angle)*2 > math.pi:
                frame[bones.Bones.LEFT_BICEP] = -math.pi*0.55
                frame[bones.Bones.LEFT_FOREARM] = math.pi*0.55
            else:
                frame[bones.Bones.LEFT_BICEP] = -math.pi*0.45
                frame[bones.Bones.LEFT_FOREARM] = math.pi*0.45
        durations = (self.duration*0.4,self.duration*0.1,self.duration*0.5,1)
        super(Punch,self).__init__(frames,durations)

    def active(self):
        return globals.time < (self.start + self.duration)

    def get_frame(self,t):
        if t > self.duration:
            t = self.duration-1
        return super(Punch,self).get_frame(0,t)
