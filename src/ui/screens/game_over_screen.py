from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QSizePolicy, QWidget,
)
from qt_material_icons import MaterialIcon
from pathlib import Path

from src.ui.screens.screen_base import ScreenBase

_ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"


def _icon_label(name: str, color: str, icon_size: int = 48) -> QLabel:
    """Return a QLabel showing a Material icon pixmap tinted with *color*.
    Always loads size=48 (the only pre-built resource) and scales to icon_size."""
    lbl = QLabel()
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon = MaterialIcon(name, size=48)
    px = icon.pixmap(QSize(48, 48), color=QColor(color))
    if icon_size != 48:
        px = px.scaled(
            QSize(icon_size, icon_size),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    lbl.setPixmap(px)
    lbl.setFixedSize(icon_size, icon_size)
    return lbl


class GameOverScreen(ScreenBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._parent = parent

        self.setObjectName("endGameContent")

        self._player_score = QLabel("0")
        self._computer_score = QLabel("0")
        self._title = QLabel("Match Complete")
        self._subtitle = QLabel("Review the final score below.")

        # Performance summary dynamic labels
        self._perf_wins_label = QLabel()
        self._perf_losses_label = QLabel()
        self._total_score_label = QLabel()

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(24)

        # ── Title block ───────────────────────────────────────────────
        self._title.setObjectName("endTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle.setObjectName("endSubtitle")
        self._subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._title)
        root.addWidget(self._subtitle)

        # ── Main 2-col content ────────────────────────────────────────
        cols = QHBoxLayout()
        cols.setSpacing(20)
        cols.addWidget(self._build_score_panel(), 2)
        cols.addWidget(self._build_leaderboard_panel(), 1)
        root.addLayout(cols, 1)

        # ── Action buttons ────────────────────────────────────────────
        root.addLayout(self._build_actions())

    # ------------------------------------------------------------------
    @property
    def camera(self):
        return None

    def reset(self) -> None:
        self._player_score.setText("0")
        self._computer_score.setText("0")
        self._title.setText("Match Complete")
        self._title.setObjectName("endTitle")
        self._title.style().unpolish(self._title)
        self._title.style().polish(self._title)
        self._subtitle.setText("Review the final score below.")
        self._perf_wins_label.setText("0 Wins × 10 = 0")
        self._perf_losses_label.setText("0 Losses × 5 = -0")
        self._total_score_label.setText(
            "<span style='font-size:28px;font-weight:900;color:#0f172a;'>0</span>"
            "<span style='font-size:13px;color:#94a3b8;font-weight:600;'> pts</span>"
        )
        if hasattr(self, "_name_input"):
            self._name_input.clear()

    def update_game_over(self, player_score: int, computer_score: int) -> None:
        self._player_score.setText(str(player_score))
        self._computer_score.setText(str(computer_score))

        wins = player_score
        losses = computer_score
        total = wins * 10 - losses * 5

        if player_score > computer_score:
            self._title.setText("Victory!")
            self._title.setObjectName("endTitleWin")
            self._subtitle.setText("You outperformed the neural network.")
        elif player_score < computer_score:
            self._title.setText("Defeat")
            self._title.setObjectName("endTitleLose")
            self._subtitle.setText("The AI won this match.")
        else:
            self._title.setText("Draw")
            self._title.setObjectName("endTitle")
            self._subtitle.setText("A balanced match with no winner.")

        self._title.style().unpolish(self._title)
        self._title.style().polish(self._title)

        self._perf_wins_label.setText(
            f"<span style='color:#34c759;font-weight:700;'>{wins}</span> "
            f"Wins × 10 = <span style='color:#34c759;font-weight:700;'>{wins * 10}</span>"
        )
        self._perf_losses_label.setText(
            f"<span style='color:#ff3b30;font-weight:700;'>{losses}</span> "
            f"Losses × 5 = <span style='color:#ff3b30;font-weight:700;'>-{losses * 5}</span>"
        )
        self._total_score_label.setText(
            f"<span style='font-size:28px;font-weight:900;color:#0f172a;'>{total}</span>"
            f"<span style='font-size:13px;color:#94a3b8;font-weight:600;'> pts</span>"
        )

    # ------------------------------------------------------------------
    def _build_score_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("endScorePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)

        # Player vs AI circles row
        layout.addLayout(self._build_vs_row())
        layout.addSpacing(24)

        # Performance summary card
        layout.addWidget(self._build_perf_summary())
        layout.addSpacing(24)

        # Admin record / name input
        layout.addWidget(self._build_admin_record())

        return panel

    def _build_vs_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(0)
        row.addStretch(1)
        row.addWidget(self._build_player_column())
        row.addStretch(1)
        row.addWidget(self._build_vs_divider())
        row.addStretch(1)
        row.addWidget(self._build_ai_column())
        row.addStretch(1)
        return row

    def _build_player_column(self) -> QWidget:
        col = QWidget()
        col.setObjectName("endPlayerCol")
        col.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(col)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        wrapper, w = self._build_circle_with_badge(
            "endPlayerCircle", "person", "#33c758", "+10 pts/win", "endBadgeGreen"
        )
        layout.addWidget(wrapper, 0, Qt.AlignmentFlag.AlignHCenter)

        label = QLabel("PLAYER")
        label.setObjectName("endPlayerLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(w)
        self._player_score.setObjectName("endPlayerScore")
        self._player_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._player_score.setFixedWidth(w)

        layout.addWidget(label)
        layout.addWidget(self._player_score)
        return col

    def _build_ai_column(self) -> QWidget:
        col = QWidget()
        col.setObjectName("endAiCol")
        col.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(col)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        wrapper, w = self._build_circle_with_badge(
            "endAiCircle", "smart_toy", "#ff3b30", "-5 pts/loss", "endBadgeRed"
        )
        layout.addWidget(wrapper, 0, Qt.AlignmentFlag.AlignHCenter)

        label = QLabel("AI ROBOT")
        label.setObjectName("endAiLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedWidth(w)
        self._computer_score.setObjectName("endAiScore")
        self._computer_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._computer_score.setFixedWidth(w)

        layout.addWidget(label)
        layout.addWidget(self._computer_score)
        return col

    def _build_circle_with_badge(
        self,
        circle_name: str,
        icon_name: str,
        icon_color: str,
        badge_text: str,
        badge_name: str,
    ) -> tuple:
        """Circle icon with a pill badge overlapping its top-right corner.
        The wrapper is wide enough to fully contain the badge so nothing is
        clipped. The circle is horizontally centred inside the wrapper so the
        whole widget centres correctly under the 'PLAYER' / 'AI ROBOT' labels
        (which are given the same fixed width as the wrapper)."""
        CIRCLE = 112   # circle diameter
        BADGE_H = 22   # badge height
        BADGE_W = 90   # wide enough for any badge text at 9px bold
        OFFSET = 10    # extra height at top for badge vertical overflow
        # Badge right-edge overhangs the circle by half its width
        OVERHANG = BADGE_W // 2  # 45 px to the right of circle centre
        WRAPPER_W = CIRCLE + OVERHANG  # 157 px — badge fully inside

        wrapper = QWidget()
        wrapper.setFixedSize(WRAPPER_W, CIRCLE + OFFSET)

        # Circle starts at x = (WRAPPER_W - CIRCLE) // 2 = ~22 px so it is
        # horizontally centred inside the wider wrapper.
        cx = (WRAPPER_W - CIRCLE) // 2
        circle = QFrame(wrapper)
        circle.setObjectName(circle_name)
        circle.setGeometry(cx, OFFSET, CIRCLE, CIRCLE)

        icon_lbl = _icon_label(icon_name, icon_color, 52)
        icon_lbl.setParent(circle)
        icon_lbl.setGeometry((CIRCLE - 52) // 2, (CIRCLE - 52) // 2, 52, 52)

        # Badge: right-aligned to the right edge of the wrapper, top of wrapper
        badge = QLabel(badge_text, wrapper)
        badge.setObjectName(badge_name)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setGeometry(WRAPPER_W - BADGE_W, 0, BADGE_W, BADGE_H)

        return wrapper, WRAPPER_W  # return width so columns can match labels

    def _build_vs_divider(self) -> QLabel:
        vs = QLabel("vs")
        vs.setObjectName("endVsLabel")
        vs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return vs

    def _build_perf_summary(self) -> QFrame:
        card = QFrame()
        card.setObjectName("endPerfCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Left: title + win/loss rows
        left = QVBoxLayout()
        left.setSpacing(8)
        title = QLabel("Performance Summary")
        title.setObjectName("endPerfTitle")
        left.addWidget(title)

        self._perf_wins_label.setObjectName("endPerfRow")
        self._perf_wins_label.setTextFormat(Qt.TextFormat.RichText)
        self._perf_wins_label.setText("0 Wins × 10 = 0")

        self._perf_losses_label.setObjectName("endPerfRow")
        self._perf_losses_label.setTextFormat(Qt.TextFormat.RichText)
        self._perf_losses_label.setText("0 Losses × 5 = -0")

        left.addWidget(self._perf_wins_label)
        left.addWidget(self._perf_losses_label)

        # Right: total score box
        total_box = QFrame()
        total_box.setObjectName("endTotalBox")
        total_layout = QVBoxLayout(total_box)
        total_layout.setContentsMargins(20, 12, 20, 12)
        total_layout.setSpacing(2)
        total_lbl = QLabel("Total Score")
        total_lbl.setObjectName("endTotalLabel")
        self._total_score_label.setObjectName("endTotalValue")
        self._total_score_label.setTextFormat(Qt.TextFormat.RichText)
        self._total_score_label.setText("<span style='font-size:28px;font-weight:900;color:#0f172a;'>0</span><span style='font-size:13px;color:#94a3b8;font-weight:600;'> pts</span>")
        total_layout.addWidget(total_lbl)
        total_layout.addWidget(self._total_score_label)

        layout.addLayout(left, 1)
        layout.addWidget(total_box, 0, Qt.AlignmentFlag.AlignVCenter)
        return card

    def _build_admin_record(self) -> QFrame:
        section = QFrame()
        section.setObjectName("endAdminSection")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(10)

        lbl = QLabel("Your nickname")
        lbl.setObjectName("endAdminLabel")
        layout.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(12)

        self._name_input = QLineEdit()
        self._name_input.setObjectName("endNameInput")
        self._name_input.setPlaceholderText("Enter your name")
        self._name_input.setFixedHeight(52)

        save_btn = QPushButton("Save Score")
        save_btn.setObjectName("endSaveButton")
        save_btn.setFixedHeight(52)

        # Add chevron icon to save button
        save_icon = MaterialIcon("chevron_right", size=48)
        save_btn.setIcon(save_icon)
        save_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        row.addWidget(self._name_input, 1)
        row.addWidget(save_btn)
        layout.addLayout(row)
        return section

    def _build_leaderboard_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("endLeaderboardPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(32, 40, 32, 40)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Leaderboard")
        title.setObjectName("endLeaderTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Scan to view your global ranking")
        subtitle.setObjectName("endLeaderSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # QR code image box
        qr_box = QFrame()
        qr_box.setObjectName("endQrBox")
        qr_box.setFixedSize(200, 200)
        qr_layout = QVBoxLayout(qr_box)
        qr_layout.setContentsMargins(12, 12, 12, 12)

        qr_image = QLabel()
        qr_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_pixmap = QPixmap(str(_ASSETS_DIR / "qr_code.png"))
        if not qr_pixmap.isNull():
            qr_pixmap = qr_pixmap.scaled(
                QSize(176, 176),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            qr_image.setPixmap(qr_pixmap)
        else:
            qr_image.setText("QR")
        qr_layout.addWidget(qr_image, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(qr_box, 0, Qt.AlignmentFlag.AlignCenter)

        # Scan pill
        scan_pill = QFrame()
        scan_pill.setObjectName("endScanPill")
        scan_layout = QHBoxLayout(scan_pill)
        scan_layout.setContentsMargins(16, 8, 16, 8)
        scan_layout.setSpacing(8)

        scan_icon = _icon_label("qr_code_scanner", "#33c758", 20)
        scan_text = QLabel("SCAN NOW")
        scan_text.setObjectName("endScanText")

        scan_layout.addWidget(scan_icon)
        scan_layout.addWidget(scan_text)
        layout.addWidget(scan_pill, 0, Qt.AlignmentFlag.AlignCenter)

        return panel

    def _build_actions(self) -> QHBoxLayout:
        actions = QHBoxLayout()
        actions.setSpacing(16)
        actions.addStretch(1)

        play_again = QPushButton("Restart game")
        play_again.setObjectName("primaryButton")
        play_again.clicked.connect(self._parent.reset_game)
        play_again.setFixedHeight(52)
        play_again.setMinimumWidth(200)

        actions.addWidget(play_again)
        actions.addStretch(1)
        return actions
