import time
from domain import Move

class GameSyncController:
    def __init__(self, swing_threshold=0.15, gesture_confirm_time=0.5):
        self.swing_threshold = swing_threshold 
        self.gesture_confirm_time = gesture_confirm_time
        self.state = "WAITING"
        self.swings_detected = 0
        self.last_y = None
        self.min_y = 1.0
        self.max_y = 0.0
        self.current_gesture = None
        self.gesture_start_time = None

    def is_fist(self, landmarks):
        tips = [8, 12, 16, 20]
        knuckles = [6, 10, 14, 18]
        return all(landmarks[t][1] > landmarks[k][1] for t, k in zip(tips, knuckles))

    def get_move_from_landmarks(self, lm):
        is_8_up = lm[8][1] < lm[6][1]
        is_12_up = lm[12][1] < lm[10][1]
        is_16_up = lm[16][1] < lm[14][1]
        
        if not is_8_up and not is_12_up:
            return Move.ROCK
        if is_8_up and is_12_up and not is_16_up:
            return Move.SCISSORS
        if is_8_up and is_12_up and is_16_up:
            return Move.PAPER
        return None

    def update(self, landmarks):
        if not landmarks:
            self.reset()
            return None

        curr_y = landmarks[9][1]

        if self.state in ["WAITING", "SWING_1"]:
            if self.is_fist(landmarks):
                if self.last_y is not None:
                    if curr_y > self.max_y: self.max_y = curr_y

                    if self.max_y - curr_y > self.swing_threshold:
                        self.swings_detected += 1
                        self.max_y = 0
                        
                        if self.swings_detected >= 2:
                            self.state = "STABILIZING"
            self.last_y = curr_y

        elif self.state == "STABILIZING":
            detected_move = self.get_move_from_landmarks(landmarks)
            
            if detected_move and detected_move == self.current_gesture:
                duration = time.time() - self.gesture_start_time
                if duration >= self.gesture_confirm_time:
                    final_move = self.current_gesture
                    self.reset()
                    return final_move
            else:
                self.current_gesture = detected_move
                self.gesture_start_time = time.time()

        return None

    def reset(self):
        self.state = "WAITING"
        self.swings_detected = 0
        self.last_y = None
        self.max_y = 0
        self.current_gesture = None