import cv2
from .game_state import GameState
from domain import Outcome, Move

class GameUI:
    MOVE_NAMES = {
        Move.ROCK: "Kamien",
        Move.PAPER: "Papier",
        Move.SCISSORS: "Nozyce"
    }

    def render(self, frame, game_logic):
        height, width = frame.shape[:2]
        
        score_text = f"Gracz: {game_logic.player_score}  Komputer: {game_logic.computer_score}"
        cv2.putText(frame, score_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)
        
        if game_logic.state == GameState.IDLE:
            cv2.putText(frame, "Pokaz KCIUK W GORE, aby zaczac", (50, height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            
        elif game_logic.state == GameState.ROUND_ACTIVE:
            sync_state = game_logic.synchronizer.state
            swings = game_logic.synchronizer.swings_detected
            
            if sync_state in ["WAITING", "SWING_1"]:
                cv2.putText(frame, f"Zacisnij piest i machnij! ({swings}/2)", (50, height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 2)
            elif sync_state == "STABILIZING":
                cv2.putText(frame, "Pokaz i zatrzymaj znak!", (50, height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                
        elif game_logic.state == GameState.ROUND_RESULT:
            player_str = self.MOVE_NAMES[game_logic.current_player_move]
            comp_str = self.MOVE_NAMES[game_logic.current_computer_move]
            
            cv2.putText(frame, f"Ty: {player_str}", (50, height//2 - 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(frame, f"Komputer: {comp_str}", (50, height//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            
            if game_logic.current_outcome == Outcome.PLAYER:
                win_text, color = "WYGRYWASZ!", (0, 255, 0)
            elif game_logic.current_outcome == Outcome.COMPUTER:
                win_text, color = "PRZEGRYWASZ!", (0, 0, 255)
            else:
                win_text, color = "REMIS!", (255, 255, 0)
                
            cv2.putText(frame, win_text, (50, height//2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
            
        return frame
