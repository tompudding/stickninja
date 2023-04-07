from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
from globals.types import Point
import sys
import actors

class Mode(object):
    """ Abstract base class to represent game modes """
    def __init__(self,parent):
        self.parent = parent

    def KeyDown(self,key):
        pass

    def KeyUp(self,key):
        pass

    def MouseMotion(self,pos,rel):
        pass

    def MouseButtonDown(self,pos,button):
        return False,False

    def Update(self,t):
        pass

class TitleStages(object):
    STARTED  = 0
    COMPLETE = 1
    TEXT     = 2
    SCROLL   = 3
    WAIT     = 4

class Titles(Mode):
    blurb = "STICK NINJA"
    def __init__(self,parent):
        self.parent          = parent
        self.start           = pygame.time.get_ticks()
        self.stage           = TitleStages.STARTED
        self.handlers        = {TitleStages.STARTED  : self.Startup,
                                TitleStages.COMPLETE : self.Complete}
        bl = self.parent.GetRelative(Point(0,0))
        tr = bl + self.parent.GetRelative(globals.screen)
        self.blurb_text = ui.TextBox(parent = self.parent,
                                     bl     = bl         ,
                                     tr     = tr         ,
                                     text   = self.blurb ,
                                     textType = drawing.texture.TextTypes.GRID_RELATIVE,
                                     colour = (1,1,1,1),
                                     scale  = 4)
        self.backdrop        = ui.Box(parent = globals.screen_root,
                                      pos    = Point(0,0),
                                      tr     = Point(1,1),
                                      colour = (0,0,0,0))
        self.backdrop.Enable()

    def KeyDown(self,key):
        self.stage = TitleStages.COMPLETE

    def Update(self):
        self.elapsed = globals.time - self.start
        self.stage = self.handlers[self.stage]()

    def Complete(self):
        self.backdrop.Delete()
        self.blurb_text.Delete()
        self.parent.mode = GameMode(self.parent)

    def Startup(self):
        if self.elapsed < 100:
            return TitleStages.STARTED
        else:
            return TitleStages.COMPLETE

class Level(Mode):
    speed = 200
    splash_time = 2000
    splash_gone = 3000
    splash_fade_duration = float(splash_gone-splash_time)

    direction_amounts = {pygame.K_a  : Point(-0.01*speed, 0.00),
                         pygame.K_d : Point( 0.01*speed, 0.00),
                         pygame.K_w    : Point( 0.00, 0.045*speed),
                         pygame.K_s  : Point( 0.00,-0.01*speed),
                         }
    inv_direction_amounts = {pygame.K_a  : Point(0.01*speed, 0.00),
                             pygame.K_d : Point(-0.01*speed, 0.00),
                             pygame.K_w    : Point( 0.00, 0.00), #hack for jumping
                             pygame.K_s  : Point( 0.00,0.01*speed),
                         }
    direction_amounts[pygame.K_RIGHT] = direction_amounts[pygame.K_d]
    direction_amounts[pygame.K_LEFT] = direction_amounts[pygame.K_a]
    direction_amounts[pygame.K_UP] = direction_amounts[pygame.K_w]
    direction_amounts[pygame.K_DOWN] = direction_amounts[pygame.K_s]
    class KeyFlags:
        LEFT  = 1
        RIGHT = 2
        UP    = 4
        DOWN  = 8
    keyflags = {pygame.K_a  : KeyFlags.LEFT,
                pygame.K_d : KeyFlags.RIGHT,
                pygame.K_w    : KeyFlags.UP,
                pygame.K_s  : KeyFlags.DOWN}
    keyflags[pygame.K_RIGHT] = KeyFlags.RIGHT
    keyflags[pygame.K_LEFT] = KeyFlags.LEFT
    keyflags[pygame.K_UP] = KeyFlags.UP
    keyflags[pygame.K_DOWN] = KeyFlags.DOWN
    jump_keys = [pygame.K_w,pygame.K_UP]
    crouch_keys = [pygame.K_s,pygame.K_DOWN]

    def __init__(self,parent):
        self.parent = parent
        self.keydownmap = 0
        self.start = globals.time
        self.splash = ui.ImageBox(globals.screen_root, Point(0.3,0.4), Point(0.7,0.6), self.splash_texture)
        self.round_sound.play()
        self.in_splash = True
        self.bowed = False

    def KeyDown(self,key):
        if key in self.direction_amounts:
            if not self.keydownmap&self.keyflags[key]:
                self.keydownmap |= self.keyflags[key]
                self.parent.player.transition_requested = True
                if key in self.jump_keys:
                    if self.parent.player.on_ground:
                        self.parent.player.move_direction.y = self.direction_amounts[key].y
                else:
                    self.parent.player.move_direction += self.direction_amounts[key]
        elif key == pygame.K_SPACE:
            self.parent.player.EnableFocus()

    def KeyUp(self,key):
        if key in self.direction_amounts and (self.keydownmap & self.keyflags[key]):
            if self.keydownmap&self.keyflags[key]:
                self.keydownmap &= (~self.keyflags[key])
                if key in self.jump_keys:
                    return
                if key in self.crouch_keys:
                    self.parent.player.move_direction.y = 0
                else:
                    self.parent.player.move_direction -= self.direction_amounts[key]
        elif key == pygame.K_SPACE:
            self.parent.player.DisableFocus()

    def MouseMotion(self,pos,rel):
        #print pos
        self.parent.player.MouseMotion(pos,rel)

    def MouseButtonDown(self,pos,button):
        self.parent.player.Click(pos,button)
        return False,False

    def Update(self):
        elapsed = globals.time - self.start
        if not self.bowed:
            for enemy in globals.game_view.enemies:
                enemy.bow()
            self.bowed = True
        if self.in_splash:
            if elapsed > self.splash_gone:
                self.splash.Disable()
                self.in_splash = False
                self.done = globals.time + self.duration
                for enemy in self.parent.enemies[:self.num_baddies]:
                    extra = max(200,((random.random()-0.5)*2000) + 1000.0/self.rate)
                    enemy.next_projectile = globals.time + extra
                self.next_projectile = globals.time
            elif elapsed > self.splash_time:
                fade_amount = (elapsed - self.splash_time)/self.splash_fade_duration
                self.splash.quad.SetColour((1,1,1,1-fade_amount))
        else:
            if globals.time > self.done:
                self.parent.player.reset_focus()
                self.parent.mode = self.next_stage(self.parent)
                self.parent.mode.keydownmap = self.keydownmap
                #This is probably a race condition. Oh well
                return
            for enemy in self.parent.enemies[:self.num_baddies]:
                if globals.time >= enemy.next_projectile:
                    diff = self.parent.player.pos - enemy.torso.end_pos_abs
                    enemy.punch(diff)
                    source_pos = enemy.right_forearm.end_pos_abs
                    distance = self.parent.player.head.centre - source_pos
                    y_velocity = random.random()*30*self.speed_range
                    a = globals.gravity*30*30
                    x = math.sqrt(y_velocity**2 + 2*a*distance.y)

                    time_to_fall = max((-y_velocity + x)/a,(-y_velocity - x)/a)
                    print time_to_fall
                    x_velocity = distance.x/time_to_fall

                    speed = Point(x_velocity/30.0, y_velocity/30.0)
                    missile = random.choice(enemy.projectiles)(source_pos,
                                                               speed,
                                                               random.random())
                    self.parent.missiles.append(missile)

                    extra = max(200,((random.random()-0.5)*2000) + 1000.0/self.rate)
                    enemy.next_projectile = globals.time + extra

        self.parent.player.Update()
        for enemy in self.parent.enemies:
            enemy.Update()
        for leaf in self.parent.leaves:
            leaf.Update()
            if leaf.pos.x < 0 or leaf.pos.y < 0:
                leaf.Delete()
        orig = len(self.parent.leaves)
        self.parent.leaves = [leaf for leaf in self.parent.leaves if not leaf.dead]
        while len(self.parent.leaves) < orig:
            self.parent.leaves.append(actors.Leaf(right=True))
        new_missiles = []
        for missile in self.parent.missiles:
            if missile.Update():
                new_missiles.append(missile)
            else:
                missile.Delete()

        self.parent.missiles = new_missiles

class LevelOne(Level):
    splash_texture = 'round1.png'
    num_baddies = 1
    duration = 15*1000
    rate = 0.5
    min_speed = 2
    speed_range = 5
    def __init__(self, *args, **kwargs):
        self.next_stage = LevelTwo
        self.round_sound = globals.sounds.round1
        super(LevelOne,self).__init__(*args, **kwargs)

class LevelTwo(Level):
    splash_texture = 'round2.png'
    num_baddies = 2
    duration = 15*1000
    rate = 0.6
    min_speed = 2
    speed_range = 6
    def __init__(self, *args, **kwargs):
        self.next_stage = LevelThree
        self.round_sound = globals.sounds.round2
        super(LevelTwo,self).__init__(*args, **kwargs)

class LevelThree(Level):
    splash_texture = 'round3.png'
    num_baddies = 3
    duration = 15*1000
    rate = 0.6
    min_speed = 2.5
    speed_range = 7
    def __init__(self, *args, **kwargs):
        self.next_stage = LevelFour
        self.round_sound = globals.sounds.round3
        super(LevelThree,self).__init__(*args, **kwargs)

class LevelFour(Level):
    splash_texture = 'round4.png'
    num_baddies = 4
    duration = 15*1000
    rate = 0.7
    min_speed = 3
    speed_range = 8
    def __init__(self, *args, **kwargs):
        self.next_stage = Success
        self.round_sound = globals.sounds.round4
        super(LevelFour,self).__init__(*args, **kwargs)


class GameOver(Mode):
    blurb = "Defeat : Final Score %d"
    def __init__(self,parent):
        self.parent          = parent
        self.blurb           = self.blurb % globals.game_view.player.score
        self.blurb_text      = None
        self.handlers        = {TitleStages.TEXT    : self.TextDraw,
                                TitleStages.SCROLL  : self.Wait,
                                TitleStages.WAIT    : self.Wait}
        self.backdrop        = ui.Box(parent = globals.screen_root,
                                      pos    = Point(0,0),
                                      tr     = Point(1,1),
                                      colour = (0,0,0,0.6))

        bl = self.parent.GetRelative(Point(0,0))
        tr = bl + self.parent.GetRelative(Point(globals.screen.x,globals.screen.y/2))
        self.blurb_text = ui.TextBox(parent = globals.screen_root,
                                     bl     = bl         ,
                                     tr     = tr         ,
                                     text   = self.blurb ,
                                     textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                     scale  = 3,
                                     alignment = drawing.texture.TextAlignments.CENTRE)

        self.start = None
        self.blurb_text.EnableChars(0)
        self.stage = TitleStages.TEXT
        self.played_sound = False
        self.skipped_text = False
        self.letter_duration = 20
        self.continued = False
        if 'ictory' in self.blurb:
            globals.sounds.victory.play()
        else:
            globals.sounds.defeated.play()
        #pygame.mixer.music.load('end_fail.mp3')
        #pygame.mixer.music.play(-1)

    def Update(self):
        if self.start is None:
            self.start = globals.time
        self.elapsed = globals.time - self.start
        self.stage = self.handlers[self.stage](globals.time)
        if self.stage == TitleStages.COMPLETE:
            raise sys.exit('Come again soon!')

    def Wait(self,t):
        return self.stage

    def SkipText(self):
        if self.blurb_text:
            self.skipped_text = True
            self.blurb_text.EnableChars()

    def TextDraw(self,t):
        if not self.skipped_text:
            if self.elapsed < (len(self.blurb_text.text)*self.letter_duration) + 2000:
                num_enabled = int(self.elapsed/self.letter_duration)
                self.blurb_text.EnableChars(num_enabled)
            else:
                self.skipped_text = True
        elif self.continued:
            return TitleStages.COMPLETE
        return TitleStages.TEXT


    def KeyDown(self,key):
        #if key in [13,27,32]: #return, escape, space
        if not self.skipped_text:
            self.SkipText()
        else:
            self.continued = True

    def MouseButtonDown(self,pos,button):
        self.KeyDown(0)
        return False,False

class Success(GameOver):
    blurb = "Victory : Final Score %d"
