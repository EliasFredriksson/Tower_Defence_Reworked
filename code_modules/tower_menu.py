import pygame
from settings import *
from code_modules.collision_functions import isCollidePointVsRect


class MenuItem():
    def __init__(self, game, whichTower):
        self.game = game
        self.pos = pygame.Vector2(0,0)
        self.NAME = whichTower
        self.TOWER_SIZE = self.game.TOWER_DATA[whichTower]["towerSize"]
        self.BASE_SIZE = self.game.TOWER_DATA[whichTower]["baseSize"]
        self.COST = self.game.TOWER_DATA[whichTower]["cost"]
        self.SIZE = int((self.game.TOWER_MENU_BACKGROUND.get_width() / 2) - 10) 

    def set_pos(self, pos):
        self.pos.update(pos)
        ### UPDATE RECT ###
        self.rect = pygame.Rect(
            self.pos.x,
            self.pos.y,
            self.SIZE,
            self.SIZE
            ) 
        
        ### BUTTON BACKGROUND ###
        self.background = pygame.transform.scale(
            self.game.TOWER_MENU_ITEM_BACKGROUND,
            (self.SIZE , self.SIZE)
        )

        ### TOWER BASE ###
        self.towerBaseImage = pygame.transform.scale(
            self.game.TOWER_BASE_IMAGE,
            (
                int(self.game.TOWER_BASE_IMAGE.get_width() * self.BASE_SIZE), 
                int(self.game.TOWER_BASE_IMAGE.get_height() * self.BASE_SIZE)
            )
        )
        self.towerBaseImagePos = pygame.Vector2(
            (self.pos.x + (self.SIZE/2) - self.towerBaseImage.get_width() / 2),
            (self.pos.y + (self.SIZE/2) - self.towerBaseImage.get_height() / 2)
        )

        ### TOWER ###
        self.towerImage = pygame.transform.scale(
            self.game.TOWER_IMAGES.get(self.NAME), 
            (
                int(self.game.TOWER_IMAGES.get(self.NAME).get_width() * self.TOWER_SIZE), 
                int(self.game.TOWER_IMAGES.get(self.NAME).get_height() * self.TOWER_SIZE)
            )
        )
        self.towerImagePos = pygame.Vector2(
            (self.pos.x + (self.SIZE/2) - self.towerImage.get_width() / 2),
            (self.pos.y + (self.SIZE/2) - self.towerImage.get_height() / 2)
        )


class TowerMenu():
    def __init__(self, game, add_tower_function):
        self.game = game
        self.add_tower_function = add_tower_function
        self.pos = pygame.Vector2(800,0)
        self.rect = pygame.Rect(
            self.pos.x,
            self.pos.y,
            self.game.TOWER_MENU_BACKGROUND.get_width(),
            self.game.TOWER_MENU_BACKGROUND.get_height()
            )

        self.TOWER_NAME_FONT_SIZE = 16
        self.COST_FONT_SIZE = 8
        self.TOWER_NAME_FONT = pygame.font.Font(self.game.FONT_PATH, self.TOWER_NAME_FONT_SIZE)
        self.COST_FONT = pygame.font.Font(self.game.FONT_PATH, self.COST_FONT_SIZE)

        self.towerNamePos = pygame.Vector2(self.pos.x + 100, self.pos.y + 30)
        self.name_of_selected_tower = "Towers"

        self.costPos = pygame.Vector2(self.pos.x + 100, self.pos.y + 55)
        self.cost_of_selected_tower = 0

        self.menu_items = self.__get_menu_items()
        self.active_item = None

        self.pressed = False

    def update(self, delta_time, actions):
        mouse_pos = actions["MOUSE_POS"]
        for i in range(len(self.menu_items)):
            if not self.pressed and actions["MOUSE_LEFT"] and isCollidePointVsRect(mouse_pos, self.menu_items[i].rect) :
                self.active_item = i
                self.pressed = True
                self.add_tower_function(self.menu_items[i].NAME)

        if self.active_item != None:
            self.name_of_selected_tower = self.menu_items[self.active_item].NAME
            self.cost_of_selected_tower = self.menu_items[self.active_item].COST

        if self.pressed:
            if not actions["MOUSE_LEFT"]:
                self.pressed = False


    def render(self, canvas):
        canvas.blit(self.game.TOWER_MENU_BACKGROUND, self.pos)

        for tower_item in self.menu_items:
            canvas.blit(tower_item.background, tower_item.pos)
            canvas.blit(tower_item.towerBaseImage, tower_item.towerBaseImagePos)
            canvas.blit(tower_item.towerImage, tower_item.towerImagePos)

            pygame.draw.rect(canvas, (255,0,0), tower_item.rect, 2)


        ### COST TEXT ###
        if self.cost_of_selected_tower != 0:
            tempTextOfSelectedTowerCost =  self.COST_FONT.render("Cost: " + str(self.cost_of_selected_tower), True, (255,255,255))
            t_size = self.COST_FONT.size("Cost: " + str(self.cost_of_selected_tower))
            canvas.blit(tempTextOfSelectedTowerCost, (self.costPos.x - t_size[0]/2, self.costPos.y - t_size[1]/2))

        ### NAME TEXT ###
        if self.name_of_selected_tower != "":
            tempTextOfSelectedTowerName =  self.TOWER_NAME_FONT.render(str(self.name_of_selected_tower), True, (255,255,255))
            t_size = self.TOWER_NAME_FONT.size(str(self.name_of_selected_tower))
            canvas.blit(tempTextOfSelectedTowerName, (self.towerNamePos.x - t_size[0]/2, self.towerNamePos.y - t_size[1]/2))


        canvas.blit(self.game.TOWER_MENU_BORDER, self.pos)
    
       
    def __get_menu_items(self):
        menuItems = []
        x = 0
        y = 0
        for tower in self.game.TOWER_DATA:
            menuItem = MenuItem(self.game, tower)
            menuItem.set_pos(
                (self.pos.x + 12 + ((15 * x) % 30) + TOWERMENU_ITEM_WIDTH * x,
                self.pos.y + 80 + ((10 * y) % 20) + TOWERMENU_ITEM_HEIGHT * y)
                )
            menuItems.append(menuItem)
            x += 1
            x = x % 2
            if x % 2 == 0:
                y += 1
        return menuItems

    # def mouseMovement(self, mousePos):
    #     for i in range(len(self.menu_items)):
    #         if isCollidePointVsRect(pygame.Vector2(mousePos), self.menu_items[i].rect):
    #             self.active_item = i
    #     if self.active_item != None:
    #         self.name_of_selected_tower = self.menu_items[self.active_item].NAME
    #         self.cost_of_selected_tower = self.menu_items[self.active_item].COST
        