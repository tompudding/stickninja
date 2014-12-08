from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
from globals.types import Point
import modes
import random
import actors

class GameView(ui.RootElement):
    def __init__(self):
        self.atlas = globals.atlas = drawing.texture.TextureAtlas('tiles_atlas_0.png','tiles_atlas.txt')
        self.game_over = False
        #pygame.mixer.music.load('music.ogg')
        #self.music_playing = False
        super(GameView,self).__init__(Point(0,0),globals.screen)
        #skip titles for development of the main game
        #self.mode = modes.Titles(self)
        self.mode = modes.LevelOne(self)
        self.StartMusic()
        self.border = ui.Border(self,Point(0,0),Point(1,1),colour=drawing.constants.colours.black,line_width=2)
        self.player = actors.Player(self.GetAbsolute(Point(0.5,0)))
        self.platform1 = ui.ImageBox(globals.screen_root, Point(0.8,0.35), Point(0.9,0.375), 'platform.png')
        self.platform2 = ui.ImageBox(globals.screen_root, Point(0.1,0.35), Point(0.2,0.375), 'platform.png')
        self.platform3 = ui.ImageBox(globals.screen_root, Point(0.25,0.65), Point(0.35,0.675), 'platform.png')
        self.platform4 = ui.ImageBox(globals.screen_root, Point(0.65,0.65), Point(0.75,0.675), 'platform.png')
        self.platforms = [self.platform1,self.platform2,self.platform3,self.platform4]

        self.missiles = []
        self.enemies = [actors.Baddie(platform.GetAbsolute(Point(0.24,0.25))) for platform in self.platforms]
        self.enemies[0].projectiles = [actors.Shuriken]
        for enemy in self.enemies[1:]:
            enemy.projectiles = [actors.Shuriken,actors.Ball]

    def StartMusic(self):
        pass
        #pygame.mixer.music.play(-1)
        #self.music_playing = True

    def Draw(self):
        drawing.ResetState()
        drawing.DrawNoTexture(globals.line_buffer)
        drawing.DrawNoTexture(globals.colour_tiles)
        drawing.DrawAll(globals.quad_buffer,self.atlas.texture.texture)
        drawing.DrawAll(globals.nonstatic_text_buffer,globals.text_manager.atlas.texture.texture)

    def Update(self):
        if self.mode:
            self.mode.Update()

        if self.game_over:
            return

    def GameOver(self):
        self.game_over = True
        self.mode = modes.GameOver(self)

    def KeyDown(self,key):
        self.mode.KeyDown(key)

    def KeyUp(self,key):
        if key == pygame.K_DELETE:
            if self.music_playing:
                self.music_playing = False
                pygame.mixer.music.set_volume(0)
            else:
                self.music_playing = True
                pygame.mixer.music.set_volume(1)
        self.mode.KeyUp(key)

    def MouseMotion(self,pos,rel,handled):
        self.mode.MouseMotion(pos,rel)

    def MouseButtonDown(self,pos,button):
        if self.mode:
            return self.mode.MouseButtonDown(pos,button)
        else:
            return False,False
