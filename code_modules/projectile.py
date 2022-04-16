import pygame, os, json
from code_modules.quad_tree.quadtree import QuadTree
from code_modules.quad_tree.quad_rectangle import QuadRectangle
from code_modules.quad_tree.quad_circle import QuadCircle
from settings import *
from code_modules.collision_functions import Circle
from code_modules.enemy import Enemy
from code_modules.pointer_list import PointerElement


class Projectile:
    def __init__(self, type, game):
        self.game = game
        self.type = type
        self.DEBUG = True

        self.firePoint = pygame.Vector2
        self.target = pygame.Vector2

        self.pos = pygame.Vector2
        self.direction = pygame.Vector2

        self.speed = self.game.projectileData[self.type]["speed"]
        self.damage = self.game.projectileData[self.type]["damage"]
        self.pierce = self.game.projectileData[self.type]["pierce"]
        self.maxDistance = self.game.projectileData[self.type]["max-distance"]
        self.aoe = self.game.projectileData[self.type]["aoe-radius"]

        self.size = self.game.projectileData[self.type]["size"]
        self.image = pygame.transform.scale(
            self.game.projectileImages[self.type],
            (self.size[0], self.size[1])
        )
        self.imageAngle = 0


        self.t = 0
        self.REACHEDMAXDISTANCE = False
        self.calculatedTarget = pygame.Vector2

        self.collision = None

        self.DEPLETED = False

        self.hitBalloons = []

    

    def update(self, deltaTime, ballonQuadTree: QuadTree):
        if self.t == 1:
            self.REACHEDMAXDISTANCE = True
            self.collision = None
        else:
            self.collision = self.__getCollision()

            #########################
            tempPosBefore = pygame.Vector2.lerp(self.firePoint, self.calculatedTarget, self.t)
            self.t += self.speed * deltaTime
            if self.t > 1:
                self.t = 1
            tempPosAfter = pygame.Vector2.lerp(self.firePoint, self.calculatedTarget, self.t)

            #### LINEAR INTERPOLATION NEEDED TO CALC IF COLLIDED DURING TRAVLE ###
                    
            self.pos = tempPosAfter
            queryRange = QuadCircle(self.collision.pos.x, self.collision.pos.y, self.collision.radius)
            balloonsCollided = ballonQuadTree.query(queryRange)

            if len(balloonsCollided) > 0:
                self.__doDamageToBalloons(ballonQuadTree)
                

    def draw(self, canvas):
        ### THE BULLET ###
        rotatedImage = pygame.transform.rotate(self.image, self.imageAngle)
        canvas.blit(rotatedImage,(self.pos.x - rotatedImage.get_width()/2,
                                self.pos.y - rotatedImage.get_height()/2)
        )

        if self.DEBUG:
            ### COLLISION RADIUS ###
            pygame.draw.circle(canvas, (0,0,0), self.collision.pos, self.collision.radius, 1)
        
            ### AOE RADIUS ###
            pygame.draw.circle(canvas, (170,0,0), self.collision.pos, self.aoe, 1)
        
            ### PROJECTILE PATH ###
            pygame.draw.line(canvas, (255,0,0), self.firePoint, self.calculatedTarget, 2)

            ### MAX TRAVLE DISTANCE ###
            pygame.draw.circle(canvas, (255,0,255), self.calculatedTarget, 10)

    def shoot(self, target, pos, angle, aim_offset):
        self.target = target.agent.getPos(aim_offset)
        self.firePoint = pos
        self.pos = pos

        direction = self.firePoint - self.target
        direction = direction.normalize()

        self.calculatedTarget = (pygame.Vector2(self.firePoint)
                                - direction * (self.maxDistance))
      
        self.imageAngle = angle

    def __doDamageToBalloons(self, ballonQuadTree):
        queryRange = QuadCircle(self.collision.pos.x, self.collision.pos.y, self.aoe)
        balloonsInAOE = ballonQuadTree.query(queryRange)
        #print("IN AOE",balloonsInAOE)
        hitBalloon = False
        for point in balloonsInAOE:
            balloon = point.userData

            if(balloon.id not in self.hitBalloons):
                balloon.takeDamage(self.damage, self.hitBalloons)
                hitBalloon = True
                self.hitBalloons.append(balloon.id)
            ### PSEUDO CODE ###
            # ballon.damage(self.damage) ->
            # ballon.spawn() -> spawn balloons according to the damage taken
        if hitBalloon:
            if self.pierce >= 0:
                self.pierce -= 1

        if self.pierce < 0:
            self.DEPLETED = True
    
    def __getCollision(self):
        return Circle(
            pygame.Vector2(self.pos),
            self.game.projectileData[self.type]["collision-radius"]
            )

    # def __isCollideWithBalloon(self, pos: pygame.Vector2, velocity: pygame.Vector2, balloon):
    #     start = pos
    #     end = pos + velocity

    #     insideBefore = isCollidePointVsCircle(start, balloon.collision)
    #     insideAfter = isCollidePointVsCircle(end, balloon.collision)

    #     if insideAfter or insideBefore:
    #         return False
        
    #     lenSquared = getDistanceSquaredPointVsPoint(start, end)
        
    #     bPos = balloon.agent.getPos()

    #     dot = (((bPos.x - start.x) * (end.x - start.x)) + ((bPos.y - start.y)*(end.y - start.y))) / lenSquared

    #     closestX = start.x + (dot * (end.x - start.x))
    #     closestY = start.y + (dot * (end.y - start.y))

    #     pygame.draw.circle(canvas, (0,0,255), (closestX, closestY), 10)

    #     onSegment = isCollidePointVsLine(start, end, pygame.Vector2(closestX, closestY))
    #     if not onSegment:
    #         return False

    #     closestCircle = Circle(pygame.Vector2(closestX, closestY), self.collision.radius)

    #     if isCollideCircleVsCircle(closestCircle, balloon.collision):
    #         return True
    #     return False

        

    
