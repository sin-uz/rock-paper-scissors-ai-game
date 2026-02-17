from .game_logic import GameLogic
from .game_ui import GameUI
from strategies import ResearchBasedStrategy

class GameController:

    def __init__(self, classifier, computer_strategy = None):
        self.logic = GameLogic(
            classifier = classifier,
            computer_strategy=computer_strategy or ResearchBasedStrategy()
        )
        
        self.ui = GameUI()
        
        self._export_properties()
    
    def _export_properties(self):
        pass

    @property
    def player_score(self):
        return self.logic.player_score
    
    @property
    def computer_score(self):
        return self.logic.computer_score
    
    @property
    def match_history(self):
        return self.logic.match_history
    
    @property
    def state(self):
        return self.logic.state

    def reset(self):
        self.logic.reset()

    def update(self, detected_hands): #priorytet prawa > lewa
        primary_hand = None
        if "Right" in detected_hands:
            primary_hand = ("Right", detected_hands["Right"])
        elif "Left" in detected_hands:
            primary_hand = ("Left", detected_hands["Left"])
        
        self.logic.update(primary_hand)

    def render_ui(self, frame):
        return self.ui.render(frame, self.logic)
    
    def is_game_over(self):
        from game_state import GameState
        return self.logic.state == GameState.GAME_OVER