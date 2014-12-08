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
        self.band = [drawing.Line(source) for i in xrange(3)]
        for b in self.band:
            b.SetColour(drawing.constants.colours.blue)
        self.set_pos(pos)

    def set_pos(self,pos):
        self.pos = pos
        self.points = []
        for i in xrange(self.segments):
            angle = (float(i)/self.segments)*math.pi*2
            p = self.pos + Point( math.cos(angle)*self.radius,math.sin(angle)*self.radius)
            self.points.append(p)
            self.lines[i].SetColour(self.colour)

        angle = math.pi*0.2
        band_start = self.pos + Point( math.cos(angle)*self.radius,math.sin(angle)*self.radius)
        angle = math.pi*0.8
        band_end = self.pos + Point( math.cos(angle)*self.radius,math.sin(angle)*self.radius)
        diff = band_end - band_start
        band_1 = band_start + Point(diff.x/3.0,-self.radius*0.2)
        band_2 = band_start + Point(diff.x*2/3.0,-self.radius*0.2)
        band_positions = [band_start,band_1,band_2,band_end]
        for i in xrange(3):
            self.band[i].SetVertices(band_positions[i],band_positions[i+1],100)


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
