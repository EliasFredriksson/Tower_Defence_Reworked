import pygame, os, json
from states.state import State
from constants import MODE
from code_modules.quad_tree.quad_point import QuadPoint
from code_modules.quad_tree.quad_rectangle import QuadRectangle
from code_modules.quad_tree.quad_circle import QuadCircle
from code_modules.quad_tree.quadtree import QuadTree
from code_modules.spline.spline import Spline
from code_modules.spline.spline_point_2D import Spline_Point2D
from code_modules.pointer_list import PointerElement
from code_modules.spline.agent import Agent
from code_modules.enemy import Enemy
from code_modules.tower import Tower
from settings import *

class Game_World(State):
    def __init__(self, game):
        super().__init__(game)

        self.levelData = self.game.levelData["testLevel"]
        self.background = self.game.levelImages["testLevel"]
        self.SHOWBACKGROUND = True
        self.border = self.game.levelBorder

        self.position = pygame.Vector2(100,0)
        self.rect = pygame.Rect(
            self.position.x,
            self.position.y,
            self.background.get_width(),
            self.background.get_height()
            )

        self.path = self.__getPath()
        self.SHOWPATH = True

        self.towersStartPointer = PointerElement()
        self.SHOWTOWERS = True

        self.enemyIdIterator = 0
        self.enemiesStartPointer = PointerElement()
        self.SHOWBALLOONS = True

        self.QUADTREECAPACITY = 8
        self.BOUNDARY = QuadRectangle(self.rect.x, self.rect.y, self.rect.width, self.rect.height)

        self.lives = 100
        self.cash = 500

        self.livesLost = 0
        self.cashLost = 0

        self.ISPLACINGTOWER = False

    ### UPDATE ###
    def update(self, delta_time, actions):
        if self.game.mode == MODE.PLAY:
            self.SHOWPATH = False
        
        if self.game.mode == MODE.DEBUG:
            self.SHOWPATH = True
            self.path.update()

        mousePos = actions["MOUSE_POS"]
        if(actions["ACTION_1"]):
            self.addEnemy("red")

        #Reset QuadTree
        self.qTree = QuadTree(self.BOUNDARY, self.QUADTREECAPACITY)

        #Update ballons
        self.__updateBallons(self.enemiesStartPointer, delta_time, mousePos)
        
        #Update towers
        self.__updateTowers(self.towersStartPointer, delta_time)

            #### LOOP THROUGH ALL ITEMS ####
    def __updateBallons(self, balloonElement: PointerElement, deltaTime, mousePos):
        ### ACTIONS ###
        if balloonElement.hasItem:
            ############################# BALLON UPDATE ###############################

            balloon = balloonElement.item
            balloon.update(deltaTime)

            #Insert the balloon into QuadTree
            ballonPos = balloon.agent.getPos()
            self.qTree.insert(
                QuadPoint(ballonPos.x, ballonPos.y, balloonElement.item)
            )

            ########## OLD CODE TO SPAWN NEW BALLOONS, REPLACED BY takeDamage() #######
            # if balloon.POPPED:
            #     ### WE DETECTED COLLISION ##
            #     for newBallon in balloon.contains:
            #         for amount in range(balloon.contains[newBallon]):
            #             self.addEnemy(newBallon, balloon.agent.fMarker, amount )

            ### CHECK IF REACHED END ###
            if balloon.agent.REACHEDEND:
                self.livesLost += balloon.health

            if balloon.POPPED:
                balloon.spawn(self.addEnemy)
                
            ### WE REMOVE BALLOONS AFTER WE HAVE UPDATED EVERYTHING ELSE ###
            if balloon.agent.REACHEDEND or balloon.POPPED:
                balloonElement.remove()

        if balloonElement.hasNext:
            self.__updateBallons(balloonElement.nextItem, deltaTime, mousePos)
    def __updateTowers(self, towerElement: PointerElement, deltaTime):
        if towerElement.hasItem:
            tower = towerElement.item

            tower.update(deltaTime, self.qTree)
            queryRange = QuadCircle(tower.pos.x, tower.pos.y, tower.range.radius)
            quadPointsInRange = self.qTree.query(queryRange)

            tower.balloonsInRange = []
            for p in quadPointsInRange:
                tower.balloonsInRange.append(p.userData)



        if towerElement.hasNext:
            self.__updateTowers(towerElement.nextItem, deltaTime)

     ### DRAW ###
    def render(self, canvas):
        # DRAW BACKGROUND
        if self.SHOWBACKGROUND:
            canvas.blit(self.background, self.position)

        # DRAW PATH (IF IN DEBUG)
        if self.SHOWPATH:
            self.path.draw(canvas)

        # DRAW BALLONS
        if self.SHOWBALLOONS:
            self.__drawPointerList(self.enemiesStartPointer ,canvas)
    
        # DRAW ANIMATIONS
        #self.animations.get("fire").draw(canvas)

        # DRAW TOWERS
        if self.SHOWTOWERS:
            self.__drawPointerList(self.towersStartPointer, canvas)

        # DRAW LEVEL BORDER
        canvas.blit(self.border, self.position)
    def __drawPointerList(self, element: PointerElement, canvas):
        if element.hasItem:
            element.item.draw(canvas)
            
        if element.hasNext:
            self.__drawPointerList(element.nextItem, canvas)
  
    def addEnemy(self, whichEnemy, tPrevious = 0, offset = 0):
        ### This calc is used to calculate the offset of ballons spawning from
        # other ballons popping.
        if tPrevious <= offset*10:
            tCalc = tPrevious - offset*10
        else:
            tCalc = tPrevious + offset*10

        # CREATE THE BALOON
        enemy = PointerElement()
        enemy.setItem(Enemy(
            Agent(self.path, tCalc), 
            whichEnemy, 
            self.enemyIdIterator, 
            self.game
            ))
        self.enemyIdIterator += 1

        # IF ANY OTHER BALOONS EXISTS:
        if self.enemiesStartPointer.hasNext:
            enemy.setNext(self.enemiesStartPointer.nextItem)

        # ADD THE NEW BALOON
        self.enemiesStartPointer.setNext(enemy)
        return enemy.item.id

    def addTower(self, whichTower):
        # CREATE THE TOWER
        tower = PointerElement()
        tower.setItem(Tower(whichTower, self.game))

        # IF ANY OTHER TOWERS EXISTS
        if self.towersStartPointer.hasNext:
            tower.setNext(self.towersStartPointer.nextItem)
        
        # ADD THE TOWER
        self.towersStartPointer.setNext(tower)
    def removeTower(self):
        if self.ISPLACINGTOWER:
            self.towersStartPointer.nextItem.remove()
        else:
            pass

    ### PART OF CONSTRUCTION ###
    def __getPath(self):
        path = Spline()
        for entry in self.levelData["path"]:
            path.points.append(
                Spline_Point2D(
                    self.levelData["path"][entry]["x_pos"] + self.position[0],
                    self.levelData["path"][entry]["y_pos"] + self.position[1]
                    ))
        path.update()
        return path


    def enter_state(self):
        super().enter_state()

    def exit_state(self):
        super().exit_state()