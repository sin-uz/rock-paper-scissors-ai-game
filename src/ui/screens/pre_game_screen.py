from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QVBoxLayout, QGridLayout, QFrame, QHBoxLayout, QLabel
from qt_material_icons import MaterialIcon

from src.ui.components.camera import CameraFrame
from src.ui.screens.screen_base import ScreenBase


class PreGameScreen(ScreenBase):
    def __init__(self,
                 camera_frame: CameraFrame,
                 parent=None,
                 *,
                 is_during_round=False,
                 ) -> None:
        super().__init__(parent)
        self.setObjectName("beforeStartContent")
        self._camera = camera_frame
        self._instruction_bar = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        root.addWidget(self._camera, 1, Qt.AlignmentFlag.AlignHCenter)

        helpers = QGridLayout()
        helpers.setHorizontalSpacing(12)
        helpers.setVerticalSpacing(12)
        self._instruction_bar = self._build_instruction_bar()
        helpers.addWidget(self._instruction_bar, 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        root.addLayout(helpers)
        self.set_helpers_visible(not is_during_round)

    @property
    def camera(self):
        return self._camera

    def reset(self) -> None:
        self._camera.set_scores(0, 0)

    def set_helpers_visible(self, visible: bool) -> None:
        if self._instruction_bar is not None:
            self._instruction_bar.setVisible(visible)

    def update_scores(self, player_score: int, computer_score: int) -> None:
        self._camera.set_scores(player_score, computer_score)

    def _build_instruction_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("instructionBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(24)
        layout.addWidget(self._build_gesture_tile("thumb_up", "Thumbs Up", "To Start The Game", icon_color=QColor("#33c758")))
        layout.addWidget(self._build_gesture_tile("thumb_down", "Thumbs Down", "To Finish The Game", icon_color=QColor("#ff3b30")))
        return bar

    def _build_gesture_tile(self, icon_name: str, title: str, subtitle: str, *, icon_color: QColor) -> QFrame:
        tile = QFrame()
        tile.setObjectName("gestureTile")
        layout = QHBoxLayout(tile)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        icon_box = QFrame()
        icon_box.setObjectName("thumbIconBoxDown" if icon_name == "thumb_down" else "thumbIconBox")
        icon_box.setFixedSize(26, 26)
        icon_box_layout = QHBoxLayout(icon_box)
        icon_box_layout.setContentsMargins(0, 0, 0, 0)
        icon_box_layout.setSpacing(0)
        icon = self._build_icon_label(icon_name, 18, "thumbIcon", icon_color)
        icon_box_layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_box, 0, Qt.AlignmentFlag.AlignVCenter)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        title_label = QLabel(title)
        title_label.setObjectName("gestureTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("gestureSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        layout.addLayout(text_layout)
        return tile

    @staticmethod
    def _build_icon_label(icon_name: str, size: int, object_name: str, icon_color: QColor) -> QLabel:
        label = QLabel()
        label.setObjectName(object_name)
        supported_sizes = (20, 24, 48)
        safe_size = min(supported_sizes, key=lambda s: abs(s - size))
        icon = MaterialIcon(icon_name, style=MaterialIcon.ROUNDED, size=safe_size)
        pixmap = icon.pixmap(safe_size, color=icon_color)
        label.setPixmap(pixmap)
        label.setFixedSize(safe_size, safe_size)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label
