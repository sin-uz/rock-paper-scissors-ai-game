from PySide6.QtCore import Qt
from PySide6.QtWidgets import (

    QVBoxLayout,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect, QMainWindow, QWidget,
)

from src.core.game_state import GameState
from src.ui.components.camera import CameraFrame
from src.ui.components.header import Header
from src.core.game_controller import GameController
from src.ui.components.score import ScoreFrame
from src.ui.utils.bridge import EventScoreChanged, EventGameIdle, EventGameCountdown, EventGameRoundActive, \
    EventGameRoundResult, EventGameOver, EventGestureProgress


class Window(QMainWindow):
    def __init__(self, game_controller: GameController, /, *, show_ai_analytics: bool = False):
        super().__init__()

        self._show_ai_analytics = show_ai_analytics
        self._game_controller = game_controller


        self.setWindowTitle("SINUZ - Kamień Papier Nożyce")
        self.resize(1280, 800)


        self._score_frame = ScoreFrame(self)
        self._camera_frame = CameraFrame(
            show_ai_analytics=self._show_ai_analytics,
        )
        self._build_ui()

        self.setStyleSheet(open("./src/ui/assets/style.qss").read())

    def on_gesture_progress(self, data: EventGestureProgress):
        print("Gesture progress: ", data.progress, "Thumb direction: ", data.thumb_direction)
        self._camera_frame.show_alert(f"Gesture progress: {int(data.progress * 100)}% - {data.thumb_direction.name}", duration=500)

    def on_game_started(self, data: GameState):
        self._score_frame.set_game_started(True)

    def on_game_idle(self, data: EventGameIdle):
        print("Game is idle.", data)

    def on_game_countdown(self, data: EventGameCountdown):
        print("Game countdown: ", data.count_down_time)

    def on_game_round_active(self, data: EventGameRoundActive):
        print("Game round active.", data)

    def on_game_round_result(self, data: EventGameRoundResult):
        print("Game round result.", data)

    def on_game_over(self, data: EventGameOver):
        print("Game over.", data)
        self._score_frame.set_game_started(False)

    def on_score_change(self, data: EventScoreChanged):
        print("Player score: ", data.player_score, "Computer score: ", data.computer_score)
        self._score_frame.update_scores(
            player_score=data.player_score,
            computer_score=data.computer_score,
        )

    def _build_ui(self):
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header = Header(central)
        main = self._build_main()

        root.addWidget(self.header)
        root.addWidget(main, 1)

        self.setCentralWidget(central)


    def _build_main(self) -> QFrame:
        main = QFrame()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)

        main_layout.addStretch(1)
        main_layout.addWidget(self._score_frame)
        main_layout.addStretch(1)
        main_layout.addWidget(self._camera_frame, 0, Qt.AlignmentFlag.AlignHCenter)
        main_layout.addStretch(1)


        return main

    def get_camera_frame(self) -> CameraFrame:
        return self._camera_frame

    def closeEvent(self, event):
        if getattr(self, "_game_controller", None) is not None:
            self._game_controller.close()
        super().closeEvent(event)

    def resizeEvent(self, event):
        if getattr(self, "_camera", None) is not None:
            self._camera_frame.handle_resize()
        super().resizeEvent(event)
