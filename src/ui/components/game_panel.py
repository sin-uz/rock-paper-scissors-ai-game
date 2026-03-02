from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap, QImage, QPainterPath, QRegion
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget,
)


class _DashedBorderOverlay(QWidget):
    """Transparent overlay that paints a rounded dashed border and holds UI widgets."""

    def __init__(
        self,
        parent=None,
        *,
        border_color: QColor | None = None,
        border_width: int = 2,
        border_margin: int = 20,
        corner_radius: float = 20.0,
    ):
        super().__init__(parent)
        self._border_color = border_color if border_color is not None else QColor(51, 199, 89, 110)
        self._border_width = border_width
        self._border_margin = border_margin
        self._corner_radius = corner_radius

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(self._border_color)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(self._border_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        m = self._border_margin
        rect = QRectF(m, m, self.width() - 2 * m, self.height() - 2 * m)
        painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)
        painter.end()


# ---------------------------------------------------------------------------

class GamePanel(QFrame):
    """Universal panel for both player camera and AI display.

    Handles:
    - Full-bleed content (camera frame or static image) clipped to the panel's
      inner border radius so it never bleeds outside the rounded corners.
    - A transparent dashed-border overlay on top with a pill label and an
      optional detected-gesture card at the bottom.
    - All pixmap scaling and rounded clipping internally — callers just call
      ``set_frame(frame)`` or ``set_pixmap(pixmap)``.

    Args:
        parent:               Parent widget.
        label:                Top-left pill text. Defaults to ``"PLAYER"``.
        pill_color:           Background ``QColor`` of the pill.
        pill_text_color:      Text ``QColor`` of the pill.
        border_color:         ``QColor`` for the dashed overlay border.
        border_width:         Dashed border pen width in pixels. Defaults to 2.
        border_margin:        Gap from panel edge to drawn rect. Defaults to 20.
        corner_radius:        Border-radius of the dashed rect AND the content
                              clip. Should match the QSS ``border-radius`` minus
                              the QSS ``border`` width. Defaults to 30.
        show_detected_card:   Show the bottom detected-gesture card. Defaults to ``True``.
        detected_card_title:  Title text inside the detected card.
    """

    def __init__(
        self,
        parent=None,
        *,
        label: str = "PLAYER",
        pill_color: QColor | None = None,
        pill_text_color: QColor | None = None,
        border_color: QColor | None = None,
        border_width: int = 2,
        border_margin: int = 20,
        corner_radius: float = 30.0,
        show_detected_card: bool = True,
        detected_card_title: str = "Detected Gesture",
    ):
        super().__init__(parent)
        self._corner_radius = corner_radius
        self._last_pixmap: QPixmap | None = None
        self._last_rendered_size: QSize = QSize()  # cache: skip redraw when size unchanged
        self._is_live: bool = False                 # live frames use fast scaling
        self._detected_value: QLabel | None = None
        self._overlay: QWidget | None = None

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(0, 0)

        # ── Content label (fills the whole panel) ─────────────────────
        self._content_label = QLabel()
        self._content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._content_label.setMinimumSize(0, 0)

        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addWidget(self._content_label)

        # ── Overlay ───────────────────────────────────────────────────
        overlay = _DashedBorderOverlay(
            self,
            border_color=border_color,
            border_width=border_width,
            border_margin=border_margin,
            corner_radius=corner_radius,
        )
        overlay.setObjectName("roundFrameOverlay")
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(20, 20, 20, 20)
        overlay_layout.setSpacing(0)

        # ── Pill ──────────────────────────────────────────────────────
        live_pill = QLabel(label)
        live_pill.setObjectName("roundLivePill")
        pill_parts: list[str] = []
        if pill_color is not None:
            r, g, b, a = pill_color.red(), pill_color.green(), pill_color.blue(), pill_color.alpha()
            pill_parts.append(f"background-color: rgba({r},{g},{b},{a});")
        if pill_text_color is not None:
            r, g, b, a = pill_text_color.red(), pill_text_color.green(), pill_text_color.blue(), pill_text_color.alpha()
            pill_parts.append(f"color: rgba({r},{g},{b},{a});")
        if pill_parts:
            live_pill.setStyleSheet(" ".join(pill_parts))

        overlay_layout.addWidget(live_pill, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        overlay_layout.addStretch(1)

        # ── Detected gesture card (optional) ──────────────────────────
        if show_detected_card:
            detected_card = QFrame()
            detected_card.setObjectName("roundDetectedCard")
            detected_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            detected_card.setMinimumHeight(76)
            detected_layout = QHBoxLayout(detected_card)
            detected_layout.setContentsMargins(20, 14, 20, 14)
            detected_layout.setSpacing(16)

            detected_text = QVBoxLayout()
            detected_title_lbl = QLabel(detected_card_title)
            detected_title_lbl.setObjectName("roundDetectedTitle")
            self._detected_value = QLabel("-")
            self._detected_value.setObjectName("roundDetectedValue")
            detected_text.addWidget(detected_title_lbl)
            detected_text.addWidget(self._detected_value)

            detected_layout.addLayout(detected_text)
            detected_layout.addStretch(1)
            overlay_layout.addWidget(detected_card, 0, Qt.AlignmentFlag.AlignBottom)

        self._overlay = overlay
        self._overlay.setGeometry(self.rect())
        self._overlay.raise_()

    # ------------------------------------------------------------------
    # Public API — frame / pixmap
    # ------------------------------------------------------------------

    def set_frame(self, frame, *, mirror: bool = False) -> None:
        """Convert a raw cv2/numpy BGR frame and display it (fast path)."""
        if frame is None:
            return
        # Flip channels BGR→RGB using a view (zero-copy when possible)
        if mirror:
            rgb = np.ascontiguousarray(frame[:, ::-1, ::-1])
        else:
            rgb = np.ascontiguousarray(frame[:, :, ::-1])
        h, w, ch = rgb.shape
        image = QImage(rgb.data, w, h, w * ch, QImage.Format.Format_RGB888)
        # Keep the numpy array alive until QImage is consumed
        image.ndarray = rgb  # type: ignore[attr-defined]
        pixmap = QPixmap.fromImage(image)
        self._last_pixmap = pixmap
        self._is_live = True
        self._last_rendered_size = QSize()  # invalidate cache so frame always renders
        self._apply_pixmap()

    def set_pixmap(self, pixmap: QPixmap) -> None:
        """Display a static ``QPixmap``, scaled and clipped with smooth quality."""
        self._last_pixmap = pixmap
        self._is_live = False
        self._last_rendered_size = QSize()  # invalidate cache
        self._apply_pixmap()

    def clear_pixmap(self) -> None:
        """Remove the current image."""
        self._last_pixmap = None
        self._last_rendered_size = QSize()
        self._content_label.setPixmap(QPixmap())
        self._content_label.setText("")

    def load_asset(self, filename: str) -> bool:
        """Load a static image from the ``assets/`` folder."""
        assets_dir = Path(__file__).resolve().parents[1] / "assets"
        pixmap = QPixmap(str(assets_dir / filename))
        if pixmap.isNull():
            return False
        self.set_pixmap(pixmap)
        return True

    # ------------------------------------------------------------------
    # Public API — detected card
    # ------------------------------------------------------------------

    @property
    def detected_value(self) -> QLabel | None:
        return self._detected_value

    def set_detected_text(self, text: str) -> None:
        if self._detected_value is not None:
            self._detected_value.setText(text)

    def reset_detected(self) -> None:
        if self._detected_value is not None:
            self._detected_value.setText("-")

    # ------------------------------------------------------------------
    # Qt overrides
    # ------------------------------------------------------------------

    def sizeHint(self) -> QSize:
        return QSize(0, 0)

    def minimumSizeHint(self) -> QSize:
        return QSize(0, 0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._overlay is not None:
            self._overlay.setGeometry(self.rect())
            self._overlay.raise_()
        self._last_rendered_size = QSize()  # invalidate cache on resize
        self._apply_pixmap()
        self._update_clip_mask()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_pixmap(self) -> None:
        if self._last_pixmap is None:
            return
        size = self._content_label.size()
        if size.isEmpty():
            return

        # For live frames skip re-render only if size hasn't changed —
        # static assets always re-render (handled by cache invalidation in set_pixmap)
        if self._is_live and size == self._last_rendered_size:
            return
        self._last_rendered_size = size

        # Live frames: fast scaling (no sub-pixel quality needed at 30 fps)
        # Static assets: smooth scaling (loaded once, quality matters)
        transform = (
            Qt.TransformationMode.FastTransformation
            if self._is_live
            else Qt.TransformationMode.SmoothTransformation
        )

        scaled = self._last_pixmap.scaled(
            size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            transform,
        )
        # Crop centre to exact label size
        if scaled.size() != size:
            x = (scaled.width() - size.width()) // 2
            y = (scaled.height() - size.height()) // 2
            scaled = scaled.copy(x, y, size.width(), size.height())

        # Rounded clip — cheap for live frames because the mask on the panel
        # already clips the widget boundary; the per-pixmap clip ensures the
        # QLabel background doesn't show in the corners.
        self._content_label.setPixmap(self._clip_rounded(scaled))

    def _clip_rounded(self, pixmap: QPixmap) -> QPixmap:
        result = QPixmap(pixmap.size())
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(QRectF(result.rect()), self._corner_radius, self._corner_radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return result

    def _update_clip_mask(self) -> None:
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._corner_radius, self._corner_radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

