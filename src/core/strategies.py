import random as rd

from domain import Move, Outcome, MOVE_BEATS, MOVE_LOSES


class NaiveStrategy:
    def __init__(self, action_weights: list = [0.25, 0.40, 0.35]):
        self.action_weights = action_weights

    def select_move(self, match_history=None):
        if not match_history:
            return self.first_move()

    def first_move(self):
        return rd.choices(tuple(Move), self.action_weights, k=1)[0]


class ResearchBasedStrategy(NaiveStrategy):

    def select_move(self, match_history=None):
        if not match_history:
            return self.first_move()

        previous_round =  self._get_previous_round(match_history)
        last_three_moves = self._get_last_moves(match_history)[-3:]

        if self._are_moves_same(last_three_moves):
            return MOVE_LOSES[previous_round.player_move]

        if previous_round.outcome == Outcome.PLAYER:
            return MOVE_BEATS[previous_round.computer_move]
        elif previous_round.outcome == Outcome.COMPUTER:
            return previous_round.player_move

        return self.first_move()
        
    def _get_previous_round(self, match_history):
        return match_history[-1]

    def _get_last_moves(self, match_history):
        return [round.player_move.value for round in match_history]

    def _are_moves_same(self, moves):
        return len(set(moves)) == 1