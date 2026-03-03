import time

import cv2
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QStackedLayout

from src.core.game_controller import GameController
from src.ui.components.camera import CameraFrame
from src.ui.screens.game_over_screen import GameOverScreen
from src.ui.screens.game_screen import GameScreen
from src.ui.screens.pre_game_screen import PreGameScreen
from src.ui.screens.screen_base import ScreenBase
from src.ui.utils.type_of_screen import TypeOfScreen
from src.ui.utils.bridge import EventFrameChanged, EventGameRoundResult, EventGameCountdown
from src.ui.visualizer import AnnotationsVisualizer


class ContentManager(QWidget):
    def __init__(self, parent=None, /, show_ai_analytics: bool = False, game_controller: GameController = None, mirror_camera: bool = True):
        super().__init__(parent)

        self._show_ai_analytics = show_ai_analytics
        self._mirror_camera = mirror_camera
        self.setObjectName("content")

        self._camera_frame = CameraFrame()
        self._visualizer = AnnotationsVisualizer()
        self._last_frame_ts = None
        self._fps = 0.0

        self._game_controller = game_controller
        self._frame_pending: bool = False   # frame-drop guard

        self._stack = QStackedLayout(self)
        self._stack.setContentsMargins(0, 0, 0, 0)

        self._screens: dict[TypeOfScreen, ScreenBase] = {
            TypeOfScreen.BEFORE_START: PreGameScreen(self._camera_frame, self),
            TypeOfScreen.DURING_ROUND: GameScreen(self),
            TypeOfScreen.RESULT_OF_ROUND: GameScreen(self, during_round=False),
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

    def _update_fps(self) -> None:
        """
        It calculates the frames per second (FPS) based on the time difference between the current frame and the last frame. It updates the FPS value and stores the timestamp of the current frame for the next calculation.

        :return:
        """
        now = time.time()
        if self._last_frame_ts is not None:
            delta = now - self._last_frame_ts
            if delta > 0:
                self._fps = 1.0 / delta
        self._last_frame_ts = now

    def update_camera_frame(self, data: EventFrameChanged) -> None:
        # Drop frame if the UI thread is still busy with the previous one
        if self._frame_pending:
            return
        self._frame_pending = True
        try:
            if self._type_of_screen == TypeOfScreen.RESULT_OF_ROUND:
                return
            screen = self._screens.get(self._type_of_screen)
            if screen is not None:
                if self._mirror_camera:
                    data.mirror_frame()

                if self._show_ai_analytics:
                    self._update_fps()
                    self._visualizer.draw_analytics(data.frame, self._fps, len(data.detected_hands))
                    data.frame = self._visualizer.render(data.frame, data.detected_hands, mirror_display=self._mirror_camera)

                screen.update_frame(data.get_pixmap())
        finally:
            self._frame_pending = False


    @property
    def camera_frame(self) -> CameraFrame:
        return self._camera_frame

    @property
    def screen_during_round(self) -> GameScreen | None:
        screen = self._screens.get(TypeOfScreen.DURING_ROUND)
        if screen is not None and isinstance(screen, GameScreen):
            return screen
        return None

    @property
    def screen_result_of_round(self) -> GameScreen | None:
        screen = self._screens.get(TypeOfScreen.RESULT_OF_ROUND)
        if screen is not None and isinstance(screen, GameScreen):
            return screen
        return None

    @property
    def screens(self) -> dict[TypeOfScreen, ScreenBase]:
        return self._screens



    def update_scores(self, player_score: int, computer_score: int) -> None:
        self._camera_frame.set_scores(
            player_score=player_score,
            computer_score=computer_score
        )
        for screen in self._screens.values():
            screen.update_scores(
                player_score=player_score,
                computer_score=computer_score,
            )

    def on_game_round_result(self, data: EventGameRoundResult) -> None:
        screen = self._screens.get(TypeOfScreen.RESULT_OF_ROUND)
        if screen is not None and isinstance(screen, GameScreen):
            if self._mirror_camera:
                data.mirror_frame()
            screen.on_game_round_result(data)
        else:
            print("No screen found for round result update.")

    def update_game_over(self, player_score: int, computer_score: int) -> None:
        screen = self._screens.get(TypeOfScreen.END_OF_GAME)
        if screen is not None and isinstance(screen, GameOverScreen):
            screen.update_game_over(player_score, computer_score)

    def change_content(self, new_type: TypeOfScreen):
        if self._type_of_screen == new_type:
            return
        self._type_of_screen = new_type
        screen = self._screens[self._type_of_screen]
        self._stack.setCurrentWidget(screen)

    def reset_game(self):
        self._camera_frame.reset()
        self._game_controller.reset()
        self._game_controller.set_stop_detection(False)
        for screen in self._screens.values():
            screen.reset()

        self.change_content(TypeOfScreen.BEFORE_START)