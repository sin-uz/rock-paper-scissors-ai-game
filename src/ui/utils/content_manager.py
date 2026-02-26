from PySide6.QtWidgets import QWidget, QStackedLayout

from src.core.domain import RoundRecord
from src.core.game_controller import GameController
from src.ui.components.camera import CameraFrame
from src.ui.screens.game_over_screen import GameOverScreen
from src.ui.screens.round_result_screen import RoundResultScreen
from src.ui.screens.pre_game_screen import PreGameScreen
from src.ui.screens.screen_base import ScreenBase
from src.ui.utils.type_of_screen import TypeOfScreen
from src.ui.utils.bridge import EventFrameChanged, EventGameRoundResult


class ContentManager(QWidget):
    def __init__(self, parent=None, /, show_ai_analytics: bool = False, game_controller: GameController = None):
        """
        Content widget that manages different screens based on the game state.
        It contains a camera frame and dynamic content that changes based on the current screen type.

        :param parent:
        :param show_ai_analytics:
        """
        super().__init__(parent)

        self._show_ai_analytics = show_ai_analytics
        self.setObjectName("content")

        self._camera_frame = CameraFrame(
            show_ai_analytics=self._show_ai_analytics,
        )
        self._game_controller = game_controller

        self._stack = QStackedLayout(self)
        self._stack.setContentsMargins(0, 0, 0, 0)

        before_start_screen = PreGameScreen(self._camera_frame, self)

        self._screens: dict[TypeOfScreen, ScreenBase] = {
            TypeOfScreen.BEFORE_START: before_start_screen,
            TypeOfScreen.DURING_ROUND: before_start_screen,
            TypeOfScreen.RESULT_OF_ROUND: RoundResultScreen(self),
            TypeOfScreen.END_OF_GAME: GameOverScreen(self),
        }

        added = set()
        for screen in self._screens.values():
            if id(screen) in added:
                continue
            self._stack.addWidget(screen)
            added.add(id(screen))

        self._type_of_screen: TypeOfScreen = TypeOfScreen.BEFORE_START
        self._stack.setCurrentWidget(self._screens[self._type_of_screen])


    def update_camera_frame(self, data: EventFrameChanged) -> None:
        screen = self._screens.get(self._type_of_screen)
        if screen is not None and screen.camera is not None:
            screen.camera.update_frame(data)
        else:
            self._camera_frame.update_frame(data)


    @property
    def camera_frame(self) -> CameraFrame:
        return self._camera_frame

    def update_scores(self, player_score: int, computer_score: int) -> None:
        self._camera_frame.set_scores(
            player_score=player_score,
            computer_score=computer_score
        )
        self._screens.get(TypeOfScreen.RESULT_OF_ROUND, ScreenBase()).update_scores(
            player_score=player_score,
            computer_score=computer_score,
        )

    def on_game_round_result(self, data: EventGameRoundResult) -> None:
        screen = self._screens.get(TypeOfScreen.RESULT_OF_ROUND)
        if screen is not None:
            screen.on_game_round_result(data)
        else:
            print("No screen found for round result update.")

    def update_game_over(self, player_score: int, computer_score: int) -> None:
        screen = self._screens.get(TypeOfScreen.END_OF_GAME)
        if screen is not None:
            screen.update_game_over(player_score, computer_score)

    def change_content(self, new_type: TypeOfScreen):
        if self._type_of_screen == new_type:
            return
        self._type_of_screen = new_type
        screen = self._screens[self._type_of_screen]
        if isinstance(screen, PreGameScreen):
            screen.set_helpers_visible(new_type == TypeOfScreen.BEFORE_START)
        self._stack.setCurrentWidget(screen)

    def reset_game(self):
        self._camera_frame.reset()
        self._game_controller.reset()
        self._game_controller.set_stop_detection(False)
        for screen in self._screens.values():
            screen.reset()

        self.change_content(TypeOfScreen.BEFORE_START)