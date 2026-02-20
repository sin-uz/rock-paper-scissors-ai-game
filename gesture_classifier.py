import random
import numpy as np
import mediapipe as mp

from domain import Move, ThumbDirection


class GestureClassifier:
    def __init__(
            self,
            wrist_thumb_threshold: float = 0.15,
            index_thumb_threshold: float = 0.05,
            thumb_straight_threshold: float = 0.02,
    ):
        self.wrist_thumb_threshold = wrist_thumb_threshold
        self.index_thumb_threshold = index_thumb_threshold
        self.thumb_straight_threshold = thumb_straight_threshold

    def classify_something(self, detected_hands):
        something = []

        for side, landmarks in detected_hands.items():
            something.append(self.determine_hand_direction(landmarks))
            something.append((side, self.determine_move(side, landmarks)))

        return something

    def determine_hand_direction(self, landmarks):
        if not self._is_thumb_straightened_y(landmarks):
            return None
        
        wrist_y_coord = self._get_coordinate(landmarks, self._HL.WRIST, 1)
        thumb_y_coord = self._get_coordinate(landmarks, self._HL.THUMB_TIP, 1)
        index_finger_y_coord = self._get_coordinate(
            landmarks, self._HL.INDEX_FINGER_MCP, 1
        )
        wrist_to_thumb = wrist_y_coord - thumb_y_coord
        index_to_thumb = index_finger_y_coord - thumb_y_coord

        if (
            wrist_to_thumb > self.wrist_thumb_threshold and
            index_to_thumb > self.index_thumb_threshold
        ):
            return ThumbDirection.UP
        elif (
            wrist_to_thumb < -self.wrist_thumb_threshold and
            index_to_thumb < -self.index_thumb_threshold
        ):
            return ThumbDirection.DOWN
        
        return None

    def determine_move(self, side, landmarks):
        patterns = {
            (False, False, False, False, False): Move.ROCK,
            (True, True, True, True, True): Move.PAPER,
            (False, True, True, False, False): Move.SCISSORS
        }

        return patterns.get(self._finger_states(side, landmarks))

    def _finger_states(self, side, landmarks):
        return (
            self._is_thumb_straightened_x(side, landmarks),
            self._is_finger_straightened(landmarks, self._HL.INDEX_FINGER_TIP),
            self._is_finger_straightened(landmarks, self._HL.MIDDLE_FINGER_TIP),
            self._is_finger_straightened(landmarks, self._HL.RING_FINGER_TIP),
            self._is_finger_straightened(landmarks, self._HL.PINKY_TIP),
        )

    def _is_thumb_straightened_x(self, side, landmarks):
        tip_x_coord = self._get_coordinate(landmarks, self._HL.THUMB_TIP, 0)
        ip_x_coord = self._get_coordinate(landmarks, self._HL.THUMB_IP, 0)

        if side == "Left":
            return tip_x_coord < ip_x_coord
        else:
            return tip_x_coord > ip_x_coord

    def _is_thumb_straightened_y(self, landmarks):
        tip_y_coord = self._get_coordinate(landmarks, self._HL.THUMB_TIP, 1)
        ip_y_coord = self._get_coordinate(landmarks, self._HL.THUMB_IP, 1)

        return abs(tip_y_coord - ip_y_coord) > self.thumb_straight_threshold

    def _is_finger_straightened(self, landmarks, tip_id):
        tip_y_coordinate = self._get_coordinate(landmarks, tip_id, 1)
        pip_y_coordinate = self._get_coordinate(landmarks, tip_id - 2, 1)
        return tip_y_coordinate < pip_y_coordinate

    def _get_coordinate(self, hand_landmarks, landmark_id, axis):
        return hand_landmarks[int(landmark_id)][axis]

    @property
    def _HL(self):
        return mp.solutions.hands.HandLandmark
    
    
class MockClassifier: 
    def __init__(self):
        self.moves= list(Move)

    def classify_something(self, landmarks):
        if not landmarks:
            return None

        return random.choice(self.moves)
    

class VectorBasedClassifier(GestureClassifier):
    def __init__(self, straightening_threshold: float = 0):
        super().__init__()

        self.straightening_threshold = straightening_threshold

    def determine_move(self, side, landmarks):
        patterns = {
            (False, False, False, False): Move.ROCK,
            (True, True, True, True): Move.PAPER,
            (True, True, False, False): Move.SCISSORS
        }

        return patterns.get(self._finger_states(side, landmarks))
    
    def _finger_states(self, side, landmarks):
        return (
            self._is_finger_straightened(landmarks, self._HL.INDEX_FINGER_PIP),
            self._is_finger_straightened(landmarks, self._HL.MIDDLE_FINGER_PIP),
            self._is_finger_straightened(landmarks, self._HL.RING_FINGER_PIP),
            self._is_finger_straightened(landmarks, self._HL.PINKY_PIP),
        )
    
    def _is_finger_straightened(self, landmarks, finger_pip_id):
        dot_product = self._calculate_dot_product(landmarks, finger_pip_id)

        return True if dot_product > self.straightening_threshold else False

    def _calculate_dot_product(self, landmarks, finger_pip_id):
        inner_vector = self._calculate_inner_vector(landmarks, finger_pip_id)
        outer_vector = self._calculate_outer_vector(landmarks, finger_pip_id)

        return float(
            np.dot(inner_vector, outer_vector) /
            (np.linalg.norm(inner_vector) * np.linalg.norm(outer_vector))
        )

    def _calculate_outer_vector(self, landmarks, finger_pip_id):
        return self._calculate_vector(
            landmarks, finger_pip_id, finger_pip_id + 2
        )

    def _calculate_inner_vector(self, landmarks, finger_pip_id):
        return self._calculate_vector(
            landmarks, finger_pip_id - 1, finger_pip_id
        )

    def _calculate_vector(self, landmarks, lm1_id, lm2_id):
        lm1_coords = np.array(self._get_all_coordinates(landmarks, lm1_id))
        lm2_coords = self._get_all_coordinates(landmarks, lm2_id)

        return lm2_coords - lm1_coords

    def _get_all_coordinates(self, hand_landmarks, landmark_id):
        return hand_landmarks[int(landmark_id)]
