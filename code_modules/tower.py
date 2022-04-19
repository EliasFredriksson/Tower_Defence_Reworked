import pygame, math
from settings import *
from enum import Enum
from code_modules.collision_functions import * 
from code_modules.linked_list import LinkedList


############################
class Target(Enum):
    FIRST = 0
    LAST = 1
    STRONG = 2
    CLOSE = 3



class Tower():
    def __init__(self, name, game, projectile_func):
        self.game = game
        self.projectile_func = projectile_func

        # BASE INFO
        self.name = name
        self.pos = pygame.Vector2(-600,-600)
        self.angle = 0

        # SETTINGS
        self.SHOWHITBOX = False             # If show tower hitbox
        self.SHOWRANGE = False              # If show range
        self.SELECTED = False               # If show info about tower
        self.PLACED = False                 # If you can move it around
        self.SOLD = False                   # If you have sold the tower
        self.AIM_OFFSET = 0.05              # Aim offset
        self.prefferedTarget = Target.FIRST # Prefered target

        # TOWER DATA
        self.towerSize = self.game.TOWER_DATA[self.name]["towerSize"]
        self.baseSize = self.game.TOWER_DATA[self.name]["baseSize"]
        self.range = Circle(self.pos, self.game.TOWER_DATA[self.name]["range"])
        self.attack_type = self.game.TOWER_DATA[self.name]["projectile"]
        self.attack_projectile_speed = self.game.PROJECTILE_DATA[self.attack_type]["speed"]
        self.fireRate = self.game.TOWER_DATA[self.name]["firerate"]

        # GRAPHICS
        self.image = pygame.transform.rotozoom(self.game.TOWER_IMAGES[self.name], 0, self.towerSize)
        self.base = pygame.transform.rotozoom(self.game.TOWER_BASE_IMAGE, 0, self.baseSize)
        self.rangeImg = pygame.transform.scale(self.game.TOWER_RANGE_IMAGE, (self.range.radius * 2 + 5, self.range.radius * 2 + 5))


        # OTHER
        self.projectile_list = LinkedList()
        self.collision = Circle(self.pos, self.base.get_width() / 2)

        #self.projectilesStarterPointer = PointerElement()
        self.current_target = -1
        self.balloons_in_range = []
        self.fire_rate_counter = 0

     


    def update(self, delta_time, actions):
        if self.PLACED:
            self.current_target = self.__get_targeted_balloon()
            self.__try_to_attack(delta_time)
        else:
            if actions["MOUSE_RIGHT"]:
                self.PLACED = True
                self.SHOWRANGE = False
            self.pos.update(actions["MOUSE_POS"])
            self.SHOWRANGE = True       

    def render(self, canvas):
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

        ### DRAW HITBOX ###
        if self.SHOWHITBOX:
            pygame.draw.circle(
                canvas,
                (255,0,255),
                self.collision.pos,
                self.collision.radius,
                2
            )       

    def __try_to_attack(self, deltaTime):
        if self.current_target != -1:
            if self.fire_rate_counter < 0:
                # Turn towards targeted balloon
                self.__turn_to_target(self.current_target)
                
                # Reset the firerate counter
                self.fire_rate_counter = self.fireRate
                
                # Run given projectile function which creates and shoots specified projectile
                self.projectile_func(self.attack_type, self.current_target, self.pos, self.angle, self.AIM_OFFSET)
            else:
                self.fire_rate_counter -= 1 * deltaTime
        else:
            if self.fire_rate_counter > 0:
                self.fire_rate_counter -= 1 * deltaTime
    

    ### ROTATION ###
    def __get_targeted_balloon(self):
        ### PREPARE NUMBER FOR FILTER ###
        target_balloon = -1
        target_filter = 0
        strong_first_filer = 0
        
        if self.prefferedTarget == Target.FIRST or self.prefferedTarget == Target.STRONG:
            target_filter = 0
        if self.prefferedTarget == Target.LAST or self.prefferedTarget == Target.CLOSE:
            target_filter = math.inf

        ### PICK PREFFERED BALLOON FROM BALLONS IN RANGE ###
        for balloon in self.balloons_in_range:
            ### FIRST ###
            if self.prefferedTarget == Target.FIRST:
                if balloon.agent.fMarker >= target_filter:
                    target_filter = balloon.agent.fMarker
                    target_balloon = balloon
            ### LAST ###
            if self.prefferedTarget == Target.LAST:
                if balloon.agent.fMarker <= target_filter:
                    target_filter = balloon.agent.fMarker
                    target_balloon = balloon

            ### STRONG ###
            if self.prefferedTarget == Target.STRONG:
                if balloon.agent.fMarker >= target_filter:
                    if balloon.value >= strong_first_filer:
                        strong_first_filer = balloon.value
                        target_filter = balloon.agent.fMarker
                        target_balloon = balloon
                        
            ### CLOSE ###
            if self.prefferedTarget == Target.CLOSE:
                tempDistance = getDistancePointVsPoint(self.pos, balloon.agent.getPos())
                if tempDistance <= target_filter:
                    target_filter = tempDistance
                    target_balloon = balloon

        ### RETURN BALLOON ###
        return target_balloon

    def __turn_to_target(self, target_balloon):
        radians = math.atan2(
                target_balloon.agent.get_pos(self.AIM_OFFSET).y - self.pos.y,
                target_balloon.agent.get_pos(self.AIM_OFFSET).x - self.pos.x
                )
        angle = -(radians * 180 / math.pi) - 90
        self.angle = angle
        self.current_target = target_balloon   

