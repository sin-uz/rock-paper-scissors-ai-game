from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class Bottom(QWidget):
    def __init__(self, parent=None):
        """
        bottom widget that shows copyright information. It is placed at the bottom of the main window and does not change during the game.
        :param parent: It should be the main window, but it is not strictly required. It is used to set the parent of the widget and to inherit the style from the main window.
        """
        super().__init__(parent)
        self.setObjectName("bottom")
        self._copyright_label = QLabel("© 2026 SINUZ (sinuz.issi.uz.zgora.pl)", self)
        self._copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._copyright_label.setObjectName("copyright_label")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._copyright_label)