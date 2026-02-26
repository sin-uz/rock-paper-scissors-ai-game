from PySide6.QtWidgets import (

    QVBoxLayout,
    QMainWindow, QWidget,
)

from src.core.domain import ThumbDirection
from src.core.game_state import GameState
from src.ui.components.bottom import Bottom
from src.ui.components.camera import CameraFrame
from src.ui.utils.content_manager import ContentManager
from src.ui.components.header import Header
from src.core.game_controller import GameController
from src.ui.utils.type_of_screen import TypeOfScreen
from src.ui.utils.bridge import EventScoreChanged, EventGameIdle, EventGameCountdown, EventGameRoundActive, \
    EventGameRoundResult, EventGameOver, EventGestureProgress


class Window(QMainWindow):
    def __init__(self, game_controller: GameController, /, *, show_ai_analytics: bool = False):
        super().__init__()

        self._show_ai_analytics = show_ai_analytics
        self._game_controller = game_controller


        self.setWindowTitle("SINUZ - Kamień Papier Nożyce")
        self.resize(1280, 800)

        self._camera_frame = CameraFrame(
            show_ai_analytics=self._show_ai_analytics,
        )

        self._init_ui()

        self.setStyleSheet(open("./src/ui/assets/style.qss").read())

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
            game_controller=self._game_controller
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
        print("Gesture progress: ", data.progress, "Thumb direction: ", data.thumb_direction)
        if data.thumb_direction == ThumbDirection.UP:
            message = f"Keep your thumb up to start the game! ({int(data.progress * 100)}%)"
        elif data.thumb_direction == ThumbDirection.DOWN:
            message = f"Keep your thumb down to end the game! ({int(data.progress * 100)}%)"
        else:
            message = f"Gesture progress: {int(data.progress * 100)}% - {data.thumb_direction.name}"

        self._content.camera_frame.show_alert(message, duration=500, priority=1)

    def on_game_started(self, data: GameState):
        print("Game started.", data)
        self._content.change_content(TypeOfScreen.DURING_ROUND)

    def on_game_idle(self, data: EventGameIdle):
        print("Game is idle.", data)
        self._content.change_content(TypeOfScreen.BEFORE_START)

    def on_game_countdown(self, data: EventGameCountdown):
        if data is None or data.count_down_time is None:
            return

        print("Game countdown: ", data.count_down_time)
        self._content.change_content(TypeOfScreen.DURING_ROUND)

        self._content.camera_frame.show_alert(f"Round starts in {data.count_down_time}...", duration=1000)

    def on_game_round_active(self, data: EventGameRoundActive):
        print("Game round active.", data)

        self._content.change_content(TypeOfScreen.DURING_ROUND)

    def on_game_round_result(self, data: EventGameRoundResult):
        print("Game round result.", data)
        self._content.change_content(TypeOfScreen.RESULT_OF_ROUND)
        self._content.on_game_round_result(data)

    def on_game_over(self, data: EventGameOver):
        print("Game over.", data)
        self._content.change_content(TypeOfScreen.END_OF_GAME)
        self._content.update_game_over(data.player_score, data.computer_score)
        self._game_controller.set_stop_detection(True)
        # self._score_frame.set_game_started(False)

    def on_score_change(self, data: EventScoreChanged):
        print("Player score: ", data.player_score, "Computer score: ", data.computer_score)
        self._content.update_scores(
            player_score=data.player_score,
            computer_score=data.computer_score,
        )

    @property
    def camera_frame(self) -> CameraFrame:
        return self._camera_frame

    @property
    def content_frame(self) -> ContentManager:
        return self._content

    def closeEvent(self, event):
        if getattr(self, "_game_controller", None) is not None:
            self._game_controller.close()
        super().closeEvent(event)

    def resizeEvent(self, event):
        if getattr(self, "_camera", None) is not None:
            self._camera_frame.handle_resize()
        super().resizeEvent(event)

    def restart_content(self):
        self._init_ui()
