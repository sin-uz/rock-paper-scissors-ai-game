import cv2
from .game_state import GameState
from domain import Outcome, Move

class GameUI:

    MOVE_NAMES = {
        Move.ROCK: "Kamien",
        Move.PAPER: "Papier",
        Move.SCISSORS: "Nozyce"
    }

    def __init__(self, move_classifier=None):
        
        self.move_classifier = move_classifier
    
    
    def render(self, frame, game_logic):
        
        height, width = frame.shape[:2]
        
        score_text = f"Player: {game_logic.player_score}  Computer: {game_logic.computer_score}"
        cv2.putText(frame, score_text, (10, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
        
        if game_logic.state == GameState.IDLE:
            self._render_idle(frame, width, height, game_logic)
        
        elif game_logic.state == GameState.COUNTDOWN:
            self._render_countdown(frame, width, height, game_logic)
        
        elif game_logic.state == GameState.ROUND_ACTIVE:
            self._render_round_active(frame, width, height, game_logic)
        
        elif game_logic.state == GameState.ROUND_RESULT:
            self._render_result(frame, width, height, game_logic)
        
        elif game_logic.state == GameState.GAME_OVER:
            self._render_game_over(frame, width, height, game_logic)
        
        return frame
    
    @staticmethod
    def get_move_name(move):
        return GameUI.MOVE_NAMES.get(move, "Unknown")
    
    def _render_idle(self, frame, width, height, game_logic):
        progress = game_logic.get_gesture_progress()
        
        if progress > 0:
            msg = f"Trzymaj kciuk w gore... {int(progress * 100)}%"
            color = (0, 255, 255)
        else:
            msg = "Pokaz kciuk w gore aby zaczac gre!"
            color = (0, 255, 255)
        
        cv2.putText(frame, msg, (width//2 - 300, height - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    def _render_countdown(self, frame, width, height, game_logic):
        countdown = game_logic.get_countdown_value()
        if countdown:
            cv2.putText(frame, str(countdown), (width//2 - 50, height//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 5.0, (0, 255, 0), 10)
        
        self._render_quit_instruction(frame, width, height, game_logic)
    
    def _render_round_active(self, frame, width, height, game_logic):
        msg = "Pokaz swoj ruch!"
        cv2.putText(frame, msg, (width//2 - 200, height//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
        
        self._render_quit_instruction(frame, width, height, game_logic)
    
    def _render_result(self, frame, width, height, game_logic):

        player_move_name = self.get_move_name(game_logic.current_player_move)
        computer_move_name = self.get_move_name(game_logic.current_computer_move)

        
        cv2.putText(frame, f"Ty: {player_move_name}", (50, height//2 - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        cv2.putText(frame, f"Komputer: {computer_move_name}", (50, height//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        # wynik rundy
        if game_logic.current_outcome == Outcome.PLAYER:
            result_text = "WYGRALES!"
            color = (0, 255, 0)
        elif game_logic.current_outcome == Outcome.COMPUTER:
            result_text = "PRZEGRALES!"
            color = (0, 0, 255)
        else:
            result_text = "REMIS!"
            color = (255, 255, 0)
        
        cv2.putText(frame, result_text, (50, height//2 + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
        
        self._render_quit_instruction(frame, width, height, game_logic)
    
    def _render_game_over(self, frame, width, height, game_logic):
        cv2.putText(frame, "KONIEC GRY!", (width//2 - 150, height//2 - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)
        
        final_score = f"Wynik koncowy: {game_logic.player_score} - {game_logic.computer_score}"
        cv2.putText(frame, final_score, (width//2 - 250, height//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        if game_logic.player_score > game_logic.computer_score:
            winner_text = "GRATULACJE!"
            winner_color = (0, 255, 0)
        elif game_logic.player_score < game_logic.computer_score:
            winner_text = "SPROBUJ PONOWNIE!"
            winner_color = (0, 0, 255)
        else:
            winner_text = "REMIS!"
            winner_color = (255, 255, 0)
        
        cv2.putText(frame, winner_text, (width//2 - 150, height//2 + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, winner_color, 3)
        
        progress = game_logic.get_gesture_progress()
        if progress > 0:
            restart_msg = f"Trzymaj kciuk w gore... {int(progress * 100)}%"
            restart_color = (0, 255, 255)
        else:
            restart_msg = "Kciuk w gore aby zagrac ponownie"
            restart_color = (200, 200, 200)
        
        cv2.putText(frame, restart_msg, (width//2 - 250, height - 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, restart_color, 2)
        
        cv2.putText(frame, "lub nacisnij ESC aby wyjsc", (width//2 - 200, height - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
    
    def _render_quit_instruction(self, frame, width, height, game_logic):
        progress = game_logic.get_gesture_progress()
        if progress > 0:
            quit_msg = f"Kciuk w dol... {int(progress * 100)}%"
            quit_color = (0, 255, 255)
        else:
            quit_msg = "Kciuk w dol aby zakonczyc"
            quit_color = (150, 150, 150)
        
        cv2.putText(frame, quit_msg, (width//2 - 200, height - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, quit_color, 2)