import time

from src.core.game_state import GameState, GameConfig
from src.core.domain import RoundRecord, evaluate_round, Outcome, ThumbDirection
from src.ui.utils.bridge import UiBridge, EventGameOver, EventGameCountdown, EventGameRoundActive, \
    EventGameRoundResult, EventScoreChanged, EventGestureProgress


class GameLogic:
    def __init__(self,
                 ui_bridge: UiBridge,
                 classifier,
                 synchronizer,
                 computer_strategy
                 ):
        self._ui_bridge = ui_bridge

        self.classifier = classifier
        self.synchronizer = synchronizer
        self.computer_strategy = computer_strategy
        
        self.state = GameState.IDLE
        self.player_score = 0
        self.computer_score = 0
        self.round_number = 0
        self.match_history = []
        
        self.gesture_start_time = None
        self.countdown_start_time = None
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
        self.countdown_start_time = None
        self.result_start_time = None
        self.current_player_move = None
        self.current_computer_move = None
        self.current_outcome = None

        self.synchronizer.reset()
    
    def update(self, primary_hand, frame):
        current_time = time.time()
        side, landmarks = primary_hand if primary_hand else (None, None)

        if self.state not in [GameState.IDLE, GameState.GAME_OVER]:
            if self._check_quit_gesture(landmarks, current_time):
                return
      
        if self.state == GameState.IDLE:
            self._handle_idle(landmarks, current_time)
        elif self.state == GameState.COUNTDOWN:
            self._handle_countdown(current_time)
        elif self.state == GameState.ROUND_ACTIVE:
            self._handle_round_active(side, landmarks, current_time, frame)
        elif self.state == GameState.ROUND_RESULT:
            self._handle_round_result(current_time)
        elif self.state == GameState.GAME_OVER:
            self._handle_game_over(landmarks, current_time)
    
    def _check_quit_gesture(self, landmarks, current_time):

        direction = self.classifier.determine_hand_direction(landmarks) if landmarks else None

        if direction == ThumbDirection.DOWN: ##
            if self.gesture_start_time is None:
                self.gesture_start_time = current_time

            elif current_time - self.gesture_start_time >= GameConfig.GESTURE_HOLD_DURATION:
                self.state = GameState.GAME_OVER
                self._ui_bridge.event_game_over.emit(EventGameOver(
                    player_score=self.player_score,
                    computer_score=self.computer_score,
                    match_history=self.match_history,
                ))
                self.gesture_start_time = None
                return True

            self._ui_bridge.event_gesture_progress.emit(EventGestureProgress(
                progress=self.get_gesture_progress(),
                thumb_direction=direction
            ))
        else:
            if direction != ThumbDirection.UP: ##
                    self.gesture_start_time = None
        return False
    
    def _handle_idle(self, landmarks, current_time):
        direction = self.classifier.determine_hand_direction(landmarks) if landmarks else None

        if direction == ThumbDirection.UP: ##
            if self.gesture_start_time is None:
                self.gesture_start_time = current_time
            elif current_time - self.gesture_start_time >= GameConfig.GESTURE_HOLD_DURATION:
                self.state = GameState.COUNTDOWN
                self.countdown_start_time = current_time
                self.gesture_start_time = None
                self._ui_bridge.event_game_started.emit(self.state)
                self._ui_bridge.event_game_countdown.emit(EventGameCountdown(
                    count_down_time=self.get_countdown_value()
                ))
                return

            self._ui_bridge.event_gesture_progress.emit(EventGestureProgress(
                progress=self.get_gesture_progress(),
                thumb_direction=direction
            ))
        else:
            self.gesture_start_time = None
    
    def _handle_countdown(self, current_time):
        elapsed = current_time - self.countdown_start_time
        if elapsed >= GameConfig.COUNTDOWN_DURATION:
            self.state = GameState.ROUND_ACTIVE
            self.round_number += 1

            self._ui_bridge.event_game_round_active.emit(EventGameRoundActive())
        else:
            self._ui_bridge.event_game_countdown.emit(EventGameCountdown(
                count_down_time=self.get_countdown_value()
            ))
    
    def _handle_round_active(self, side, landmarks, current_time, frame):
        if not landmarks:
            self.synchronizer.reset()
            return
        
        player_move, sync_status = self.synchronizer.update(
            side, landmarks, current_time
        )
        print(f"Sync status: {sync_status}")

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
        
        round_record = RoundRecord(
            round_number=self.round_number,
            player_move=player_move,
            computer_move=computer_move,
            outcome=outcome
        )
        self.match_history.append(round_record)
        
        self.state = GameState.ROUND_RESULT
        self._ui_bridge.event_game_round_result.emit(EventGameRoundResult(
            round_record=round_record,
            frame=frame
        ))
        self._ui_bridge.event_score_changed.emit(EventScoreChanged(
            computer_score=self.computer_score,
            player_score=self.player_score
        ))

        self.result_start_time = current_time
    
    def _handle_round_result(self, current_time):
        elapsed = current_time - self.result_start_time
        if elapsed >= GameConfig.RESULT_DURATION:
            self.state = GameState.COUNTDOWN
            # self._ui_bridge.state_changed.emit(StateChangeEventData(
            #     self.state,
            #     player_score=self.player_score,
            #     computer_score=self.computer_score,
            #     match_history=self.match_history,
            # ))
            # self._ui_bridge.event_game_countdown.emit(EventGameCountdown(
            #     count_down_time=self.get_countdown_value()
            # ))
            self.countdown_start_time = current_time
            self.current_player_move = None
            self.current_computer_move = None
            self.current_outcome = None
    
    def _handle_game_over(self, landmarks, current_time):
        direction = self.classifier.determine_hand_direction(landmarks) if landmarks else None
        
        if direction == ThumbDirection.UP: ##
            if self.gesture_start_time is None:
                self.gesture_start_time = current_time
            elif current_time - self.gesture_start_time >= GameConfig.GESTURE_HOLD_DURATION:
                self.reset()
                self.gesture_start_time = None
        else:
            self.gesture_start_time = None
    
    def get_countdown_value(self):
        if self.state != GameState.COUNTDOWN or self.countdown_start_time is None:
            return None
        
        elapsed = time.time() - self.countdown_start_time
        remaining = GameConfig.COUNTDOWN_DURATION - elapsed
        
        if remaining > 2.0:
            return 3
        elif remaining > 1.0:
            return 2
        elif remaining > 0.0:
            return 1
        return None
    
    def get_gesture_progress(self):
        if self.gesture_start_time is None:
            return 0.0
        
        elapsed = time.time() - self.gesture_start_time
        progress = min(elapsed / GameConfig.GESTURE_HOLD_DURATION, 1.0)
        return progress