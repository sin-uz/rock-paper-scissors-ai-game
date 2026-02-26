from collections.abc import Callable

import cv2
from cv2 import VideoCapture

from src.ml.hand_detector import HandDetector
from src.core.game_logic import GameLogic
from src.logic.game_ui import GameUI
from src.core.strategies import ResearchBasedStrategy
from .game_state import GameState
from ..ui.utils.bridge import UiBridge, EventFrameChanged


class GameController:

    def __init__(self,
                 classifier,
                 bridge: UiBridge,
                 *,
                 computer_strategy: ResearchBasedStrategy = None,
                 cap: VideoCapture = None
                 ):

        self._ui_bridge = bridge
        self.logic = GameLogic(
            self._ui_bridge,
            classifier = classifier,
            computer_strategy=computer_strategy or ResearchBasedStrategy()
        )
        self.ui = GameUI()
        self._cap = cap or VideoCapture(0)
        self._stop_detection = False

    def start(self):
        with HandDetector(
            user_perspective=True,
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        ) as detector:
            while self._cap.isOpened():
                if self._stop_detection:
                    continue

                reft, frame = self._cap.read()
                if not reft:
                    break

                detected_hands = detector.detect(frame)
                self.update(detected_hands, frame)

                self._ui_bridge.event_frame_changed.emit(EventFrameChanged(frame, detected_hands))
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
        """
        Priorytet wykrywania ręki prawej nad lewą
        """
        primary_hand = None
        if "Right" in detected_hands:
            primary_hand = ("Right", detected_hands["Right"])
        elif "Left" in detected_hands:
            primary_hand = ("Left", detected_hands["Left"])
        
        self.logic.update(primary_hand, frame)

    def render_ui(self, frame):
        return self.ui.render(frame, self.logic)
    
    def is_game_over(self):
        return self.logic.state == GameState.GAME_OVER

    def set_stop_detection(self, stop: bool):
        self._stop_detection = stop

    def close(self):
        if self._cap.isOpened():
            self._cap.release()