import drawing
import math
from globals.types import Point

class Circle(object):
    segments = 10
    def __init__(self,pos,radius,source,colour=None):
        if colour is None:
            colour = drawing.constants.colours.black
        self.colour = colour
        self.radius = radius
        self.lines = [drawing.Line(source) for i in xrange(self.segments)]
        self.set_pos(pos)

    def set_pos(self,pos):
        self.pos = pos
        self.points = []
        for i in xrange(self.segments):
            angle = (float(i)/self.segments)*math.pi*2
            p = self.pos + Point( math.cos(angle)*self.radius,math.sin(angle)*self.radius)
            self.points.append(p)
            self.lines[i].SetColour(self.colour)

        for i in xrange(self.segments):
            self.lines[i].SetVertices(self.points[i],self.points[(i+1)%self.segments],100)

class Line(object):
    level = 100
    def __init__(self,start,end,source,colour=None):
        if colour is None:
            colour = drawing.constants.colours.black
        self.colour = colour
        self.line = drawing.Line(source)
        self.set_pos(start,end)
        self.line.SetColour(self.colour)

    def set_pos(self,start,end):
        self.start = start
        self.end = end
        self.line.SetVertices(self.start,self.end,self.level)
