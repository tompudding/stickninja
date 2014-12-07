from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
from globals.types import Point
import sys

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

class GameMode(Mode):
    speed = 200
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

    def MouseMotion(self,pos,rel):
        #print pos
        self.parent.player.MouseMotion(pos,rel)

    def MouseButtonDown(self,pos,button):
        self.parent.player.Click(pos,button)
        return False,False

    def Update(self):
        self.parent.player.Update()
        new_missiles = []
        for missile in self.parent.missiles:
            if missile.Update():
                new_missiles.append(missile)
            else:
                missile.Delete()

        self.parent.missiles = new_missiles


class GameOver(Mode):
    blurb = "Final Score %d"
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
        #pygame.mixer.music.load('end_fail.mp3')
        #pygame.mixer.music.play(-1)

    def Update(self):
        if self.start == None:
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
