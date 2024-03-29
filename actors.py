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
        self.left_bicep    = bones.LineBone(self.torso,3.5*self.scale)
        self.left_forearm  = bones.LineBone(self.left_bicep,3*self.scale)
        self.right_bicep   = bones.LineBone(self.torso,3.5*self.scale)
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
        self.health = self.initial_health
        self.in_bow = False

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

        self.walking = {Directions.RIGHT : {Stances.STANDING : animation_data.walk_right_anim,
                                            Stances.CROUCH   : animation_data.crouch_right_anim},
                        Directions.LEFT  : {Stances.STANDING : animation_data.walk_left_anim,
                                            Stances.CROUCH   : animation_data.crouch_left_anim}}

        self.standing = {Directions.RIGHT : {Stances.STANDING : animation_data.StaticFrame(animation_data.standing_right),
                                             Stances.CROUCH   : animation_data.StaticFrame(animation_data.crouch_right)},
                         Directions.LEFT  : {Stances.STANDING : animation_data.StaticFrame(animation_data.standing_left),
                                             Stances.CROUCH   : animation_data.StaticFrame(animation_data.crouch_left)}}

        self.bowing = {Directions.RIGHT : animation_data.bow_right_anim,
                       Directions.LEFT  : animation_data.bow_left_anim}

        self.current_animation = self.standing[self.dir][self.stance]

        self.arm_angle_distance = {}
        for direction in (Directions.LEFT,Directions.RIGHT):
            self.arm_angle_distance[direction] = {stance : bones.angle_difference(anim.frame[bones.Bones.RIGHT_BICEP],
                                                                                  anim.frame[bones.Bones.LEFT_BICEP])
                                                  for stance,anim in self.standing[direction].iteritems()}
        self.set_key_frame(self.current_animation.get_frame(0,0),0)

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

    def bow(self):
        self.in_bow = globals.time + 1000

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
                self.move_speed.y += self.move_direction.y*0.5
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
        self.move_speed.x *= math.pow(0.7,(elapsed/20.0))
        if self.gravity:
            self.move_speed.y += globals.gravity*elapsed*0.03

        amount = Point(self.move_speed.x*elapsed*0.03,self.move_speed.y*elapsed*0.03)
        self.walked += amount.x

        if abs(amount.x) <  0.01:
            self.still = True
            self.walked = 0
            amount.x = 0
            self.move_speed.x = 0
            if self.in_bow and globals.time < self.in_bow:
                new_animation = self.bowing[self.dir]
            else:
                self.in_bow = False
                new_animation = self.standing[self.dir][self.stance]
        else:
            self.still = False
            new_animation = self.walking[self.dir][self.stance]


        if self.transition_requested or self.end_frame is None:
            self.transition_requested = False
            #We can set the frame directly since we're not transitioning
            if new_animation is not self.current_animation:
                #we want to quickly transition to the first frame of the new animation
                new_animation.start = globals.time
                self.set_key_frame(new_animation.get_frame(globals.time,0),100)
            else:
                self.set_key_frame(self.current_animation.get_frame(globals.time,self.walked*24.0),0)
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

    def add_score(self,amount):
        pass

    def punch(self,diff):
        if self.punching:
            return
        self.punching = animation_data.Punch(self, self.punch_duration, diff)

    def collides(self,missile):
        centre = self.pos + self.size/2
        #Just skip if it's miles away...
        if (centre-missile.pos).SquareLength() > (self.height+missile.radius)**2:
            return None

        hit = False
        for bone_type,bone in self.bones.iteritems():
            if bone.collides(missile):
                #print 'collide on bone',bone_type
                if self.punching and self.punching.active() and bone_type in bones.Bones.right_arm:
                    self.add_score(missile.hit_points)
                    self.reset_focus()
                    globals.sounds.ping.play()
                    return self.punching.extra_speed, self.punching.extra_rotation
                if bone_type in bones.Bones.damageable:
                    hit = True
        if hit:
            missile.Damage(self)
            return True

    def point_at(self, target):
        diff = target - self.torso.end_pos_abs
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

class Ninja(Actor):
    initial_health = 100
    punch_duration = 300
    gravity = True

class Baddie(Ninja):
    gravity = False
    def __init__(self,*args,**kwargs):
        super(Baddie,self).__init__(*args,**kwargs)
        for b in self.head.circle.band:
            b.SetColour(drawing.constants.colours.red)
    def Update(self):
        super(Baddie,self).Update()
        self.point_at(globals.game_view.player.pos)

class Player(Ninja):
    focus_rate = 0.4
    focus_duration = float(500)
    initial_focus = 5000
    punch_duration = 300
    def __init__(self, *args, **kwargs):
        super(Player,self).__init__(*args, **kwargs)
        self.mouse_pos = Point(0,0)
        barColours = [drawing.constants.colours.red, drawing.constants.colours.yellow, drawing.constants.colours.light_green]
        barBorder = drawing.constants.colours.black
        self.score          = 0
        self.focus          = self.initial_focus
        self.focus_start    = None
        self.focus_end      = None
        self.focus_target   = None
        self.focus_value    = None
        self.focus_change   = None
        self.focused = False
        self.last_focus = 0

        self.health_bar = ui.PowerBar(globals.screen_root, Point(0.8,0.9), Point(0.9,0.93), 1.0, barColours, barBorder)
        self.focus_bar = ui.PowerBar(globals.screen_root, Point(0.1,0.9), Point(0.2,0.93), 1.0, barColours, barBorder)
        self.score_format = '%d'
        self.score_box = ui.TextBox(parent = globals.screen_root,
                                    bl     = Point(0.3,0.9),
                                    tr     = Point(0.7,0.95),
                                    text   = self.score_format % self.score ,
                                    textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                    scale  = 2,
                                    alignment = drawing.texture.TextAlignments.CENTRE)
        self.health_text = ui.ImageBox(globals.screen_root, Point(0.8,0.85), Point(0.9,0.9), 'health.png')
        self.focus_text = ui.ImageBox(globals.screen_root, Point(0.45,0.85), Point(0.55,0.9), 'score.png')
        self.score_text = ui.ImageBox(globals.screen_root, Point(0.1,0.85), Point(0.2,0.9), 'focus.png')

    def MouseMotion(self,pos,rel):
        self.mouse_pos = pos

    def EnableFocus(self):
        if self.focus <= 0:
            return
        globals.sounds.slow.stop()
        globals.sounds.fast.stop()
        globals.sounds.slow.play()
        self.focus_start = globals.real_time
        self.focus_end = globals.real_time + 500
        self.focus_target = self.focus_rate
        self.focus_value = 1.0
        self.focus_change = self.focus_target - self.focus_value
        self.focused = True
        self.last_focus = globals.real_time

    def DisableFocus(self):
        if not self.focused:
            return
        globals.sounds.slow.stop()
        globals.sounds.fast.stop()
        globals.sounds.fast.play()
        self.focus_start = globals.real_time
        self.focus_end = globals.real_time + 500
        self.focus_target = 1.0
        self.focus_value = globals.tick_rate
        self.focus_change = self.focus_target - self.focus_value
        self.focused = False

    def reset_focus(self):
        change = self.initial_focus - self.focus
        self.add_focus(change)

    def add_focus(self,amount):
        self.focus += amount
        if self.focus < 0:
            self.focus = 0
            self.DisableFocus()
        if self.focus > self.initial_focus:
            self.focus = self.initial_focus
        self.focus_bar.SetBarLevel(float(self.focus)/self.initial_focus)

    def Update(self):
        if self.focus_end:
            if globals.real_time > self.focus_end:
                self.focus_end = None
                globals.tick_rate = self.focus_target
            else:
                elapsed = globals.real_time - self.focus_start
                partial = elapsed / self.focus_duration
                globals.tick_rate = self.focus_value + self.focus_change*partial

        diff = globals.real_time - self.last_focus
        self.last_focus = globals.real_time
        if self.focused:
            self.add_focus(-diff)
        else:
            self.add_focus(diff/2)

        super(Player,self).Update()
        diff = self.mouse_pos - self.torso.end_pos_abs
        self.point_at(self.mouse_pos)

    def Damage(self,amount):
        self.health -= amount
        random.choice(globals.sounds.hurt).play()
        if self.health <= 0:
            globals.mode = globals.game_view.mode = modes.GameOver(globals.game_view)
            return
        self.health_bar.SetBarLevel(float(self.health)/self.initial_health)

    def Click(self, pos, button):
        #print pos,button
        diff = pos - self.torso.end_pos_abs
        random.choice(globals.sounds.punches).play()
        self.punch(diff)

    def add_score(self,amount):
        self.score += amount
        self.score_box.SetText(self.score_format % self.score)

class Leaf(object):
    texture_name = 'leaf.png'
    def __init__(self,right=False):
        self.pos = globals.screen*Point(1.0 if right else random.random(),random.random()*2 if right else random.random())
        self.radius = 4
        self.angle = random.random()*math.pi*2
        self.quad = drawing.Quad(globals.quad_buffer,tc = globals.atlas.TextureSpriteCoords(self.texture_name))
        self.set_pos(self.pos, self.angle)
        self.move_speed = Point(-1 + (random.random()-0.5)*0.2,-0.5+ (random.random()-0.5)*0.2)
        self.rotation_speed = (random.random()-0.5)*0.1
        self.dead = False
        self.last_update = None

    def set_pos(self,pos,angle):
        self.pos = pos
        self.angle = angle
        vertices = []
        for i in xrange(4):
            r = cmath.rect(self.radius,self.angle + (math.pi*(i*0.5 + 0.25)))
            vertices.append(self.pos + Point(r.real, r.imag))
        self.quad.SetAllVertices(vertices,100)

    def Update(self):
        if self.dead:
            return False
        if self.last_update is None:
            self.last_update = globals.time
            return True
        elapsed = globals.time - self.last_update
        self.last_update = globals.time
        amount = Point(self.move_speed.x*elapsed*0.03,self.move_speed.y*elapsed*0.03)
        target = self.pos + amount
        new_angle = self.angle + self.rotation_speed*elapsed*0.03
        self.set_pos(target, new_angle)

    def Delete(self):
        self.quad.Delete()
        self.dead = True

class Missile(object):
    ghost_duration = 1000
    def __init__(self,pos,speed,rotation_speed):
        self.last_update = None
        self.move_speed = speed/self.mass2
        self.rotation_speed = float(rotation_speed)
        self.angle = 0
        self.quad = drawing.Quad(globals.quad_buffer,tc = globals.atlas.TextureSpriteCoords(self.texture_name))
        self.set_pos(pos, self.angle)
        self.dead = False
        self.ghost = False

    def Update(self):
        if self.dead:
            return False
        if self.last_update is None:
            self.last_update = globals.time
            return True
        elapsed = globals.time - self.last_update
        self.last_update = globals.time
        self.move_speed.y += globals.gravity*elapsed*0.03
        amount = Point(self.move_speed.x*elapsed*0.03,self.move_speed.y*elapsed*0.03)

        if self.ghost:
            if globals.time > self.ghost:
                self.ghost = False

        if not self.ghost:
            collides = globals.game_view.player.collides(self)
            if collides:
                self.ghost = globals.time + self.ghost_duration
            if collides and collides != True:
                extra_speed, extra_rotation = collides
                self.move_speed += (extra_speed/self.mass)
                self.rotation_speed += extra_rotation

            #print 'collides!',bone

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

    def Delete(self,hit=False):
        if not hit:
            globals.game_view.player.add_score(self.survive_points)
        else:
            #amazing hacks you do with less than an hour left
            self.survive_points = 0
        if self.dead:
            self.quad.Delete()
            return
        self.quad.Delete()
        self.dead = True

    def Damage(self, dude):
        if self.dead:
            return
        dude.Damage(self.damage_amount)
        self.Delete(hit=True)

class Shuriken(Missile):
    texture_name = 'shuriken.png'
    radius = 4
    restitution = -0.05
    damage_amount = 10
    hit_points = 100
    survive_points = 10
    mass = 1.0
    mass2 = 1.0

class Ball(Missile):
    texture_name = 'ball.png'
    radius = 6
    restitution = -0.5
    damage_amount = 20
    hit_points = 250
    survive_points = 25
    mass = 1.2
    mass2 = 2.0
