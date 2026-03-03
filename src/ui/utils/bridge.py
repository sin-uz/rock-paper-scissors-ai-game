from dataclasses import dataclass, field

import cv2
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QPixmap, QImage

from src.core.domain import RoundRecord, ThumbDirection
from src.core.game_state import GameState


class EventWithFrame:
    def __init__(self, frame: cv2.typing.MatLike):
        self.frame = frame

    def mirror_frame(self) -> None:
        self.frame = cv2.flip(self.frame, 1)

    def get_pixmap(self) -> QPixmap:
        rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        height, width, _ = rgb_frame.shape
        image = QImage(
            rgb_frame.data,
            width,
            height,
            width * 3,
            QImage.Format.Format_RGB888,
        )
        return QPixmap.fromImage(image)


class EventFrameChanged(EventWithFrame):
    def __init__(self, frame: cv2.typing.MatLike, detected_hands: dict[str, list[tuple[float, float, float]]]):
        super().__init__(frame)
        self.detected_hands = detected_hands


@dataclass
class EventScoreChanged:
    player_score: int
    computer_score: int


@dataclass
class EventGameIdle:
    pass


@dataclass
class EventGameCountdown:
    count_down_time: int


@dataclass
class EventGameRoundActive:
    pass


class EventGameRoundResult(EventWithFrame):
    def __init__(self, round_record: RoundRecord, frame: cv2.typing.MatLike):
        super().__init__(frame)
        self.round_record = round_record


@dataclass
class EventGameOver:
    player_score: int
    computer_score: int
    match_history: list = field(default_factory=list)


@dataclass
class EventGestureProgress:
    progress: float
    thumb_direction: ThumbDirection


class UiBridge(QObject):
    event_frame_changed = Signal(EventFrameChanged)
    event_score_changed = Signal(EventScoreChanged)
    event_game_started = Signal(GameState)
    event_game_idle = Signal(EventGameIdle)
    event_game_countdown = Signal(EventGameCountdown)
    event_gesture_progress = Signal(EventGestureProgress)
    event_game_round_active = Signal(EventGameRoundActive)
    event_game_round_result = Signal(EventGameRoundResult)
    event_game_over = Signal(EventGameOver)
