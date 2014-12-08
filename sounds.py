import sys, pygame, glob, os

from pygame.locals import *
import pygame.mixer

pygame.mixer.init()

class Sounds(object):
    def __init__(self):
        self.punches = []
        self.hurt = []

        for filename in glob.glob(os.path.join('resource','sounds','*.ogg')):
            sound = pygame.mixer.Sound(filename)
            sound.set_volume(0.6)
            name = os.path.basename(filename)
            name = os.path.splitext(name)[0]
            if name.startswith('hurt'):
                self.hurt.append(sound)
            elif name.startswith('punch'):
                self.punches.append(sound)
            setattr(self,name,sound)

