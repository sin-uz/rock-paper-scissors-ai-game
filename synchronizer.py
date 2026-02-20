import time
from domain import Move

class GameSyncController:
    def __init__(self, classifier, swing_threshold=0.1, gesture_confirm_time=0.8):
        self.classifier = classifier
        self.swing_threshold = swing_threshold 
        self.gesture_confirm_time = gesture_confirm_time
        self.state = "WAITING"
        self.swings_detected = 0
        self.min_y = 1.0 
        self.current_gesture = None
        self.gesture_start_time = None

    def update(self, side, landmarks):
        if not landmarks:
            self.reset()
            return None

        curr_y = landmarks[0][1]
        detected_move = self.classifier.determine_move(side, landmarks)

        if self.state in ["WAITING", "SWING_1"]:
            if curr_y < self.min_y: 
                self.min_y = curr_y

            if curr_y - self.min_y > self.swing_threshold:
                self.swings_detected += 1
                self.min_y = 1.0
                
                if self.swings_detected >= 2:
                    self.state = "STABILIZING"
                    self.current_gesture = None
                    self.gesture_start_time = None

        elif self.state == "STABILIZING":
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
        self.min_y = 1.0
        self.current_gesture = None
        self.gesture_start_time = None