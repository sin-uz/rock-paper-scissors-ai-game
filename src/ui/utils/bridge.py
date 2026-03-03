from dataclasses import dataclass

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

@dataclass
class EventFrameChanged(EventWithFrame):
    def __init__(self, frame: cv2.typing.MatLike, detected_hands: dict[str, list[tuple[float, float, float]]]):
        super().__init__(frame)
        self.detected_hands = detected_hands

@dataclass
class EventScoreChanged:
    def __init__(self, player_score: int, computer_score: int):
        self.player_score = player_score
        self.computer_score = computer_score


@dataclass
class EventGameIdle:
    def __init__(self):
        pass

@dataclass
class EventGameCountdown:
    def __init__(self, count_down_time: int):
        self.count_down_time = count_down_time

@dataclass
class EventGameRoundActive:
    def __init__(self):
        pass

@dataclass
class EventGameRoundResult(EventWithFrame):
    def __init__(self, round_record: RoundRecord, frame: cv2.typing.MatLike):
        super().__init__(frame)
        self.round_record = round_record

@dataclass
class EventGameOver:
    def __init__(self, player_score: int, computer_score: int, match_history: list[RoundRecord]):
        self.player_score = player_score
        self.computer_score = computer_score
        self.match_history = match_history


@dataclass
class EventGestureProgress:
    def __init__(self, progress: float, thumb_direction: ThumbDirection):
        self.progress = progress
        self.thumb_direction = thumb_direction


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


