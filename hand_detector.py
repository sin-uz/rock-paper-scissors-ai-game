import cv2
import mediapipe as mp

class HandDetector:
    def __init__(
        self,
        mirror_view = True,
        static_image_mode: bool = False,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        self._mirror_view = mirror_view
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        self._hands.close()
        
    def detect(self, frame_bgr):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(frame_rgb)

        return self._extract_hands_by_side(results)
    
    def _extract_hands_by_side(self, results):
        hands_by_side = {}

        if not results.multi_hand_landmarks or not results.multi_handedness:
            return hands_by_side
        
        for handedness, hand_landmarks in zip(
            results.multi_handedness,
            results.multi_hand_landmarks
        ):
            side = self._extract_side(handedness)
            landmark_coordinates = self._to_coordinates(hand_landmarks)
            hands_by_side[side] = landmark_coordinates

        return hands_by_side

    def _extract_side(self, handedness):
        side = handedness.classification[0].label
        if self._mirror_view:
            side = "Left" if side == "Right" else "Right"

        return side

    @staticmethod
    def _to_coordinates(hand_landmarks):
        return [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]