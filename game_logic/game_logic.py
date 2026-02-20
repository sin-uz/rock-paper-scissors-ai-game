import time
from .game_state import GameState, GameConfig
from domain import RoundRecord, evaluate_round, Outcome, ThumbDirection
from synchronizer import GameSyncController

class GameLogic:
    def __init__(self, classifier, computer_strategy):
        self.classifier = classifier
        self.computer_strategy = computer_strategy
        self.synchronizer = GameSyncController(classifier)
        
        self.state = GameState.IDLE
        self.player_score = 0
        self.computer_score = 0
        self.round_number = 0
        self.match_history = []
        
        self.gesture_start_time = None
        self.result_start_time = None
        
        self.current_player_move = None
        self.current_computer_move = None
        self.current_outcome = None
    
    def reset(self):
        self.state = GameState.IDLE
        self.player_score = 0
        self.computer_score = 0
        self.round_number = 0
        self.match_history = []
        self.gesture_start_time = None
        self.result_start_time = None
        self.current_player_move = None
        self.current_computer_move = None
        self.current_outcome = None
        self.synchronizer.reset()
    
    def update(self, primary_hand):
        current_time = time.time()
        side, landmarks = primary_hand if primary_hand else (None, None)

        if self.state not in [GameState.IDLE, GameState.GAME_OVER]:
            if self._check_quit_gesture(landmarks, current_time):
                return
      
        if self.state == GameState.IDLE:
            self._handle_idle(landmarks, current_time)
        elif self.state == GameState.ROUND_ACTIVE:
            self._handle_round_active(side, landmarks, current_time)
        elif self.state == GameState.ROUND_RESULT:
            self._handle_round_result(current_time)
        elif self.state == GameState.GAME_OVER:
            self._handle_game_over(landmarks, current_time)
    
    def _check_quit_gesture(self, landmarks, current_time):
        direction = self.classifier.determine_hand_direction(landmarks) if landmarks else None

        if direction == ThumbDirection.DOWN: 
            if self.gesture_start_time is None:
                self.gesture_start_time = current_time
            elif current_time - self.gesture_start_time >= GameConfig.GESTURE_HOLD_DURATION:
                self.state = GameState.GAME_OVER
                self.gesture_start_time = None
                return True
        else:
            if direction != ThumbDirection.UP: 
                self.gesture_start_time = None
        return False
    
    def _handle_idle(self, landmarks, current_time):
        direction = self.classifier.determine_hand_direction(landmarks) if landmarks else None

        if direction == ThumbDirection.UP: 
            if self.gesture_start_time is None:
                self.gesture_start_time = current_time
            elif current_time - self.gesture_start_time >= GameConfig.GESTURE_HOLD_DURATION:
                self.state = GameState.ROUND_ACTIVE
                self.synchronizer.reset()
                self.gesture_start_time = None
        else:
            self.gesture_start_time = None
    
    def _handle_round_active(self, side, landmarks, current_time):
        if not landmarks:
            return

        player_move = self.synchronizer.update(side, landmarks)
        if player_move is None:
            return
      
        computer_move = self.computer_strategy.select_move(self.match_history)
        outcome = evaluate_round(player_move, computer_move)
        
        self.current_player_move = player_move
        self.current_computer_move = computer_move
        self.current_outcome = outcome
        
        if outcome == Outcome.PLAYER:
            self.player_score += 1
        elif outcome == Outcome.COMPUTER:
            self.computer_score += 1
        
        self.round_number += 1
        round_record = RoundRecord(
            round_number=self.round_number,
            player_move=player_move,
            computer_move=computer_move,
            outcome=outcome
        )
        self.match_history.append(round_record)
        
        self.state = GameState.ROUND_RESULT
        self.result_start_time = current_time
    
    def _handle_round_result(self, current_time):
        elapsed = current_time - self.result_start_time
        if elapsed >= GameConfig.RESULT_DURATION:
            self.state = GameState.ROUND_ACTIVE
            self.synchronizer.reset()
            self.current_player_move = None
            self.current_computer_move = None
            self.current_outcome = None
    
    def _handle_game_over(self, landmarks, current_time):
        direction = self.classifier.determine_hand_direction(landmarks) if landmarks else None
        
        if direction == ThumbDirection.UP: 
            if self.gesture_start_time is None:
                self.gesture_start_time = current_time
            elif current_time - self.gesture_start_time >= GameConfig.GESTURE_HOLD_DURATION:
                self.reset()
                self.gesture_start_time = None
        else:
            self.gesture_start_time = None
    
    def get_gesture_progress(self):
        if self.gesture_start_time is None:
            return 0.0
        
        elapsed = time.time() - self.gesture_start_time
        progress = min(elapsed / GameConfig.GESTURE_HOLD_DURATION, 1.0)
        return progress
