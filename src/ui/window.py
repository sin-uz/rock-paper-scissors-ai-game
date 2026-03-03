import logging
from pathlib import Path

from PySide6.QtWidgets import (

    QVBoxLayout,
    QMainWindow, QWidget,
)

from src.core.domain import ThumbDirection
from src.core.game_state import GameState
from src.ui.components.bottom import Bottom
from src.ui.utils.content_manager import ContentManager
from src.ui.components.header import Header
from src.core.game_controller import GameController
from src.ui.utils.type_of_screen import TypeOfScreen
from src.ui.utils.bridge import EventScoreChanged, EventGameIdle, EventGameCountdown, EventGameRoundActive, \
    EventGameRoundResult, EventGameOver, EventGestureProgress

_ASSETS_DIR = Path(__file__).resolve().parent / "assets"
_logger = logging.getLogger(__name__)


class Window(QMainWindow):
    def __init__(self, game_controller: GameController, /, *, show_ai_analytics: bool = False,
                 mirror_camera: bool = True):
        super().__init__()

        self._show_ai_analytics = show_ai_analytics
        self._mirror_camera = mirror_camera
        self._game_controller = game_controller

        self.setWindowTitle("SINUZ - Kamień Papier Nożyce")
        self.resize(1280, 800)

        self._init_ui()

        with open(_ASSETS_DIR / "style.qss") as f:
            self.setStyleSheet(f.read())

    def _init_ui(self):
        central = QWidget(self)
        root = QVBoxLayout(central)
        central.setObjectName("rootLayout")
        root.setContentsMargins(0, 10, 0, 10)
        root.setSpacing(0)

        self._header = Header(central)
        self._content = ContentManager(
            central,
            show_ai_analytics=self._show_ai_analytics,
            game_controller=self._game_controller,
            mirror_camera=self._mirror_camera,
        )
        self._bottom = Bottom(central)

        # Const (nothing will change) UI elements
        root.addWidget(self._header)

        # Dynamic content (different content will be shown based on the game state)
        root.addWidget(self._content, 1)

        # Const (nothing will change) UI elements
        root.addWidget(self._bottom)

        self.setCentralWidget(central)

    def on_gesture_progress(self, data: EventGestureProgress):
        _logger.debug("Gesture progress: %s  Thumb direction: %s", data.progress, data.thumb_direction)
        if data.thumb_direction == ThumbDirection.UP:
            self._content.camera_frame.show_alert(
                f"Keep your thumb up to start the game! ({int(data.progress * 100)}%)",
                duration=500,
                priority=1
            )
        elif data.thumb_direction == ThumbDirection.DOWN:
            screens = (self._content.screen_during_round, self._content.screen_result_of_round)
            for screen in screens:
                if screen is not None:
                    screen.show_alert(
                        title="Keep your thumb down to end the game!",
                        subtitle=f"{int(data.progress * 100)}%",
                        duration=500,
                        priority=1
                    )

    def on_game_started(self, data: GameState):
        _logger.debug("Game started: %s", data)
        self._content.change_content(TypeOfScreen.DURING_ROUND)

    def on_game_idle(self, data: EventGameIdle):
        _logger.debug("Game is idle: %s", data)
        self._content.change_content(TypeOfScreen.BEFORE_START)

    def on_game_countdown(self, data: EventGameCountdown):
        if data is None or data.count_down_time is None:
            return

        during_round_screen = self._content.screen_during_round
        if during_round_screen is not None:
            during_round_screen.show_alert(
                title=f"Round starts in {data.count_down_time}...",
                subtitle=f"Get ready!",
                duration=1000,
            )

    def on_game_round_active(self, data: EventGameRoundActive):
        _logger.debug("Game round active: %s", data)
        self._content.change_content(TypeOfScreen.DURING_ROUND)

    def on_game_round_result(self, data: EventGameRoundResult):
        _logger.debug("Game round result: %s", data)
        self._content.change_content(TypeOfScreen.RESULT_OF_ROUND)
        self._content.on_game_round_result(data)

    def on_game_over(self, data: EventGameOver):
        _logger.debug("Game over: %s", data)
        self._content.change_content(TypeOfScreen.END_OF_GAME)
        self._content.update_game_over(data.player_score, data.computer_score)
        self._game_controller.set_stop_detection(True)

    def on_score_change(self, data: EventScoreChanged):
        _logger.debug("Player score: %s  Computer score: %s", data.player_score, data.computer_score)
        self._content.update_scores(
            player_score=data.player_score,
            computer_score=data.computer_score,
        )

    @property
    def content_frame(self) -> ContentManager:
        return self._content

    def closeEvent(self, event):
        if getattr(self, "_game_controller", None) is not None:
            self._game_controller.close()
        super().closeEvent(event)
