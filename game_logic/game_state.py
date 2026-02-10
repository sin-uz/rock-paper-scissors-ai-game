from enum import Enum, auto

#stany gry
class GameState(Enum):
    IDLE = auto()
    WAITING_TO_START = auto()
    COUNTDOWN = auto()
    ROUND_ACTIVE = auto()
    ROUND_RESULT = auto()
    WAITING_TO_QUIT = auto()
    GAME_OVER = auto()

#ustawione czasy
class GameConfig:
    GESTURE_HOLD_DURATION = 2.0    
    COUNTDOWN_DURATION = 3.0      
    RESULT_DURATION = 3.0    