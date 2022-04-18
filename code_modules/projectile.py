import pygame, os, json
from code_modules.quad_tree.quadtree import QuadTree
from code_modules.quad_tree.quad_rectangle import QuadRectangle
from code_modules.quad_tree.quad_circle import QuadCircle
from settings import *
from code_modules.collision_functions import Circle
from code_modules.enemy import Enemy


class Projectile:
    def __init__(self, type, game, quad_tree):
        self.game = game
        self.quad_tree = quad_tree

        # BASE INFO
        self.type = type

        # SETTINGS
        self.DEBUG = True
        self.REACHED_MAX_DISTANCE = False
        self.DEPLETED = False

        # TRAVEL
        self.fire_point = pygame.Vector2
        self.target = pygame.Vector2
        self.pos = pygame.Vector2
        self.direction = pygame.Vector2
        self.travel_procent = 0  # Number between 0 and 1, represents where along the travel line the projectile is

        # PROJECTILE DATA
        self.speed = self.game.PROJECTILE_DATA[self.type]["speed"]
        self.damage = self.game.PROJECTILE_DATA[self.type]["damage"]
        self.pierce = self.game.PROJECTILE_DATA[self.type]["pierce"]
        self.max_distance = self.game.PROJECTILE_DATA[self.type]["max-distance"]
        self.aoe = self.game.PROJECTILE_DATA[self.type]["aoe-radius"]
        self.size = self.game.PROJECTILE_DATA[self.type]["size"]

        # GRAPHICS
        self.image = pygame.transform.scale(
            self.game.PROJECTILE_IMAGES[self.type],
            (self.size[0], self.size[1])
        )
        self.image_angle = 0

        # OTHER
        self.calculated_target_pos = pygame.Vector2
        self.collision = None
        self.hit_balloons = []

    def update(self, deltaTime, actions):
        if self.travel_procent == 1:
            self.REACHED_MAX_DISTANCE = True
            self.collision = None
        else:
            self.collision = self.__get_collision()

            #########################
            tempPosBefore = pygame.Vector2.lerp(self.fire_point, self.calculated_target_pos, self.travel_procent)
            self.travel_procent += self.speed * deltaTime
            if self.travel_procent > 1:
                self.travel_procent = 1
            tempPosAfter = pygame.Vector2.lerp(self.fire_point, self.calculated_target_pos, self.travel_procent)
            #
            #### LINEAR INTERPOLATION NEEDED TO CALC IF COLLIDED DURING TRAVLE ###
            #
            #
            #
            #######################################################################
                    
            self.pos = tempPosAfter
            query_range = QuadCircle(self.collision.pos.x, self.collision.pos.y, self.collision.radius)
            balloons_collided = self.quad_tree.query(query_range)

            if len(balloons_collided) > 0:
                self.__do_damage_to_balloons()

    def render(self, canvas):
        ### THE BULLET ###
        rotatedImage = pygame.transform.rotate(self.image, self.image_angle)
        canvas.blit(rotatedImage,(self.pos.x - rotatedImage.get_width()/2,
                                self.pos.y - rotatedImage.get_height()/2)
        )

        if self.DEBUG:
            ### COLLISION RADIUS ###
            pygame.draw.circle(canvas, (0,0,0), self.collision.pos, self.collision.radius, 1)
        
            ### AOE RADIUS ###
            pygame.draw.circle(canvas, (170,0,0), self.collision.pos, self.aoe, 1)
        
            ### PROJECTILE PATH ###
            pygame.draw.line(canvas, (255,0,0), self.fire_point, self.calculated_target_pos, 2)

            ### MAX TRAVLE DISTANCE ###
            pygame.draw.circle(canvas, (255,0,255), self.calculated_target_pos, 10)

    def shoot(self, target, start_pos, angle, aim_offset):
        # Fetch target position
        self.target = target.agent.get_pos(aim_offset)
        # Set fire_point and self position to given start position
        self.fire_point = start_pos
        self.pos = start_pos

        # Calculate the direction by subtracting the vectors
        direction = self.fire_point - self.target
        direction = direction.normalize()

        # Calculate target position by normalizing the direction and increasing the length to self max distance.
        self.calculated_target_pos = (pygame.Vector2(self.fire_point)
                                - direction * (self.max_distance))
      
        # Update the image angle
        self.image_angle = angle

    def __do_damage_to_balloons(self):
        query_range = QuadCircle(self.collision.pos.x, self.collision.pos.y, self.aoe)
        balloons_in_AOE = self.quad_tree.query(query_range)
        for point in balloons_in_AOE:
            hit_balloon = False
            balloon = point.userData

            # If ballon in AOE has not already been hit, damage it and add it to list of hit balloons.
            if(balloon.id not in self.hit_balloons):
                balloon.take_damage(self.damage, self.hit_balloons)
                hit_balloon = True
                self.hit_balloons.append(balloon.id)
        
        # Decrease pierce
        if hit_balloon:
            if self.pierce >= 0:
                self.pierce -= 1

        # If pierce has run out, its depleted and shall be removed.
        if self.pierce < 0:
            self.DEPLETED = True
    
    def __get_collision(self):
        return Circle(
            pygame.Vector2(self.pos),
            self.game.PROJECTILE_DATA[self.type]["collision-radius"]
            )
        

    
