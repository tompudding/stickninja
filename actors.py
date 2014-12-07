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
import copy
import animation_data

class Directions:
    UP    = 0
    DOWN  = 1
    RIGHT = 2
    LEFT  = 3

class Stances:
    STANDING = 0
    CROUCH   = 1

class Actor(object):
    width  = 10
    height = 20
    scale = 1.5
    size = Point(width*scale,height*scale)
    jump_amount = 4
    def __init__(self,pos):
        self.set_pos(pos)
        self.end_frame = None
        self.children = []
        self.move_direction = Point(0,0)
        self.last_update = None
        self.move_speed = Point(0,0)
        self.torso         = bones.LineBone(self,4*self.scale)
        self.neck          = bones.LineBone(self.torso,1*self.scale)
        self.head          = bones.CircleBone(self.neck,2*self.scale)
        self.left_bicep    = bones.LineBone(self.torso,3*self.scale)
        self.left_forearm  = bones.LineBone(self.left_bicep,3*self.scale)
        self.right_bicep   = bones.LineBone(self.torso,3*self.scale)
        self.right_forearm = bones.LineBone(self.right_bicep,3*self.scale)
        self.left_thigh    = bones.LineBone(self.torso, 4*self.scale, end = bones.ends.START)
        self.left_calf     = bones.LineBone(self.left_thigh, 3*self.scale)
        self.right_thigh   = bones.LineBone(self.torso, 4*self.scale, end = bones.ends.START)
        self.right_calf    = bones.LineBone(self.right_thigh, 3*self.scale)
        self.walked = 0
        self.jumping = False
        self.jumped = False
        self.on_ground = True
        self.dir = Directions.RIGHT
        self.stance = Stances.STANDING
        self.transition_requested = False
        self.still = True
        self.punching = None

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

        self.walking = {Directions.RIGHT : {Stances.STANDING : animation_data.Animation(animation_data.walk_cycle_right,
                                                                                        (100,300,300,200,100,300,300,200)),
                                            Stances.CROUCH   : animation_data.Animation(animation_data.crouch_cycle_right,
                                                                                        (200,200,200,200))},
                        Directions.LEFT  : {Stances.STANDING : animation_data.Animation(animation_data.walk_cycle_left[::-1],
                                                                                        (100,300,300,200,100,300,300,200)),
                                            Stances.CROUCH   : animation_data.Animation(animation_data.crouch_cycle_left[::-1],
                                                                                        (200,200,200,200))}}

        self.standing = {Directions.RIGHT : {Stances.STANDING : animation_data.StaticFrame(animation_data.standing_right),
                                             Stances.CROUCH   : animation_data.StaticFrame(animation_data.crouch_right)},
                         Directions.LEFT  : {Stances.STANDING : animation_data.StaticFrame(animation_data.standing_left),
                                             Stances.CROUCH   : animation_data.StaticFrame(animation_data.crouch_left)}}

        self.current_animation = self.standing[self.dir][self.stance]

        self.arm_angle_distance = {}
        for direction in (Directions.LEFT,Directions.RIGHT):
            self.arm_angle_distance[direction] = {stance : bones.angle_difference(anim.frame[bones.Bones.RIGHT_BICEP],
                                                                                  anim.frame[bones.Bones.LEFT_BICEP])
                                                  for stance,anim in self.standing[direction].iteritems()}

    def add_child(self,child):
        self.children.append(child)

    def set_key_frame(self,frame,duration,damping=1.0):
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
            self.bones[bone].set_key_frame(pos,angle,duration,damping)

    def add_key_frame(self,frame,duration):
        self.pending_frames.append( (frame, duration) )

    def Update(self):
        for child in self.children:
            child.Update()
        if self.end_frame and globals.time > self.end_frame:
            self.end_frame = None
            self.walked = 0

        self.Move()

    def Move(self):
        if self.last_update is None:
            self.last_update = globals.time
            return
        elapsed = globals.time - self.last_update
        self.last_update = globals.time

        self.stance = Stances.STANDING

        if self.on_ground:

            if self.move_direction.y > 0:
                #sort of a jump
                self.move_speed.y += self.move_direction.y*elapsed*0.03
                self.move_direction.y = 0
                self.crouch = False
            elif self.move_direction.y < 0:
                #crouching
                self.stance = Stances.CROUCH

        if self.stance != Stances.CROUCH:
            self.move_speed.x += self.move_direction.x*elapsed*0.03
        else:
            self.move_speed.x += self.move_direction.x*elapsed*0.03*0.6

        #Apply friction
        self.move_speed.x *= 0.7*(1-(elapsed/1000.0))


        self.move_speed.y += globals.gravity*elapsed*0.03

        amount = Point(self.move_speed.x*elapsed*0.03,self.move_speed.y*elapsed*0.03)
        self.walked += amount.x

        # dir = None
        # if amount.x > 0:
        #     dir = Directions.RIGHT
        # elif amount.x < 0:
        #     dir = Directions.LEFT
        # if dir != None and dir != self.dir:
        #     self.dir = dir

        if abs(amount.x) <  0.01:
            self.still = True
            self.walked = 0
            amount.x = 0
            self.move_speed.x = 0
            new_animation = self.standing[self.dir][self.stance]
        else:
            self.still = False
            new_animation = self.walking[self.dir][self.stance]

        if self.transition_requested or self.end_frame is None:
            self.transition_requested = False
            #We can set the frame directly since we're not transitioning
            if new_animation is not self.current_animation:
                #we want to quickly transition to the first frame of the new animation
                self.set_key_frame(new_animation.get_frame(0),100)
            else:
                self.set_key_frame(self.current_animation.get_frame(self.walked*24.0),0)
            self.current_animation = new_animation

        if self.punching:
            elapsed = globals.time - self.punching.start
            if elapsed > self.punching.damping:
                self.punching = False
            else:
                damping = 1.0
                if elapsed > self.punching.duration:
                    damping = (elapsed - self.punching.duration)/self.punching.damping_duration
                    damping = 1.0 - damping
                #transition smoothly back to where it should be
                self.set_key_frame(self.punching.get_frame(globals.time - self.punching.start),0,damping=damping)

        target = self.pos + amount
        if target.y < 0:
            amount.y = -self.pos.y
            self.move_speed.y = 0

        if target.x < 0:
            amount.x = -self.pos.x

        if target.x + self.size.x > globals.game_view.absolute.size.x:
            amount.x = globals.game_view.absolute.size.x - self.size.x - self.pos.x

        target = self.pos + amount

        if abs(target.y) < 0.1:
            self.on_ground = True
        else:
            self.on_ground = False

        self.set_pos(target)

    def set_pos(self,pos):
        self.pos = pos
        self.start_pos_abs = pos
        self.end_pos_abs = pos

    def punch(self,diff):
        if self.punching:
            return
        self.punching = animation_data.Punch(self, self.punch_duration, diff)

    def collides(self,missile):
        centre = self.pos + self.size/2
        #Just skip if it's miles away...
        if (centre-missile.pos).SquareLength() > (self.height+missile.radius)**2:
            return None

        for bone_type,bone in self.bones.iteritems():
            if bone.collides(missile):
                print 'collide on bone',bone_type
                return bone

class Ninja(Actor):
    initial_health = 100
    punch_duration = 400

class Player(Ninja):
    punch_duration = 300
    def __init__(self, *args, **kwargs):
        super(Player,self).__init__(*args, **kwargs)
        self.mouse_pos = Point(0,0)

    def MouseMotion(self,pos,rel):
        self.mouse_pos = pos

    def Update(self):
        super(Player,self).Update()
        diff = self.mouse_pos - self.torso.end_pos_abs
        distance,angle = cmath.polar(complex(diff.x,diff.y))
        if self.punching:
            return

        if abs(angle)*2 > math.pi:
            self.dir = Directions.LEFT
        else:
            self.dir = Directions.RIGHT

        if abs(abs(angle)-0.5*math.pi) < 0.4:
            return

        frame = self.standing[self.dir][self.stance].frame
        aad = self.arm_angle_distance[self.dir][self.stance]

        frame[bones.Bones.RIGHT_BICEP] = angle - aad/2
        frame[bones.Bones.LEFT_BICEP] = angle + aad/2

        #Do the other side too otherwise it looks funny when we cross over...
        other_dir = Directions.LEFT if self.dir == Directions.RIGHT else Directions.RIGHT
        aad = self.arm_angle_distance[other_dir][self.stance]
        angle = math.pi - angle
        frame = self.standing[other_dir][self.stance].frame
        frame[bones.Bones.RIGHT_BICEP] = angle - aad/2
        frame[bones.Bones.LEFT_BICEP] = angle + aad/2


    def Click(self, pos, button):
        #print pos,button
        diff = pos - self.torso.end_pos_abs
        self.punch(diff)

class Missile(object):
    def __init__(self,pos,speed,rotation_speed):
        self.last_update = None
        self.move_speed = speed
        self.rotation_speed = float(rotation_speed)
        self.angle = 0
        self.quad = drawing.Quad(globals.quad_buffer,tc = globals.atlas.TextureSpriteCoords(self.texture_name))
        self.set_pos(pos, self.angle)
        self.dead = False

    def Update(self):
        if self.dead:
            return False
        if self.last_update == None:
            self.last_update = globals.time
            return True
        elapsed = globals.time - self.last_update
        self.last_update = globals.time
        self.move_speed.y += globals.gravity*elapsed*0.03
        amount = Point(self.move_speed.x*elapsed*0.03,self.move_speed.y*elapsed*0.03)

        bone = globals.game_view.player.collides(self)
        if bone:
            print 'collides!',bone

        target = self.pos + amount
        collision = False
        if target.y < self.radius or target.y > globals.game_view.absolute.size.y - self.radius:
            #It's hit the floor
            self.move_speed.y = self.move_speed.y*self.restitution
            collision = True
        elif target.x < self.radius or target.x > globals.game_view.absolute.size.x - self.radius:
            self.move_speed.x = self.move_speed.x*self.restitution
            collision = True

        if collision:
            self.move_speed.x *= 0.8
            self.rotation_speed *= 0.8
            if self.move_speed.SquareLength() < 0.1:
                self.dead = True
            amount = Point(self.move_speed.x*elapsed*0.03,self.move_speed.y*elapsed*0.03)

        new_angle = self.angle + self.rotation_speed*elapsed*0.03
        self.set_pos(self.pos + amount, new_angle)
        return True

    def set_pos(self,pos,angle):
        self.pos = pos
        self.angle = angle
        vertices = []
        for i in xrange(4):
            r = cmath.rect(self.radius,self.angle + (math.pi*(i*0.5 + 0.25)))
            vertices.append(self.pos + Point(r.real, r.imag))
        self.quad.SetAllVertices(vertices,100)

    def Delete(self):
        self.quad.Delete()

class Shuriken(Missile):
    texture_name = 'shuriken.png'
    radius = 4
    restitution = -0.1
