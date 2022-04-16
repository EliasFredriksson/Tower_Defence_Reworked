from enum import Enum
import pygame, os, time, json
from settings import *
from constants import MODE
from states.title_screen import Title_Screen

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_NAME)
        self.monitor_info = pygame.display.Info()
        self.SCREEN_WIDTH = int(self.monitor_info.current_w * WINDOW_SIZE_START_SCALE)
        self.SCREEN_HEIGHT = int(self.monitor_info.current_h * WINDOW_SIZE_START_SCALE)
        self.GAME_WIDTH = GAME_WIDTH
        self.GAME_HEIGHT = GAME_HEIGHT
        self.main_canvas = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.window = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.DOUBLEBUF)

        self.running = True
        self.playing = True
        self.mode = MODE.PLAY

        self.delta_time = 0
        self.prev_time = 0

        self.state_stack = []
        self.load_assets()
        self.load_states()

        self.actions = {
            "UP": False,
            "DOWN": False,
            "LEFT": False,
            "RIGHT": False,
            "ACTION_1": False,
            "ACTION_2": False,
            "ACTION_3": False,
            "ACTION_4": False,
            "ACTION_5": False,
            "START": False,
            "BACK": False,
            "MOUSE_LEFT": False,
            "MOUSE_RIGHT": False,
            "MOUSE_POS": None
        }

    def game_loop(self):
        ### Core game loop ###
        while self.playing:
            self.get_delta_time()
            self.get_events()
            self.update()
            self.render()
 
    def get_events(self):
        ### EVENT HANDLER that updates self.actions ###
         for event in pygame.event.get():
            ##### QUIT EVENT #####
            if event.type == pygame.QUIT:
                self.running = False
                self.playing = False
            ##### KEYDOWN EVENT #####
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.playing = False
                if event.key == pygame.K_F1:
                    self.switch_mode()
                if event.key == pygame.K_UP:
                    self.actions["UP"] = True
                if event.key == pygame.K_DOWN:
                    self.actions["DOWN"] = True
                if event.key == pygame.K_LEFT:
                    self.actions["LEFT"] = True
                if event.key == pygame.K_RIGHT:
                    self.actions["RIGHT"] = True

                if event.key == pygame.K_BACKSPACE:
                    self.actions["BACK"] = True
                if event.key == pygame.K_RETURN:
                    self.actions["START"] = True
                
                if event.key == pygame.K_1:
                    self.actions["ACTION_1"] = True
                if event.key == pygame.K_2:
                    self.actions["ACTION_2"] = True
                if event.key == pygame.K_3:
                    self.actions["ACTION_3"] = True
                if event.key == pygame.K_4:
                    self.actions["ACTION_4"] = True
                if event.key == pygame.K_5:
                    self.actions["ACTION_5"] = True

            ##### KEYUP EVENT #####
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.actions["UP"] = False
                if event.key == pygame.K_DOWN:
                    self.actions["DOWN"] = False
                if event.key == pygame.K_LEFT:
                    self.actions["LEFT"] = False
                if event.key == pygame.K_RIGHT:
                    self.actions["RIGHT"] = False

                if event.key == pygame.K_BACKSPACE:
                    self.actions["BACK"] = False
                if event.key == pygame.K_RETURN:
                    self.actions["START"] = False
                
                if event.key == pygame.K_1:
                    self.actions["ACTION_1"] = False
                if event.key == pygame.K_2:
                    self.actions["ACTION_2"] = False
                if event.key == pygame.K_3:
                    self.actions["ACTION_3"] = False
                if event.key == pygame.K_4:
                    self.actions["ACTION_4"] = False
                if event.key == pygame.K_5:
                    self.actions["ACTION_5"] = False             

            ##### MOUSE MOTION EVENT #####
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                self.actions["MOUSE_POS"] = pygame.Vector2(mouse_pos[0], mouse_pos[1])
            
            ##### MOUSE BUTTON DOWN #####
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.actions["MOUSE_LEFT"] = True
                if event.button == 3:
                    self.actions["MOUSE_RIGHT"] = True

            ##### MOUSE BUTTON UP #####
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.actions["MOUSE_LEFT"] = False
                if event.button == 3:
                    self.actions["MOUSE_RIGHT"] = False

    def update(self):
        ### Update whats on top of the state stack ###
        self.state_stack[-1].update(self.delta_time, self.actions)
      
    def render(self):
        ### Render whats on top of the state stack ###
        self.state_stack[-1].render(self.main_canvas)
        self.window.blit(
            pygame.transform.scale(
                self.main_canvas, 
                (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
                ) , (0,0)
            )
        pygame.display.flip()

    def get_delta_time(self):
        ### DELTA TIME ###
        now_time = time.time()
        self.delta_time = now_time - self.prev_time
        self.prev_time = now_time

    def draw_text(self, surface, text, color, x, y):
        ### Helper function to draw text ###
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        surface.blit(text_surface, text_rect)

    def load_assets(self):
        ### Load all assets folders and fonts ###
        # FOLDERS
        self.assets_dir = os.path.join(ROOT_DIR, "assets")
        self.sprites_dir = os.path.join(self.assets_dir, "sprites")
        self.sounds_dir = os.path.join(self.assets_dir, "sound")
        self.levels_dir = os.path.join(self.assets_dir, "levels")
        self.fonts_dir = os.path.join(self.assets_dir, "fonts")

        # LEVELS
        self.levelData = json.load(open(os.path.join(self.sprites_dir, "levels/levels-data.json")))
        self.levelImages = {}
        for level in self.levelData:
            filePath = "levels/backgrounds/" + self.levelData[level]["background"]
            loadedImg = pygame.image.load(os.path.join(self.sprites_dir, filePath))
            self.levelImages[level] = loadedImg
        
        # BORDERS
        self.levelBorder = pygame.image.load(os.path.join(self.sprites_dir, "levels/Level-Border.png"))

        # FONTS
        self.font = pygame.font.Font(os.path.join(self.fonts_dir, "PressStart2P-vaV7.ttf"), 48)

        # ENEMIES
        self.enemyData = json.load(open(os.path.join(self.sprites_dir, "enemies/enemy-data.json")))
        self.enemyImages = {}
        for enemy in self.enemyData:
            filePath = "enemies/" + self.enemyData[enemy]["image"]
            loadedImg = pygame.image.load(os.path.join(self.sprites_dir, filePath)).convert_alpha()
            self.enemyImages[enemy] = loadedImg
        
        # PROJECTILES
        self.projectileData = json.load(open(os.path.join(self.sprites_dir, "projectiles/projectile-data.json")))   
        self.projectileImages = {}
        for projectile in self.projectileData:
            filePath = "projectiles/" + self.projectileData[projectile]["image"]
            loadedImg = pygame.image.load(os.path.join(self.sprites_dir, filePath)).convert_alpha()
            self.projectileImages[projectile] = loadedImg

        # TOWERS
        self.towerData = json.load(open(os.path.join(self.sprites_dir, "towers/tower-data.json")))
        self.towerImages = {}
        for tower in self.towerData:
            filePath = "towers/" + self.towerData[tower]["image"]
            loadedImg = pygame.image.load(os.path.join(self.sprites_dir, filePath)).convert_alpha()
            self.towerImages[tower] = loadedImg  

        filePath = "towers/Range-border.png"
        self.towerRangeImage = pygame.image.load(os.path.join(self.sprites_dir, filePath)).convert_alpha()

        filePath = "towers/Tower.png"
        self.towerBaseImage = pygame.image.load(os.path.join(self.sprites_dir, filePath)).convert_alpha()

    def load_states(self):
        ### Load all states and add title_screen state to stack ###
        self.title_screen = Title_Screen(self)
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        for action in self.actions:
            self.actions[action] = False

    def switch_mode(self):
        if self.mode == MODE.PLAY:
            self.mode = MODE.DEBUG
        else:
            self.mode = MODE.PLAY

if __name__ == "__main__":
    g = Game()
    while g.running:
        g.game_loop()