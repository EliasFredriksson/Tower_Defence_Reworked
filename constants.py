from enum import Enum
######### COLORS ARE SPECIFIED IN RGB #########
class COLORS():
    BLACK = (0, 0, 0)
    WHITE = (255,255,255)
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)

class MODE(Enum):
    PLAY = "play"
    DEBUG = "debug"