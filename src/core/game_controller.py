import time
import cv2

from src.ml.hand_detector import HandDetector
from src.core.game_logic import GameLogic

from src.core.game_state import GameState
from src.ui.utils.bridge import UiBridge, EventFrameChanged


class GameController:
    def __init__(self,
                 classifier,
                 computer_strategy,
                 bridge: UiBridge,
                 *,
                 detection_camera_index: int = 0,
                 showing_camera_index: int = None,
                 cap: cv2.VideoCapture = None,
                 ):

        self._ui_bridge = bridge
        self.logic = GameLogic(
            self._ui_bridge,
            classifier=classifier,
            computer_strategy=computer_strategy
        )
        self._cap = cap or cv2.VideoCapture(detection_camera_index)
        self._showing_cap = cv2.VideoCapture(showing_camera_index) if showing_camera_index is not None else None
        self._stop_detection = False

    def start(self):
        with HandDetector(
                user_perspective=True,
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
        ) as detector:
            while self._cap.isOpened():
                if self._stop_detection:
                    time.sleep(0.05)
                    continue

                reft, frame = self._cap.read()
                if not reft:
                    break

                detected_hands = detector.detect(frame)
                self.update(detected_hands, frame)

                reft2, showing_frame = self._showing_cap.read() if self._showing_cap is not None else (False, None)
                if reft2 and showing_frame is not None:
                    detected_hands = detector.detect(showing_frame)
                    frame = showing_frame

                self._ui_bridge.event_frame_changed.emit(
                    EventFrameChanged(frame, detected_hands)
                )

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

    def update(self, detected_hands: dict[str, list[tuple[float, float, float]]], frame: cv2.typing.MatLike) -> None:
        """Right hand takes priority over left hand for gesture detection."""
        primary_hand = None
        if "Right" in detected_hands:
            primary_hand = ("Right", detected_hands["Right"])
        elif "Left" in detected_hands:
            primary_hand = ("Left", detected_hands["Left"])

        self.logic.update(primary_hand, frame)

    def is_game_over(self):
        return self.logic.state == GameState.GAME_OVER

    def set_stop_detection(self, stop: bool):
        self._stop_detection = stop

    def close(self):
        if self._cap.isOpened():
            self._cap.release()
        if self._showing_cap is not None and self._showing_cap.isOpened():
            self._showing_cap.release()
