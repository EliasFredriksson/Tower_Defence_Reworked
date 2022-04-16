############## THESE SPLINES ARE USING CATMULL SPLINES ##############
# https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline
#
# FOLLOWING javidx9's SPLINE VIDEOS:
# https://www.youtube.com/watch?v=9_aJGUTePYo&t=898s&ab_channel=javidx9


from typing import List
import pygame, math
from code_modules.spline.spline_point_2D import Spline_Point2D


### THE FONT IS USED TO SHOW fOffset AND fMarker ###

###############


class Spline:
    def __init__(self):
        self.points = []
        self.activePoint = 0
        self.isLooped = False
        self.RIGHT = False
        self.LEFT = False
        self.UP = False
        self.DOWN = False
        self.totalLineLength = 0
        ############# DEBUG FONT #############
        ### THE FONT IS USED TO SHOW fOffset AND fMarker ###
        self.font = pygame.font.SysFont(None, 20)

    def update(self):
        if self.RIGHT:
            self.points[self.activePoint].x += 5
        if self.LEFT:
            self.points[self.activePoint].x -= 5
        if self.UP:
            self.points[self.activePoint].y -= 5
        if self.DOWN:
            self.points[self.activePoint].y += 5
        
        ### CALCULATE TOTAL LENGTH ###
        self.totalLineLength = self.__getTotalLength()

    def draw(self, canvas):
        ##### DRAW SPLINE POINTS #####
        ### LOOPED ###
        if self.isLooped:
            for t in range(0, len(self.points)*100, 1):
                pos = self.getSplinePoint(t / 100)
                pygame.draw.circle(canvas, (255,255,255), (pos.x, pos.y), 2)
        ### NOT LOOPED ###
        else:
            for t in range(0, (len(self.points)*100) - 300 , 1):
                pos = self.getSplinePoint(t / 100)
                pygame.draw.circle(canvas, (255,255,255), (pos.x, pos.y), 2)

        ##### DRAW CONTROL POINTS + TEXT #####
        for i in range(len(self.points)):
            ### DRAW DISTANCE ###
            tempImg = self.font.render(str(self.points[i].length), True, (200,200,200))
            canvas.blit(tempImg, (self.points[i].x + 20, self.points[i].y))
            ##########################

            ##### CONTROL POINTS #####
            if i == self.activePoint:
                pygame.draw.circle(canvas, (255,255,0), (self.points[i].x, self.points[i].y), 5)
            else:
                pygame.draw.circle(canvas, (255,0,0), (self.points[i].x, self.points[i].y), 5)
            tempImg = self.font.render(str(i), True, (255,255,255))
            canvas.blit(tempImg, (self.points[i].x, self.points[i].y))

    def getSplinePoint(self, t):
        if not self.isLooped:
            p1 = int(t) + 1
            p2 = p1 + 1
            p3 = p2 + 1
            p0 = p1 - 1
        else:
            p1 = int(t)
            p2 = (p1 + 1) % len(self.points)
            p3 = (p2 + 1) % len(self.points)
            if p1 >= 1:
                p0 = p1 - 1
            else:
                p0 = len(self.points) - 1
        
        t = t - int(t)
        tSquare = t * t
        tCube = tSquare * t

        q1 = -tCube + 2 * tSquare - t
        q2 = 3 * tCube - 5 * tSquare + 2
        q3 = -3 * tCube + 4 * tSquare + t
        q4 = tCube - tSquare

        tx = 0.5 * (self.points[p0].x * q1 + 
                self.points[p1].x * q2 +
                self.points[p2].x * q3 +
                self.points[p3].x * q4)

        ty = 0.5 * (self.points[p0].y * q1 + 
                self.points[p1].y * q2 +
                self.points[p2].y * q3 +
                self.points[p3].y * q4)

        return Spline_Point2D(tx, ty)
        
    def getSplineGradient(self, t):
        if not self.isLooped:
            p1 = int(t) + 1
            p2 = p1 + 1
            p3 = p2 + 1
            p0 = p1 - 1

        else:
            p1 = int(t)
            p2 = (p1 + 1) % len(self.points)
            p3 = (p2 + 1) % len(self.points)
            if p1 >= 1:
                p0 = p1 - 1
            else:
                p0 = len(self.points) - 1
        
        t = t - int(t)

        tSquare = t * t
        tCube = tSquare * t

        q1 = -3*tSquare + 4*t - 1
        q2 = 9*tSquare - 10*t
        q3 = -9*tSquare + 8*t + 1
        q4 = 3*tSquare - 2*t

        tx = 0.5 * (self.points[p0].x * q1 + 
                self.points[p1].x * q2 +
                self.points[p2].x * q3 +
                self.points[p3].x * q4)

        ty = 0.5 * (self.points[p0].y * q1 + 
                self.points[p1].y * q2 +
                self.points[p2].y * q3 +
                self.points[p3].y * q4)

        return Spline_Point2D(tx, ty)

    def __getTotalLength(self):
        ### CALCULATE TOTAL LENGTH ###
        total = 0
        if self.isLooped:
            for i in range(len(self.points)):
                self.points[i].length = self.__calculateSegmentLength(i)
                total += self.points[i].length
        else:
            for i in range(len(self.points)-3):
                self.points[i].length = self.__calculateSegmentLength(i)
                total += self.points[i].length
        return total

    def __calculateSegmentLength(self, node):
        fLength = 0
        fStepSize = 3
        old_point = self.getSplinePoint(node)
        for t in range(0, 100, fStepSize):
            new_point = self.getSplinePoint(node + t/100)
            fLength += math.sqrt((new_point.x - old_point.x) * (new_point.x - old_point.x)
                                + (new_point.y - old_point.y)*(new_point.y - old_point.y))
            old_point = new_point

        ### You need to recalculate the segment lengths if the spline changes. 
        # which means its very innefficient to use splines dynamically. Preferrably
        # you use them Statically.

        return fLength

    def getNormalizedOffset(self, p):
        # Which node is the base?
        i = 0
        while p > self.points[i].length:
            p -= self.points[i].length
            i += 1

        # The fractional is the offset
        return i + (p / self.points[i].length)

