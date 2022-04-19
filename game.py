import pygame, os, time, json
from settings import *
from constants import MODE
from states.title_screen import Title_Screen

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_NAME)
        self.monitor_info = pygame.display.Info()

        ##### TEMPORARY #####
        # self.SCREEN_WIDTH = int(self.monitor_info.current_w * WINDOW_SIZE_START_SCALE)
        # self.SCREEN_HEIGHT = int(self.monitor_info.current_h * WINDOW_SIZE_START_SCALE)
        #
        # BUG
        # Hitboxes (rect) does not scale properly.
        self.SCREEN_WIDTH = GAME_WIDTH
        self.SCREEN_HEIGHT = GAME_HEIGHT
        #####################

        self.GAME_WIDTH = GAME_WIDTH
        self.GAME_HEIGHT = GAME_HEIGHT
        self.main_canvas = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.window = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.DOUBLEBUF)

        self.running = True

        self.delta_time = 0
        self.prev_time = 0

        self.state_stack = []
        self.load_assets()
        self.load_states()

        self.actions = {
            ### ACTIONS ###
            # Every action has a state and a _HELD state.
            # The base action acts as a "click" event. Turns true one frame, and next frame becomes false.
            # It cannot become true again until you have released the key.
            # The "_HELD" action is true as long as you hold the key down.
            ###############
            # ARROW KEYS
            "UP": False,
            "UP_HELD": False,
            "DOWN": False,
            "DOWN_HELD": False,
            "LEFT": False,
            "LEFT_HELD": False,
            "RIGHT": False,
            "RIGHT_HELD": False,
            # NUMBERS (1-5)
            "ACTION_1": False,
            "ACTION_1_HELD": False,
            "ACTION_2": False,
            "ACTION_2_HELD": False,
            "ACTION_3": False,
            "ACTION_3_HELD": False,
            "ACTION_4": False,
            "ACTION_4_HELD": False,
            "ACTION_5": False,
            "ACTION_5_HELD": False,
            # OTHER
            "START": False,
            "START_HELD": False,
            "BACK": False,
            "BACK_HELD": False,
            # MOUSE
            "MOUSE_LEFT": False,
            "MOUSE_LEFT_HELD": False,
            "MOUSE_RIGHT": False,
            "MOUSE_RIGHT_HELD": False,
            "MOUSE_POS": pygame.Vector2(0,0)
        }
        self.keys_to_reset = []

        ### FPS TIMER ###
        self.clock = pygame.time.Clock()

        ### MODE ###
        self.mode = MODE.PLAY
        ### DEBUG SETTINGS ###
        self.PRINT_INFO = True
        self.SHOW_INPUT = True
        self.SHOW_FPS = True


    def run(self):
        ### Core game loop ###
        while self.running:
            self.clock.tick_busy_loop(TARGET_FPS)
            self.get_delta_time()
            self.get_events()
            self.update()
            self.render()
            self.reset_keys()

 
    def get_events(self):
        ### EVENT HANDLER that updates self.actions ###
         for event in pygame.event.get():
            ##### QUIT EVENT #####
            if event.type == pygame.QUIT:
                self.running = False
            ##### KEYDOWN EVENT #####
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                ### TOGGLE DEBUG MODE ###
                if event.key == pygame.K_d and event.mod & pygame.KMOD_LCTRL:
                    self.switch_mode()

                if event.key == pygame.K_UP:
                    self.actions["UP_HELD"] = True
                    self.__action_click("UP")
                if event.key == pygame.K_DOWN:
                    self.actions["DOWN_HELD"] = True
                    self.__action_click("DOWN")
                if event.key == pygame.K_LEFT:
                    self.actions["LEFT_HELD"] = True
                    self.__action_click("LEFT")
                if event.key == pygame.K_RIGHT:
                    self.actions["RIGHT_HELD"] = True
                    self.__action_click("RIGHT")

                if event.key == pygame.K_BACKSPACE:
                    self.actions["BACK_HELD"] = True
                    self.__action_click("BACK")
                if event.key == pygame.K_RETURN:
                    self.actions["START_HELD"] = True
                    self.__action_click("START")
                
                if event.key == pygame.K_1:
                    self.actions["ACTION_1_HELD"] = True
                    self.__action_click("ACTION_1")
                if event.key == pygame.K_2:
                    self.actions["ACTION_2_HELD"] = True
                    self.__action_click("ACTION_2")
                if event.key == pygame.K_3:
                    self.actions["ACTION_3_HELD"] = True
                    self.__action_click("ACTION_3")
                if event.key == pygame.K_4:
                    self.actions["ACTION_4_HELD"] = True
                    self.__action_click("ACTION_4")
                if event.key == pygame.K_5:
                    self.actions["ACTION_5_HELD"] = True
                    self.__action_click("ACTION_5")

            ##### KEYUP EVENT #####
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.actions["UP_HELD"] = False
                if event.key == pygame.K_DOWN:
                    self.actions["DOWN_HELD"] = False
                if event.key == pygame.K_LEFT:
                    self.actions["LEFT_HELD"] = False
                if event.key == pygame.K_RIGHT:
                    self.actions["RIGHT_HELD"] = False

                if event.key == pygame.K_BACKSPACE:
                    self.actions["BACK_HELD"] = False
                if event.key == pygame.K_RETURN:
                    self.actions["START_HELD"] = False
                
                if event.key == pygame.K_1:
                    self.actions["ACTION_1_HELD"] = False
                if event.key == pygame.K_2:
                    self.actions["ACTION_2_HELD"] = False
                if event.key == pygame.K_3:
                    self.actions["ACTION_3_HELD"] = False
                if event.key == pygame.K_4:
                    self.actions["ACTION_4_HELD"] = False
                if event.key == pygame.K_5:
                    self.actions["ACTION_5_HELD"] = False             

            ##### MOUSE MOTION EVENT #####
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                self.actions["MOUSE_POS"] = pygame.Vector2(mouse_pos[0], mouse_pos[1])
                
            
            ##### MOUSE BUTTON DOWN #####
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.actions["MOUSE_LEFT_HELD"] = True
                    self.__action_click("MOUSE_LEFT")
                if event.button == 3:
                    self.actions["MOUSE_RIGHT_HELD"] = True
                    self.__action_click("MOUSE_RIGHT")

            ##### MOUSE BUTTON UP #####
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.actions["MOUSE_LEFT_HELD"] = False
                if event.button == 3:
                    self.actions["MOUSE_RIGHT_HELD"] = False

    def update(self):
        ### Update whats on top of the state stack ###
        self.state_stack[-1].update(self.delta_time, self.actions)
        ### PRINT INFO ###
        
        
        if self.mode == MODE.DEBUG:
            if self.PRINT_INFO:
                os.system('cls' if os.name=='nt' else 'clear')
                print("=========================")
                print("MODE: ", self.mode)
                print("FPS: ", self.clock.get_fps())
                print("=========================")
                print("======== ACTIONS ========")
                for action in self.actions:
                    print(action, ": ", self.actions[action])
                print("=========================")
      
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

    def load_assets(self):
        ### Load all assets folders and fonts ###
        # FOLDERS
        self.ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
        self.SPRITES_DIR = os.path.join(self.ASSETS_DIR, "sprites")
        self.SOUNDS_DIR = os.path.join(self.ASSETS_DIR, "sound")
        self.LEVELS_DIR = os.path.join(self.ASSETS_DIR, "levels")
        self.FONTS_DIR = os.path.join(self.ASSETS_DIR, "fonts")

        # LEVELS
        self.LEVEL_DATA = json.load(open(os.path.join(self.SPRITES_DIR, "levels/levels-data.json")))
        self.LEVEL_IMAGES = {}
        for level in self.LEVEL_DATA:
            filePath = "levels/backgrounds/" + self.LEVEL_DATA[level]["background"]
            loadedImg = pygame.image.load(os.path.join(self.SPRITES_DIR, filePath))
            self.LEVEL_IMAGES[level] = loadedImg
        
        # BORDERS
        self.LEVEL_BORDER = pygame.image.load(os.path.join(self.SPRITES_DIR, "levels/Level-Border.png"))

        # FONTS
        self.FONT = pygame.font.Font(os.path.join(self.FONTS_DIR, "PressStart2P-vaV7.ttf"), 48)
        self.FONT_PATH = os.path.join(self.FONTS_DIR, "PressStart2P-vaV7.ttf")

        # ENEMIES
        self.ENEMY_DATA = json.load(open(os.path.join(self.SPRITES_DIR, "enemies/enemy-data.json")))
        self.ENEMY_IMAGES = {}
        for enemy in self.ENEMY_DATA:
            filePath = "enemies/" + self.ENEMY_DATA[enemy]["image"]
            loadedImg = pygame.image.load(os.path.join(self.SPRITES_DIR, filePath)).convert_alpha()
            self.ENEMY_IMAGES[enemy] = loadedImg
        
        # PROJECTILES
        self.PROJECTILE_DATA = json.load(open(os.path.join(self.SPRITES_DIR, "projectiles/projectile-data.json")))   
        self.PROJECTILE_IMAGES = {}
        for projectile in self.PROJECTILE_DATA:
            filePath = "projectiles/" + self.PROJECTILE_DATA[projectile]["image"]
            loadedImg = pygame.image.load(os.path.join(self.SPRITES_DIR, filePath)).convert_alpha()
            self.PROJECTILE_IMAGES[projectile] = loadedImg

        # TOWERS
        self.TOWER_DATA = json.load(open(os.path.join(self.SPRITES_DIR, "towers/tower-data.json")))
        self.TOWER_IMAGES = {}
        for tower in self.TOWER_DATA:
            filePath = "towers/" + self.TOWER_DATA[tower]["image"]
            loadedImg = pygame.image.load(os.path.join(self.SPRITES_DIR, filePath)).convert_alpha()
            self.TOWER_IMAGES[tower] = loadedImg  

        filePath = "towers/Range-border.png"
        self.TOWER_RANGE_IMAGE = pygame.image.load(os.path.join(self.SPRITES_DIR, filePath)).convert_alpha()

        filePath = "towers/Tower.png"
        self.TOWER_BASE_IMAGE = pygame.image.load(os.path.join(self.SPRITES_DIR, filePath)).convert_alpha()

        # TOWER MENU
        filePath = "tower_menu/Tower-Border.png"
        self.TOWER_MENU_BORDER = pygame.image.load(os.path.join(self.SPRITES_DIR, filePath)).convert_alpha()

        filePath = "tower_menu/Tower-Background.png"
        self.TOWER_MENU_BACKGROUND = pygame.image.load(os.path.join(self.SPRITES_DIR, filePath)).convert_alpha()

        filePath = "tower_menu/Menu-Item-Background.png"
        self.TOWER_MENU_ITEM_BACKGROUND = pygame.image.load(os.path.join(self.SPRITES_DIR, filePath)).convert_alpha()

    def load_states(self):
        ### Load all states and add title_screen state to stack ###
        self.title_screen = Title_Screen(self)
        self.state_stack.append(self.title_screen)

    def reset_all_keys(self):
        for action in self.actions:
            self.actions[action] = False

    def reset_keys(self):
        for key in self.keys_to_reset:
            self.actions[key] = False
        self.keys_to_reset.clear()

    def switch_mode(self):
        if self.mode == MODE.PLAY:
            self.mode = MODE.DEBUG
        else:
            self.mode = MODE.PLAY

    ### HELPERS ###
    def draw_text(self, surface, text, color, x, y):
        ### Helper function to draw text ###
        text_surface = self.FONT.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        surface.blit(text_surface, text_rect)

    ### PRIVATE HELPERS ###
    def __action_click(self, whichAction):
        if not self.actions[whichAction] and self.actions[whichAction + "_HELD"]:
            self.actions[whichAction] = True
            self.keys_to_reset.append(whichAction)
        

if __name__ == "__main__":
    g = Game()
    g.run()