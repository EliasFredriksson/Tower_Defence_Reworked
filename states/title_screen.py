from states.state import State
from states.game_world import Game_World
from constants import COLORS

class Title_Screen(State):
    def __init__(self, game):
        super().__init__(game)

    def update(self, delta_time, actions):
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
    