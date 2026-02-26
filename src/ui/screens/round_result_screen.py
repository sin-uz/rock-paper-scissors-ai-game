import numpy as np
from pathlib import Path
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath, QPen, QColor
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QWidget,
)

from src.core.domain import Outcome, Move
from src.ui.screens.screen_base import ScreenBase
from src.ui.utils.bridge import EventGameRoundResult


class RoundResultScreen(ScreenBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("roundResultContent")
        self._player_score = QLabel("0")
        self._computer_score = QLabel("0")
        self._round_title = QLabel("ROUND IN PROGRESS")
        self._round_title.setObjectName("roundTitle")
        self._round_subtitle = QLabel("Waiting for player move...")
        self._round_subtitle.setObjectName("roundSubtitle")
        self._player_move = QLabel("-")
        self._computer_move = QLabel("-")
        self._frame_label = QLabel("Waiting for frame...")
        self._frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._frame_label.setObjectName("roundFrameLabel")
        self._last_pixmap = None
        self._ai_icon = None
        self._frame_corner_radius = 28

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(0)

        # --- Score card + title block (mimics the HTML hero section) ---
        hero = QVBoxLayout()
        hero.setSpacing(0)
        hero.setContentsMargins(0, 0, 0, 20)
        hero.addWidget(self._build_score_card(), 0, Qt.AlignmentFlag.AlignHCenter)
        hero.addSpacing(20)
        hero.addWidget(self._round_title, 0, Qt.AlignmentFlag.AlignHCenter)
        hero.addSpacing(6)
        hero.addWidget(self._round_subtitle, 0, Qt.AlignmentFlag.AlignHCenter)
        root.addLayout(hero)

        # --- Two-panel gameplay area ---
        mid = QHBoxLayout()
        mid.setSpacing(20)

        player_panel = self._build_player_panel()
        ai_panel = self._build_ai_panel()

        mid.addWidget(player_panel, 1)
        mid.addWidget(ai_panel, 1)
        root.addLayout(mid, 1)

    # ------------------------------------------------------------------
    @property
    def camera(self):
        return None

    def reset(self) -> None:
        self._player_score.setText("0")
        self._computer_score.setText("0")
        self._round_title.setText("ROUND IN PROGRESS")
        self._round_title.setObjectName("roundTitle")
        self._round_title.style().unpolish(self._round_title)
        self._round_title.style().polish(self._round_title)
        self._round_subtitle.setText("Waiting for player move...")
        self._player_move.setText("-")
        self._computer_move.setText("-")
        self._frame_label.setText("Waiting for frame...")
        self._frame_label.setPixmap(QPixmap())
        self._last_pixmap = None
        if hasattr(self, "_ai_value"):
            self._ai_value.setText("-")
        if hasattr(self, "_detected_value"):
            self._detected_value.setText("-")
        if self._ai_icon is not None:
            self._ai_icon.setPixmap(QPixmap())
            self._ai_icon.setText("")

    def update_scores(self, player_score: int, computer_score: int) -> None:
        self._player_score.setText(str(player_score))
        self._computer_score.setText(str(computer_score))

    def on_game_round_result(self, data: EventGameRoundResult) -> None:
        if data is None:
            return
        if data.round_record.outcome == Outcome.PLAYER:
            self._round_title.setText("YOU WIN!")
            self._round_title.setObjectName("roundTitleWin")
        elif data.round_record.outcome == Outcome.COMPUTER:
            self._round_title.setText("YOU LOST!")
            self._round_title.setObjectName("roundTitleLose")
        else:
            self._round_title.setText("DRAW!")
            self._round_title.setObjectName("roundTitle")

        # Force style refresh after objectName change
        self._round_title.style().unpolish(self._round_title)
        self._round_title.style().polish(self._round_title)

        self._round_subtitle.setText(
            f"Player wins this round with {data.round_record.player_move.name} vs {data.round_record.computer_move.name}"
            if data.round_record.outcome != Outcome.DRAW
            else f"Both chose {data.round_record.player_move.name}"
        )
        self._player_move.setText(data.round_record.player_move.name)
        self._computer_move.setText(data.round_record.computer_move.name)
        self._ai_value.setText(data.round_record.computer_move.name.upper())
        self._detected_value.setText(data.round_record.player_move.name.upper())
        self._set_ai_icon(data.round_record.computer_move)
        self._update_frame(data.frame, mirror=True)

    # ------------------------------------------------------------------
    def _build_score_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("roundScoreCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(60, 32, 60, 32)
        layout.setSpacing(48)

        layout.addLayout(self._build_score_column("Player", self._player_score, "roundScoreValuePlayer"))

        divider = QFrame()
        divider.setObjectName("roundScoreDivider")
        divider.setFixedWidth(1)
        divider.setMinimumHeight(80)
        layout.addWidget(divider)

        layout.addLayout(self._build_score_column("AI", self._computer_score, "roundScoreValueAi"))
        return card

    def _build_score_column(self, title: str, value_label: QLabel, value_name: str) -> QVBoxLayout:
        column = QVBoxLayout()
        column.setSpacing(4)
        title_label = QLabel(title)
        title_label.setObjectName("roundScoreLabel")
        value_label.setObjectName(value_name)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(title_label, 0, Qt.AlignmentFlag.AlignHCenter)
        column.addWidget(value_label, 0, Qt.AlignmentFlag.AlignHCenter)
        return column

    # ------------------------------------------------------------------
    def _build_player_panel(self) -> "_PlayerPanel":
        panel = _PlayerPanel()
        panel.setObjectName("roundFramePanel")
        panel.setMinimumHeight(420)

        # Base layout: camera frame fills the panel
        base_layout = QVBoxLayout(panel)
        base_layout.setContentsMargins(0, 0, 0, 0)
        self._frame_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        base_layout.addWidget(self._frame_label)

        # Overlay is a direct child of panel (no layout manager owns it),
        # positioned to fill the panel via the panel's resizeEvent.
        overlay = _DashedBorderOverlay(panel)
        overlay.setObjectName("roundFrameOverlay")
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(20, 20, 20, 20)
        overlay_layout.setSpacing(0)

        live_pill = QLabel("PLAYER")
        live_pill.setObjectName("roundLivePill")
        overlay_layout.addWidget(live_pill, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        overlay_layout.addStretch(1)

        # Detected gesture card at bottom
        detected_card = QFrame()
        detected_card.setObjectName("roundDetectedCard")
        detected_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        detected_card.setMinimumHeight(76)
        detected_layout = QHBoxLayout(detected_card)
        detected_layout.setContentsMargins(20, 14, 20, 14)
        detected_layout.setSpacing(16)

        detected_text = QVBoxLayout()
        detected_title = QLabel("Detected Gesture")
        detected_title.setObjectName("roundDetectedTitle")
        self._detected_value = QLabel("-")
        self._detected_value.setObjectName("roundDetectedValue")
        detected_text.addWidget(detected_title)
        detected_text.addWidget(self._detected_value)


        detected_layout.addLayout(detected_text)
        detected_layout.addStretch(1)

        overlay_layout.addWidget(detected_card, 0, Qt.AlignmentFlag.AlignBottom)

        panel.set_overlay(overlay)
        return panel

    # ------------------------------------------------------------------
    def _build_ai_panel(self) -> QFrame:
        ai_panel = QFrame()
        ai_panel.setObjectName("roundAiPanel")
        ai_layout = QVBoxLayout(ai_panel)
        ai_layout.setContentsMargins(32, 32, 32, 32)
        ai_layout.setSpacing(20)
        ai_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # AI decision badge at top (mirrors HTML's absolute top badge)
        ai_badge = QLabel("AI DECISION")
        ai_badge.setObjectName("roundAiBadge")
        ai_layout.addWidget(ai_badge, 0, Qt.AlignmentFlag.AlignLeft)

        # Large double-circle (256 outer / 192 inner like the HTML)
        outer = QFrame()
        outer.setObjectName("roundAiCircleOuter")
        outer.setFixedSize(240, 240)
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(16, 16, 16, 16)

        inner = QFrame()
        inner.setObjectName("roundAiCircleInner")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)

        self._ai_icon = QLabel()
        self._ai_icon.setObjectName("roundAiIcon")
        self._ai_icon.setFixedSize(108, 108)
        self._ai_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(self._ai_icon, 1, Qt.AlignmentFlag.AlignCenter)

        outer_layout.addWidget(inner)

        ai_label = QLabel("AI Chose")
        ai_label.setObjectName("roundAiLabel")
        self._ai_value = QLabel("-")
        self._ai_value.setObjectName("roundAiValue")
        self._ai_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ai_value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        ai_layout.addWidget(outer, 0, Qt.AlignmentFlag.AlignCenter)
        ai_layout.addWidget(ai_label, 0, Qt.AlignmentFlag.AlignCenter)
        ai_layout.addWidget(self._ai_value, 0, Qt.AlignmentFlag.AlignCenter)
        ai_layout.addStretch(1)
        ai_layout.addWidget(self._build_move_row())
        return ai_panel

    # ------------------------------------------------------------------
    def _build_move_row(self) -> QFrame:
        row = QFrame()
        row.setObjectName("moveRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        player_group = self._build_move_group("Player", self._player_move)
        ai_group = self._build_move_group("AI", self._computer_move)
        layout.addWidget(player_group, 1)
        layout.addWidget(ai_group, 1)
        return row

    def _build_move_group(self, title: str, value_label: QLabel) -> QFrame:
        group = QFrame()
        group.setObjectName("moveGroup")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setObjectName("moveTitle")
        value_label.setObjectName("moveValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(value_label, 0, Qt.AlignmentFlag.AlignHCenter)
        return group

    # ------------------------------------------------------------------
    def _update_frame(self, frame, *, mirror: bool = False) -> None:
        if frame is None:
            return
        rgb_frame = frame
        if mirror:
            rgb_frame = rgb_frame[:, ::-1]
        if len(rgb_frame.shape) == 3:
            rgb_frame = rgb_frame[:, :, ::-1]
        rgb_frame = np.ascontiguousarray(rgb_frame)
        height, width, _ = rgb_frame.shape
        image = QImage(
            rgb_frame.data,
            width,
            height,
            width * 3,
            QImage.Format.Format_RGB888,
        )
        self._set_frame_pixmap(QPixmap.fromImage(image))

    def _set_frame_pixmap(self, pixmap: QPixmap) -> None:
        self._last_pixmap = pixmap
        scaled = pixmap.scaled(
            self._frame_label.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._frame_label.setPixmap(self._rounded_pixmap(scaled))

    def _rounded_pixmap(self, pixmap: QPixmap) -> QPixmap:
        result = QPixmap(pixmap.size())
        result.fill(Qt.GlobalColor.transparent)

        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        rect = QRectF(result.rect())
        path.addRoundedRect(rect, self._frame_corner_radius, self._frame_corner_radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return result

    def _set_ai_icon(self, move: Move) -> None:
        if self._ai_icon is None:
            return
        icon_path = self._resolve_move_icon_path(move)
        if icon_path is None:
            self._ai_icon.setPixmap(QPixmap())
            self._ai_icon.setText("?")
            return
        pixmap = QPixmap(str(icon_path))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                self._ai_icon.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._ai_icon.setPixmap(pixmap)
            self._ai_icon.setText("")

    @staticmethod
    def _resolve_move_icon_path(move: Move) -> Path | None:
        asset_map = {
            Move.ROCK: "fist.png",
            Move.PAPER: "open-hand.png",
            Move.SCISSORS: "scissors.png",
        }
        filename = asset_map.get(move)
        if filename is None:
            return None
        assets_dir = Path(__file__).resolve().parents[1] / "assets"
        return assets_dir / filename

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._last_pixmap is not None:
            self._set_frame_pixmap(self._last_pixmap)


# ---------------------------------------------------------------------------
class _PlayerPanel(QFrame):
    """Camera panel that keeps an overlay widget filling its full bounds."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._overlay: QWidget | None = None

    def set_overlay(self, overlay: QWidget) -> None:
        self._overlay = overlay
        self._overlay.setGeometry(self.rect())
        self._overlay.raise_()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._overlay is not None:
            self._overlay.setGeometry(self.rect())
            self._overlay.raise_()


# ---------------------------------------------------------------------------
class _DashedBorderOverlay(QWidget):
    """Transparent overlay that paints a rounded dashed border + holds UI widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(51, 199, 89, 110))
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        margin = 20
        rect = QRectF(
            margin, margin,
            self.width() - 2 * margin,
            self.height() - 2 * margin,
        )
        painter.drawRoundedRect(rect, 20, 20)
        painter.end()


