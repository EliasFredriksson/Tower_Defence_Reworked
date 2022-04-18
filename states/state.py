from abc import ABC, abstractmethod

class State(ABC):
    def __init__(self, game, has_new_assets = False):
        self.game = game
        self.prev_state = None
        self.needs_loading = has_new_assets
        self.IS_LOADING = False

    @abstractmethod
    def update(self, delta_time, actions):
        ### ALWAYS CALL super().update(delta_time, actions) BEFORE WRITING YOUR OWN CODE ###
        if self.needs_loading:
            self.__trigger_loading()
        
    @abstractmethod
    def render(self, canvas):
        pass

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()

    @abstractmethod
    def load_assets(self):
        ### CALL super().load_assets() WHEN YOU ARE DONE LOADING IN NEW ASSETS ###
        self.needs_loading = False

    def __trigger_loading(self):
        self.IS_LOADING = True
        self.load_assets()
        self.IS_LOADING = False