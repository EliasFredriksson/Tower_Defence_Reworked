import pygame, json, math
from settings import *
from enum import Enum
from code_modules.collision_functions import * 
from code_modules.pointer_list import PointerElement
from code_modules.projectile import Projectile
from code_modules.enemy import Enemy


############################
class Target(Enum):
    FIRST = 0
    LAST = 1
    STRONG = 2
    CLOSE = 3



class Tower():
    def __init__(self, name, game):
        self.game = game
        self.name = name

        self.pos = pygame.Vector2(-600,-600)

        self.towerSize = game.towerData[self.name]["towerSize"]
        self.baseSize = game.towerData[self.name]["baseSize"]
        self.image = pygame.transform.rotozoom(game.towerImages[self.name], 0, self.towerSize)
        self.base = pygame.transform.rotozoom(game.towerBaseImage, 0, self.baseSize)

        self.collision = Circle(self.pos, self.base.get_width() / 2)
        self.SHOWHITBOX = False

        self.range = Circle(self.pos, game.towerData[self.name]["range"])
        self.rangeImg = pygame.transform.scale(game.towerRangeImage, (self.range.radius * 2 + 5, self.range.radius * 2 + 5))
        
        self.attackType = game.towerData[self.name]["projectile"]
        self.attackProjectileSpeed = game.ProjectileData[self.attackType]["speed"]
        self.projectilesStarterPointer = PointerElement()

        self.fireRate = game.towerData[self.name]["firerate"]
        self.fireRateCounter = 0

        self.angle = 0

        self.prefferedTarget = Target.FIRST
        self.currentTarget = -1
        
        self.SHOWRANGE = False  #IF show range
        self.SELECTED = False   #IF show info about tower
        self.PLACED = False     #IF you can move it around

        self.AIM_OFFSET = 0.05

        self.balloonsInRange = []
     


    def update(self, deltaTime, balloonQuadTree):
        if self.PLACED:
            self.bQuadTree = balloonQuadTree
            self.currentTarget = self.__getTargetedBalloon()
            self.__tryToAttack(deltaTime)
            self.__projectilesUpdate(self.projectilesStarterPointer, deltaTime, balloonQuadTree)

    def draw(self, canvas):
        ### DRAW INFO IF SELECTED ###
        if self.SELECTED or self.SHOWRANGE:
            canvas.blit(self.rangeImg, (self.pos.x - self.rangeImg.get_width()/2,
                                self.pos.y - self.rangeImg.get_height()/2)
            )

        ### DRAW TOWER BASE ###
        canvas.blit(self.base,(self.pos.x - self.base.get_width()/2,
                                self.pos.y - self.base.get_height()/2)
        )
        ### DRAW TOWER ###
        rotatedImage = pygame.transform.rotate(self.image, self.angle)
        canvas.blit(rotatedImage,(self.pos.x - rotatedImage.get_width()/2,
                                self.pos.y - rotatedImage.get_height()/2)
        )

        self.__projectilesDraw(self.projectilesStarterPointer, canvas)

        ### DRAW HITBOX ###
        if self.SHOWHITBOX:
            pygame.draw.circle(
                canvas,
                (255,0,255),
                self.collision.pos,
                self.collision.radius,
                2
            )
   
    def tryMoveTower(self, mousePos):
        if not self.PLACED:
            self.pos.update(mousePos)
            self.SHOWRANGE = True
    def __tryToAttack(self, deltaTime):
        if self.currentTarget != -1:
            if self.fireRateCounter < 0:
                self.__turnToTarget(self.currentTarget)
                self.fireRateCounter = self.fireRate

                tempProjectile = PointerElement()
                tempProjectile.setItem(Projectile(self.attackType, self.game))
                tempProjectile.item.shoot(self.currentTarget, self.pos, self.angle, self.AIM_OFFSET)

                if self.projectilesStarterPointer.hasNext:
                    tempProjectile.setNext(self.projectilesStarterPointer.nextItem)
                self.projectilesStarterPointer.setNext(tempProjectile) 

            else:
                self.fireRateCounter -= 1 * deltaTime
        else:
            if self.fireRateCounter > 0:
                self.fireRateCounter -= 1 * deltaTime
    
    def __projectilesUpdate(self, element: PointerElement, deltaTime, bQuadTree):
        if element.hasItem:
            element.item.update(deltaTime, bQuadTree)

            if element.item.REACHEDMAXDISTANCE or element.item.DEPLETED:
                element.remove()

        if element.hasNext:
            self.__projectilesUpdate(element.nextItem, deltaTime, bQuadTree)
    def __projectilesDraw(self, element: PointerElement, canvas):
        if element.hasItem:
            element.item.draw(canvas)

        if element.hasNext:
            self.__projectilesDraw(element.nextItem, canvas)

    ### ROTATION ###
    def __getTargetedBalloon(self):
        ### PREPARE NUMBER FOR FILTER ###
        targetBalloon = -1
        targetFilter = 0
        strongFirstFilter = 0
        
        if self.prefferedTarget == Target.FIRST or self.prefferedTarget == Target.STRONG:
            targetFilter = 0
        if self.prefferedTarget == Target.LAST or self.prefferedTarget == Target.CLOSE:
            targetFilter = math.inf

        ### PICK PREFFERED BALLOON FROM BALLONS IN RANGE ###
        for b in self.balloonsInRange:
            ### FIRST ###
            if self.prefferedTarget == Target.FIRST:
                if b.agent.fMarker >= targetFilter:
                    targetFilter = b.agent.fMarker
                    targetBalloon = b
            ### LAST ###
            if self.prefferedTarget == Target.LAST:
                if b.agent.fMarker <= targetFilter:
                    targetFilter = b.agent.fMarker
                    targetBalloon = b

            ### STRONG ###
            if self.prefferedTarget == Target.STRONG:
                if b.agent.fMarker >= targetFilter:
                    if b.value >= strongFirstFilter:
                        strongFirstFilter = b.value
                        targetFilter = b.agent.fMarker
                        targetBalloon = b
                        
            ### CLOSE ###
            if self.prefferedTarget == Target.CLOSE:
                tempDistance = getDistancePointVsPoint(self.pos, b.agent.getPos())
                if tempDistance <= targetFilter:
                    targetFilter = tempDistance
                    targetBalloon = b

        ### RETURN BALLOON ###
        if targetBalloon != -1:
            return targetBalloon 
        else:
            return -1
    def __turnToTarget(self, targetBalloon):
        radians = math.atan2(
                targetBalloon.agent.getPos(self.AIM_OFFSET).y - self.pos.y,
                targetBalloon.agent.getPos(self.AIM_OFFSET).x - self.pos.x
                )
        angle = -(radians * 180 / math.pi) - 90
        self.angle = angle
        self.currentTarget = targetBalloon   

    def iteratePointerList(self, element: PointerElement):
        if element.hasItem:
            print("NAME: ", element.item.name, "\tID: ", element.item.id)
            
        if element.hasNext:
            self.iteratePointerList(element.nextItem)
    