import random as rd

from src.core.domain import Move, Outcome, MOVE_BEATS


class NaiveStrategy:
    def __init__(self, action_space=tuple(Move)):
        self.action_space = action_space

    def reset(self):
        pass
    
    def select_move(self):
        return rd.choice(self.action_space)
    

class ResearchBasedStrategy:

    def __init__(
            self,
            action_space=tuple(Move),
            action_weights=[0.40, 0.35, 0.25]
    ):
        self.action_space = action_space
        self.action_weights = action_weights

    def select_move(self, match_history=None):
        # level 0
        if not match_history:
            return self.first_move()
        
        round_number = match_history[-1].round_number

        # level 1
        previous_round =  match_history[-1]

        if previous_round.outcome == Outcome.PLAYER:
            return MOVE_BEATS[previous_round.computer_move]
        elif previous_round.outcome == Outcome.COMPUTER:
            return previous_round.player_move
        else:
            return self.first_move()
        
        # level 2
        #
        #
        #

    def first_move(self):
        return rd.choices(self.action_space, self.action_weights, k=1)[0]