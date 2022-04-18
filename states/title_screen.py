from states.state import State
from states.game_world import Game_World
from constants import COLORS

class Title_Screen(State):
    def __init__(self, game):
        ### WE SEND True TO TELL THE STATE MACHINE THAT NEW ASSETS NEEDS LOADING ###
        super().__init__(game, True)

    def update(self, delta_time, actions):
        ### NEEDS TO BE CALLED AT START OF UPDATE FUNCTION TO MAKE SURE NEW ASSETS ARE LOADED ###
        super().update(delta_time, actions)
        if actions["START"]:
            new_state = Game_World(self.game)
            new_state.enter_state()
        

    def render(self, canvas):
        canvas.fill(COLORS.GREEN)
        self.game.draw_text(canvas, "Game State Demo", COLORS.BLACK, self.game.GAME_WIDTH/2, self.game.GAME_HEIGHT/2)


    def enter_state(self):
        super().enter_state()

    def exit_state(self):
        super().exit_state()
    
    def load_assets(self):
        ### LOAD ASSETS BEFORE CALLING super().load_assets() ###
        print("TITLE SCREEN")
        super().load_assets()