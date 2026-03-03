import cv2
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget

from src.ui.utils.bridge import EventFrameChanged


class ScreenBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def update_scores(self, player_score: int, computer_score: int) -> None:
        pass

    def update_frame(self, image: QPixmap) -> None:
        pass

    def reset(self) -> None:
        pass
