### Add agents AFTER youve finalized how the spline should look ###
import pygame, math
from code_modules.spline.spline import Spline

############# DEBUG FONT #############
### THE FONT IS USED TO SHOW fOffset AND fMarker ###


class Agent:
    def __init__(self, path: Spline, fMarker = 0):
        self.path = path
        self.nSelectedPoint = 0
        self.fMarker = fMarker

        self.REACHEDEND = False

        self.FORWARD = False
        self.BACKWARD = False

        self.LINESIZE = 20
        self.LINEWIDTH = 8
        ############# DEBUG FONT #############
        ### THE FONT IS USED TO SHOW fOffset AND fMarker ###
        self.font = pygame.font.SysFont(None, 20)

    def update(self, deltaTime, speed):
        if self.FORWARD:
            self.fMarker += speed * deltaTime
        if self.BACKWARD:
            self.fMarker -= speed * deltaTime


        if self.fMarker >= self.path.totalLineLength - speed * deltaTime:
            #self.fMarker -= self.path.totalLineLength
            self.REACHEDEND = True

        if not self.REACHEDEND:
            self.fMarker += speed * deltaTime
            
        if self.fMarker < 0:
            self.fMarker += self.path.totalLineLength

    def draw(self, canvas):
        fOffset = self.path.getNormalizedOffset(self.fMarker)

        p1 = self.path.getSplinePoint(fOffset)
        g1 = self.path.getSplineGradient(fOffset) 

        ### DRAW TANGENT LINE ###
        # r = radiance
        r = math.atan2(-g1.y, g1.x)
        pygame.draw.line(canvas, (0,0,255), 
                    (self.LINESIZE*math.sin(r) + p1.x, self.LINESIZE*math.cos(r) + p1.y),
                    (-self.LINESIZE*math.sin(r) + p1.x, -self.LINESIZE*math.cos(r) + p1.y),
                    self.LINEWIDTH)

        ### DRAW OFFSET AND MARKEKR ###
        tempImg = self.font.render(str(fOffset), True, (255,255,255))
        canvas.blit(tempImg,(10, 10) )
        tempImg = self.font.render(str(self.fMarker), True, (255,255,255))
        canvas.blit(tempImg,(10, 30) )

    def getPos(self, offset = 0):
        fOffset = self.path.getNormalizedOffset(self.fMarker)
        ### TINY POTENTIAL BUG ###
        # Maybe will go outside what fOffset is allowed to be
        # sense we (may) add an offset to it to help towers hit their target.
        pos = self.path.getSplinePoint(fOffset + offset)
        return pygame.Vector2(pos.x, pos.y)

        