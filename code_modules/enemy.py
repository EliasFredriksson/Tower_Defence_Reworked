import pygame, json
from code_modules.spline.agent import Agent
from settings import *
from code_modules.collision_functions import *


class Enemy():
    def __init__(self, givenAgent: Agent, whichEnemy, id, game):
        self.game = game

        self.name = whichEnemy
        self.id = id

        self.agent = givenAgent
        self.SHOWTANGENT = False

        self.collision = self.__getCollision()
        self.SHOWHITBOX = True

        self.speed = self.game.enemyData[self.name]["speed"]
        self.size = self.game.enemyData[self.name]["size"]
        self.contains = self.game.enemyData[self.name]["contains"]
        self.health = self.game.enemyData[self.name]["health"]

        self.POPPED = False
        self.NEWBALLOONAMOUNT = 0
        self.KILLINGBLOWPROJECTILE = None

        self.image = pygame.transform.scale(self.game.enemyImages[self.name], (self.size[0], self.size[1]))

    def update(self, delta_time):
        self.agent.update(delta_time, self.speed)
        pos = self.agent.getPos()
        self.collision.pos.update(pos.x, pos.y - 3)

    def draw(self, canvas):
        pos = self.agent.getPos()
        pos.x -= self.image.get_width()/2
        pos.y -= self.image.get_height()/2 
        canvas.blit(self.image, (pos.x, pos.y))
        if self.SHOWTANGENT:
            self.agent.draw(canvas)
        if self.SHOWHITBOX:
            pygame.draw.circle(
                canvas,
                (255,0,0),
                self.collision.pos,
                self.collision.radius,
                2
            )

    def __getCollision(self):
        size = self.game.enemyData[self.name]["size"]
        pos = self.agent.getPos()
        tempCircle = Circle(pygame.Vector2(pos.x, pos.y-3), size[0] - size[0]/1.5 + 5)
        return tempCircle

    def checkCollision(self, pos):
        if isCollidePointVsCircle(pos, self.collision):
            return True
        return False

    def takeDamage(self, damage, projectileHitList):
        newBalloonsAmount = 0
        updatedHealth = self.health - damage

        if(updatedHealth < 0):
             updatedHealth = 0

        if(updatedHealth > 0):
            newBalloonsAmount = 1
            while(self.health > updatedHealth):
                for newBalloon in self.contains:
                    newBalloonsAmount *= self.contains[newBalloon]
                self.health -= 1

        self.NEWBALLOONAMOUNT = newBalloonsAmount   
        self.KILLINGBLOWPROJECTILE = projectileHitList
        self.POPPED = True 
      
    def spawn(self, addEnemy):
        if(self.health > 0):
            newEnemy = None

            for enemy in self.game.enemyData:
                if self.game.enemyData[enemy]["health"] == self.health:
                    newEnemy = enemy
                    break
            for i in range(self.NEWBALLOONAMOUNT):
                newEnemyId = addEnemy(newEnemy, self.agent.fMarker, (i*-1))
                self.KILLINGBLOWPROJECTILE.append(newEnemyId)
    
