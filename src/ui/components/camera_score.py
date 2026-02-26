from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QGraphicsDropShadowEffect


class CameraScoreOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cameraScoreOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._player_score_label = QLabel("0")
        self._computer_score_label = QLabel("0")
        self._apply_score_shadow(self._player_score_label)
        self._apply_score_shadow(self._computer_score_label)

        overlay_layout = QVBoxLayout(self)
        overlay_layout.setContentsMargins(0, 12, 0, 0)
        overlay_layout.setSpacing(0)
        overlay_layout.setObjectName("scoreOverlay")

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._build_score_bar())
        row.addStretch(1)
        overlay_layout.addLayout(row)
        overlay_layout.addStretch(1)

    def set_scores(self, player_score: int, computer_score: int) -> None:
        self._player_score_label.setText(str(player_score))
        self._computer_score_label.setText(str(computer_score))

    def _build_score_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("scoreBar")
        self._apply_bar_shadow(bar)
        layout = QHBoxLayout(bar)
        layout.setObjectName("scoreBar")
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(16)

        player_pill = self._build_score_pill("Player", self._player_score_label, "playerScore")
        computer_pill = self._build_score_pill("AI", self._computer_score_label, "computerScore")
        layout.addWidget(player_pill)
        layout.addWidget(computer_pill)
        return bar

    @staticmethod
    def _apply_bar_shadow(target: QFrame) -> None:
        shadow = QGraphicsDropShadowEffect(target)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 80))
        target.setGraphicsEffect(shadow)

    @staticmethod
    def _apply_score_shadow(label: QLabel) -> None:
        shadow = QGraphicsDropShadowEffect(label)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 140))
        label.setGraphicsEffect(shadow)

    @staticmethod
    def _build_score_pill(title: str, value_label: QLabel, value_name: str) -> QFrame:
        pill = QFrame()
        pill.setObjectName("scorePill")
        layout = QHBoxLayout(pill)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)
        title_label = QLabel(title)
        title_label.setObjectName("scoreLabel")
        value_label.setObjectName(value_name)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return pill

    def reset_scores(self) -> None:
        self.set_scores(0, 0)
