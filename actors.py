from globals.types import Point
import globals
import ui
import drawing
import os
import game_view
import random
import pygame
import cmath
import math
import modes
import bones
from bones import Bones

class Directions:
    UP    = 0
    DOWN  = 1
    RIGHT = 2
    LEFT  = 3

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

for i in xrange(len(walk_cycle_right)):
    walk = dict(walk_cycle_right[i])
    for (a,b) in ( (Bones.RIGHT_CALF, Bones.LEFT_CALF),
                   (Bones.RIGHT_BICEP, Bones.LEFT_BICEP),
                   (Bones.LEFT_THIGH, Bones.RIGHT_THIGH),
                   (Bones.LEFT_FOREARM, Bones.RIGHT_FOREARM)):
        walk[a],walk[b] = walk[b],walk[a]
    walk_cycle_right.append(walk)

walk_cycle_left = [bones.reflect(wc) for wc in walk_cycle_right]

class FrameTransition(object):
    def __init__(self,start,end,duration):
        self.start = start
        self.end = end
        self.duration = duration
        self.change = bones.FrameDifference(self.start,self.end)

    def get_frame(self,t):
        return bones.add((self.change*(t/self.duration)),self.start)

class Animation(object):
    def __init__(self,frames,durations):
        self.frames = []
        self.total_duration = 0
        for i in xrange(len(frames)):
            start_frame = frames[i]
            end_frame = frames[(i+1)%len(frames)]
            duration = durations[i]
            self.total_duration += duration
            self.frames.append(FrameTransition(start_frame,end_frame,duration))

    def get_frame(self,t):
        t %= self.total_duration
        orig = t
        for frame in self.frames:
            if frame.duration > t:
                return frame.get_frame(t)
            t -= frame.duration
        print orig,self.total_duration
        raise Bobbins

class Actor(object):
    width  = 10
    height = 20
    size = Point(width,height)
    def __init__(self,pos):
        self.start_pos_abs = pos
        self.end_pos_abs = pos
        self.end_frame = None
        self.children = []
        self.move_direction = Point(0,0)
        self.last_update = None
        self.move_speed = Point(0,0)
        self.torso         = bones.LineBone(self,6)
        self.neck          = bones.LineBone(self.torso,1)
        self.head          = bones.CircleBone(self.neck,3)
        self.left_bicep    = bones.LineBone(self.torso,3)
        self.left_forearm  = bones.LineBone(self.left_bicep,3)
        self.right_bicep   = bones.LineBone(self.torso,3)
        self.right_forearm = bones.LineBone(self.right_bicep,3)
        self.left_thigh    = bones.LineBone(self.torso, 4, end = bones.ends.START)
        self.left_calf     = bones.LineBone(self.left_thigh, 3)
        self.right_thigh   = bones.LineBone(self.torso, 4, end = bones.ends.START)
        self.right_calf    = bones.LineBone(self.right_thigh, 3)
        self.walked = 0
        self.jumping = False
        self.jumped = False
        self.dir = Directions.RIGHT

        self.bones = {Bones.TORSO         : self.torso,
                      Bones.HEAD          : self.head,
                      Bones.NECK          : self.neck,
                      Bones.LEFT_BICEP    : self.left_bicep,
                      Bones.LEFT_FOREARM  : self.left_forearm,
                      Bones.RIGHT_BICEP   : self.right_bicep,
                      Bones.RIGHT_FOREARM : self.right_forearm,
                      Bones.LEFT_THIGH    : self.left_thigh,
                      Bones.LEFT_CALF     : self.left_calf,
                      Bones.RIGHT_THIGH   : self.right_thigh,
                      Bones.RIGHT_CALF    : self.right_calf}

        self.walking = {Directions.RIGHT : Animation(walk_cycle_right, (100,300,300,200,100,300,300,200)),
                        Directions.LEFT  : Animation(walk_cycle_left, (100,300,300,200,100,300,300,200))}

        self.standing = {Directions.RIGHT : Animation([standing_right,standing_right],(100,100)),
                         Directions.LEFT  : Animation([standing_left,standing_left],(100,100))}

        self.current_animation = self.standing[self.dir]

    def add_child(self,child):
        self.children.append(child)

    def set_key_frame(self,frame,duration):
        if duration:
            self.end_frame = globals.time + duration
        else:
            self.end_frame = None
        for bone, data in frame.iteritems():
            try:
                pos,angle = data
                pos *= self.size
            except TypeError:
                pos = Point(0,0)
                angle = data
            self.bones[bone].set_key_frame(pos,angle,duration)

    def add_key_frame(self,frame,duration):
        self.pending_frames.append( (frame, duration) )

    def Update(self):
        for child in self.children:
            child.Update()
        if self.end_frame and globals.time > self.end_frame:
            self.end_frame = None
        self.Move()

    def Move(self):
        if self.last_update is None:
            self.last_update = globals.time
            return
        elapsed = globals.time - self.last_update
        self.last_update = globals.time

        self.move_speed.x += self.move_direction.x*elapsed*0.03
        if self.jumping and not self.jumped:
            self.move_speed.y += self.jump_amount
            self.jumped = True
        self.move_speed.x *= 0.5*(1-(elapsed/1000.0))
        self.move_speed.y += globals.gravity*elapsed*0.03

        amount = Point(self.move_speed.x*elapsed*0.03,self.move_speed.y*elapsed*0.03)
        self.walked += amount.x

        dir = None
        if amount.x > 0:
            dir = Directions.RIGHT
        elif amount.x < 0:
            dir = Directions.LEFT
        if dir != None and dir != self.dir:
            self.dir = dir

        if abs(amount.x) <  0.0001:
            self.still = True
            self.walked = 0
            amount.x = 0
            self.move_speed.x = 0
            new_animation = self.standing[self.dir]
        else:
            self.still = False
            new_animation = self.walking[self.dir]

        if self.end_frame is None:
            #We can set the frame directly since we're not transitioning
            if new_animation is not self.current_animation:
                #we want to quickly transition to the first frame of the new animation
                self.set_key_frame(new_animation.get_frame(0),100)
            else:
                self.set_key_frame(self.current_animation.get_frame(self.walked*30.0),0)
            self.current_animation = new_animation

class Ninja(Actor):
    initial_health = 100
