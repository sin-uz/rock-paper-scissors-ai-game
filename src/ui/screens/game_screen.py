from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QFrame,
)

from src.core.domain import Outcome, Move
from src.ui.components.game_panel import GamePanel
from src.ui.screens.screen_base import ScreenBase
from src.ui.utils.bridge import EventGameRoundResult, EventFrameChanged


class GameScreen(ScreenBase):
    def __init__(self,
                 parent=None,
                 /,
                 during_round: bool = True,
                 ):
        super().__init__(parent)
        self.setObjectName("roundResultContent")
        self._player_score = QLabel("0")
        self._computer_score = QLabel("0")
        self._round_title = QLabel("ROUND IN PROGRESS")
        self._round_title.setObjectName("roundTitle")
        self._round_subtitle = QLabel("Waiting for player move...")
        self._round_subtitle.setObjectName("roundSubtitle")

        self._player_panel: GamePanel | None = None
        self._ai_panel: GamePanel | None = None
        self._ai_has_result: bool = False
        self._ai_thinking_shown: bool = False
        self._during_round: bool = during_round

        self._round_title_before_alert = self._round_title.text()
        self._round_title_object_name_before_alert = self._round_title.objectName()
        self._round_subtitle_before_alert = self._round_subtitle.text()

        self._alert_priority = None
        self._alert_timer = QTimer(self)
        self._alert_timer.setSingleShot(True)
        self._alert_timer.timeout.connect(self._clear_alert)


        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(0)
        root.setSizeConstraint(QVBoxLayout.SizeConstraint.SetNoConstraint)

        # --- Score card + title block ---
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
        mid.setSizeConstraint(QHBoxLayout.SizeConstraint.SetNoConstraint)

        self._player_panel = self._build_player_panel()
        self._ai_panel = self._build_ai_panel()

        mid.addWidget(self._player_panel, 1)
        mid.addWidget(self._ai_panel, 1)
        root.addLayout(mid, 1)


    def set_round_title(self, title: str) -> None:
        self._round_title.setText(title)
        self._round_title.style().unpolish(self._round_title)
        self._round_title.style().polish(self._round_title)

    def set_round_subtitle(self, subtitle: str) -> None:
        self._round_subtitle.setText(subtitle)
        self._round_subtitle.style().unpolish(self._round_subtitle)
        self._round_subtitle.style().polish(self._round_subtitle)

    def show_alert(self, title: str, subtitle: str = "", duration: int = 2000, priority: int = 0) -> None:
        if self._alert_priority is not None and priority < self._alert_priority:
            return

        self._alert_priority = priority
        self._save_current_title_and_subtitle()

        self._round_title.setText(title)
        self._round_title.setObjectName("roundTitleAlert")
        self._round_subtitle.setText(subtitle)

        self._round_title.style().unpolish(self._round_title)
        self._round_title.style().polish(self._round_title)
        self._round_subtitle.style().unpolish(self._round_subtitle)
        self._round_subtitle.style().polish(self._round_subtitle)

        self._alert_timer.start(max(0, int(duration)))

    def update_frame(self, image: QPixmap) -> None:
        if self._player_panel is not None:
            self._player_panel.set_frame(image)
        if self._ai_panel is not None and not self._ai_has_result and not self._ai_thinking_shown:
            self._set_ai_thinking()

    def sizeHint(self) -> QSize:
        return QSize(0, 0)

    def minimumSizeHint(self) -> QSize:
        return QSize(0, 0)

    def reset(self) -> None:
        self._ai_has_result = False
        self._ai_thinking_shown = False
        self._player_score.setText("0")
        self._computer_score.setText("0")
        self._round_title.setText("ROUND IN PROGRESS")
        self._round_title.setObjectName("roundTitle")
        self._round_title.style().unpolish(self._round_title)
        self._round_title.style().polish(self._round_title)
        self._round_subtitle.setText("Waiting for player move...")
        if self._player_panel is not None:
            self._player_panel.clear_pixmap()
            self._player_panel.reset_detected()
        if self._ai_panel is not None:
            self._ai_panel.reset_detected()
            self._set_ai_thinking()

    def update_scores(self, player_score: int, computer_score: int) -> None:
        self._player_score.setText(str(player_score))
        self._computer_score.setText(str(computer_score))

    def on_game_round_result(self, data: EventGameRoundResult) -> None:
        if data is None:
            return
        self._ai_has_result = True

        if data.round_record.outcome == Outcome.PLAYER:
            self._round_title.setText("YOU WIN!")
            self._round_title.setObjectName("roundTitleWin")
        elif data.round_record.outcome == Outcome.COMPUTER:
            self._round_title.setText("YOU LOST!")
            self._round_title.setObjectName("roundTitleLose")
        else:
            self._round_title.setText("DRAW!")
            self._round_title.setObjectName("roundTitle")

        self._round_title.style().unpolish(self._round_title)
        self._round_title.style().polish(self._round_title)

        self._round_subtitle.setText(
            f"Player wins this round with {data.round_record.player_move.name} vs {data.round_record.computer_move.name}"
            if data.round_record.outcome != Outcome.DRAW
            else f"Both chose {data.round_record.player_move.name}"
        )

        if self._ai_panel is not None:
            self._ai_panel.set_detected_text(data.round_record.computer_move.name.upper())
            self._set_ai_move_icon(data.round_record.computer_move)
        if self._player_panel is not None:
            self._player_panel.set_detected_text(data.round_record.player_move.name.upper())
            self._player_panel.set_frame(data.get_pixmap())

    # ------------------------------------------------------------------
    def _save_current_title_and_subtitle(self) -> None:
        if self._round_title.objectName() == "roundTitleAlert":
            return
        self._round_title_before_alert = self._round_title.text()
        self._round_title_object_name_before_alert = self._round_title.objectName()
        self._round_subtitle_before_alert = self._round_subtitle.text()

    def _clear_alert(self):
        self._alert_priority = None
        self._round_title.setText(self._round_title_before_alert)
        self._round_title.setObjectName(self._round_title_object_name_before_alert)
        self._round_subtitle.setText(self._round_subtitle_before_alert)
        self._round_title.style().unpolish(self._round_title)
        self._round_title.style().polish(self._round_title)
        self._round_subtitle.style().unpolish(self._round_subtitle)
        self._round_subtitle.style().polish(self._round_subtitle)

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

    @staticmethod
    def _build_score_column(title: str, value_label: QLabel, value_name: str) -> QVBoxLayout:
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
    def _build_player_panel(self) -> GamePanel:
        panel = GamePanel(
            label="PLAYER",
            border_color=QColor(51, 199, 89, 110),
            border_width=2,
            border_margin=20,
            corner_radius=30.0,
            show_detected_card=not self._during_round,
            detected_card_title="Detected Gesture",
        )
        panel.setObjectName("roundFramePanel")
        return panel

    def _build_ai_panel(self) -> GamePanel:
        panel = GamePanel(
            label="AI",
            pill_color=QColor(255, 59, 48, 255),
            border_color=QColor(255, 59, 48, 110),
            border_width=2,
            border_margin=20,
            corner_radius=30.0,
            show_detected_card=not self._during_round,
            detected_card_title="AI Chose",
        )
        panel.setObjectName("roundAiPanel")
        return panel

    # ------------------------------------------------------------------
    def _set_ai_thinking(self) -> None:
        if self._ai_panel is not None:
            self._ai_panel.load_asset("ai_thinking.png")
            self._ai_thinking_shown = True

    def _set_ai_move_icon(self, move: Move) -> None:
        asset_map = {
            Move.ROCK: "ai_rock.png",
            Move.PAPER: "ai_paper.png",
            Move.SCISSORS: "ai_scissors.png",
        }
        filename = asset_map.get(move)
        if filename and self._ai_panel is not None:
            self._ai_panel.load_asset(filename)
