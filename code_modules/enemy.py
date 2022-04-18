import pygame
from code_modules.spline.agent import Agent
from settings import *
from code_modules.collision_functions import Circle, isCollidePointVsCircle


class Enemy():
    def __init__(self, game, givenAgent: Agent, whichEnemy, id):
        # REFERENCE TO GAME
        self.game = game

        # BASE INFO
        self.name = whichEnemy
        self.id = id
        self.agent = givenAgent

        # BALLOON DATA
        self.speed = self.game.ENEMY_DATA[self.name]["speed"]
        self.size = self.game.ENEMY_DATA[self.name]["size"]
        self.contains = self.game.ENEMY_DATA[self.name]["contains"]
        self.health = self.game.ENEMY_DATA[self.name]["health"]
        self.image = pygame.transform.scale(self.game.ENEMY_IMAGES[self.name], (self.size[0], self.size[1]))
        self.collision = self.__get_collision()

        # SETTINGS
        self.SHOW_TANGENT = False
        self.POPPED = False
        self.SHOW_HITBOX = True
        self.HITBOX_OFFSET = pygame.Vector2(0,-3)

        # KILLING BLOW INFO
        self.killing_blow_projectile = None
        self.new_balloon_amount = 0


    def update(self, delta_time):
        self.agent.update(delta_time, self.speed)
        pos = self.agent.get_pos()
        self.collision.pos.update(pos.x + self.HITBOX_OFFSET.x, pos.y + self.HITBOX_OFFSET.y)

    def render(self, canvas):
        pos = self.agent.get_pos()
        pos.x -= self.image.get_width()/2
        pos.y -= self.image.get_height()/2 
        canvas.blit(self.image, (pos.x, pos.y))
        if self.SHOW_TANGENT:
            self.agent.render(canvas)
        if self.SHOW_HITBOX:
            pygame.draw.circle(
                canvas,
                (255,0,0),
                self.collision.pos,
                self.collision.radius,
                2
            )

    def __get_collision(self):
        pos = self.agent.get_pos()
        tempCircle = Circle(pygame.Vector2(pos.x, pos.y-3), self.size[0] - self.size[0]/1.5 + 5)
        return tempCircle

    def check_collision(self, pos):
        if isCollidePointVsCircle(pos, self.collision):
            return True
        return False

    def take_damage(self, damage, projectileHitList):
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

        self.new_balloon_amount = newBalloonsAmount   
        self.killing_blow_projectile = projectileHitList
        self.POPPED = True 
      
    def spawn(self, add_enemy):
        if(self.health > 0):
            newEnemy = None
            for enemy in self.game.ENEMY_DATA:
                if self.game.ENEMY_DATA[enemy]["health"] == self.health:
                    newEnemy = enemy
                    break
            for i in range(self.new_balloon_amount):
                newEnemyId = add_enemy(newEnemy, self.agent.fMarker, (i*-1))
                self.killing_blow_projectile.append(newEnemyId)
    
