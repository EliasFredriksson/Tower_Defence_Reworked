import pygame, json
from settings import *
from code_modules.collision_functions import *

########### TOWER DATA ###########
towerData = json.load(open(os.path.join(ROOT_DIR, "assets/Towers/tower-data.json")))    
towerImages = {}
for tower in towerData:
    filePath = "assets/Towers/Images/" + towerData[tower]["image"]
    loadedImg = pygame.image.load(os.path.join(ROOT_DIR, filePath)).convert_alpha()
    towerImages[tower] = loadedImg
filePath = "assets/Towers/Images/Tower.png"
towerImages["base"] = loadedImg = pygame.image.load(os.path.join(ROOT_DIR, filePath)).convert_alpha()
##################################

########### TOWER MENU ###########
filePath = "assets/Tower-Border.png"
menuBorder = pygame.image.load(os.path.join(ROOT_DIR, filePath)).convert_alpha()

filePath = "assets/Tower-Background.png"
menuBackground = pygame.image.load(os.path.join(ROOT_DIR, filePath)).convert_alpha()

filePath = "assets/Menu-Item-Background.png"
menuItemBackground = pygame.image.load(os.path.join(ROOT_DIR, filePath)).convert_alpha()
##################################

class MenuItem():
    def __init__(self, whichTower):
        self.name = whichTower
        self.pos = pygame.Vector2(0,0)
        self.towerSize = towerData[whichTower]["towerSize"]
        self.baseSize = towerData[whichTower]["baseSize"]
        self.cost = towerData[whichTower]["cost"]

    def setPos(self, pos):
        self.pos.update(pos)
        ### UPDATE RECT ###
        self.rect = pygame.Rect(
            self.pos.x,
            self.pos.y,
            TOWERMENU_ITEM_WIDTH,
            TOWERMENU_ITEM_HEIGHT
            ) 
        
        ### BUTTON BACKGROUND ###
        self.background = pygame.transform.scale(
            menuItemBackground,
            (TOWERMENU_ITEM_WIDTH, TOWERMENU_ITEM_HEIGHT)
        )

        ### TOWER BASE ###
        self.towerBaseImage = pygame.transform.scale(
            towerImages.get("base"), 
            (
                int(towerImages.get("base").get_width() * self.baseSize), 
                int(towerImages.get("base").get_height() * self.baseSize)
            )
        )
        self.towerBaseImagePos = pygame.Vector2(
            (self.pos.x + (TOWERMENU_ITEM_WIDTH / 2) - 
                self.towerBaseImage.get_width() / 2),
            (self.pos.y + TOWERMENU_ITEM_HEIGHT / 2 -
                self.towerBaseImage.get_height() / 2)
        )

        ### TOWER ###
        self.towerImage = pygame.transform.scale(
            towerImages.get(self.name), 
            (
                int(towerImages.get(self.name).get_width() * self.towerSize), 
                int(towerImages.get(self.name).get_height() * self.towerSize)
            )
        )
        self.towerImagePos = pygame.Vector2(
            (self.pos.x + (TOWERMENU_ITEM_WIDTH / 2) - 
                self.towerImage.get_width() / 2),
            (self.pos.y + TOWERMENU_ITEM_HEIGHT / 2 -
                self.towerImage.get_height() / 2)
        )


class TowerMenu():
    def __init__(self):
        self.pos = pygame.Vector2(800,0)
        self.rect = pygame.Rect(
            self.pos.x,
            self.pos.y,
            menuBackground.get_width(),
            menuBackground.get_height()
            )

        self.towerNameFont = pygame.font.Font(FONTFILE, 36)
        self.costFont = pygame.font.Font(FONTFILE, 16)

        self.towerNamePos = pygame.Vector2(self.pos.x + 100, self.pos.y + 30)
        self.nameOfSelectedTower = "Cannon"

        self.costPos = pygame.Vector2(self.pos.x + 100, self.pos.y + 55)
        self.costOfSelectedTower = 10000

        self.menuItems = self.__getMenuItems()
        self.activeItem = None

    def draw(self, canvas):
        canvas.blit(menuBackground, self.pos)

        for towerItem in self.menuItems:
            canvas.blit(towerItem.background, towerItem.pos)
            canvas.blit(towerItem.towerBaseImage, towerItem.towerBaseImagePos)
            canvas.blit(towerItem.towerImage, towerItem.towerImagePos)


        ### COST TEXT ###
        if self.costOfSelectedTower != 0:
            tempTextOfSelectedTowerCost =  self.costFont.render("Cost: " + str(self.costOfSelectedTower), True, (255,255,255))
            t_size = self.costFont.size("Cost: " + str(self.costOfSelectedTower))
            canvas.blit(tempTextOfSelectedTowerCost, (self.costPos.x - t_size[0]/2, self.costPos.y - t_size[1]/2))

        ### NAME TEXT ###
        if self.nameOfSelectedTower != "":
            tempTextOfSelectedTowerName =  self.towerNameFont.render(str(self.nameOfSelectedTower), True, (255,255,255))
            t_size = self.towerNameFont.size(str(self.nameOfSelectedTower))
            canvas.blit(tempTextOfSelectedTowerName, (self.towerNamePos.x - t_size[0]/2, self.towerNamePos.y - t_size[1]/2))


        canvas.blit(menuBorder, self.pos)

    def update(self):
        pass
        

    def __getMenuItems(self):
        menuItems = []
        x = 0
        y = 0
        for tower in towerData:
            menuItem = MenuItem(tower)
            menuItem.setPos(
                (self.pos.x + 12 + ((15 * x) % 30) + TOWERMENU_ITEM_WIDTH * x,
                self.pos.y + 80 + ((10 * y) % 20) + TOWERMENU_ITEM_HEIGHT * y)
                )
            menuItems.append(menuItem)
            x += 1
            x = x % 2
            if x % 2 == 0:
                y += 1
        return menuItems

    def mouseMovement(self, mousePos):
        for i in range(len(self.menuItems)):
            if isCollidePointVsRect(pygame.Vector2(mousePos), self.menuItems[i].rect):
                self.activeItem = i
        if self.activeItem != None:
            self.nameOfSelectedTower = self.menuItems[self.activeItem].name
            self.costOfSelectedTower = self.menuItems[self.activeItem].cost
        