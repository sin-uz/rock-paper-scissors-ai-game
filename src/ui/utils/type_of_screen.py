from enum import Enum, auto


class TypeOfScreen(Enum):
    BEFORE_START = auto()
    DURING_ROUND = auto()
    RESULT_OF_ROUND = auto()
    END_OF_GAME = auto()
