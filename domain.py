from enum import Enum, auto
from dataclasses import dataclass

# types
class Move(Enum):
    ROCK = auto()
    PAPER = auto()
    SCISSORS = auto()

class Outcome(Enum):
    PLAYER = auto()
    COMPUTER = auto()
    DRAW = auto()


# records
@dataclass(frozen=True, slots=True)
class RoundRecord:
    round_number: int
    player_move: Move
    computer_move: Move
    outcome: Outcome

class GameSummary:
    def __init__(self):
        pass


# rules
MOVE_BEATS = {
    Move.ROCK: Move.SCISSORS,
    Move.PAPER: Move.ROCK,
    Move.SCISSORS: Move.PAPER
}

def evaluate_round(player: Move, computer: Move):
    if player == computer:
        return Outcome.DRAW
    
    return Outcome.PLAYER if MOVE_BEATS[player] == computer else Outcome.COMPUTER