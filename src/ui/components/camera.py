import time

import cv2
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QGraphicsBlurEffect, \
    QStackedLayout

from src.ui.components.camera_score import CameraScoreOverlay
from src.ui.utils.bridge import EventFrameChanged
from src.ui.visualizer import AnnotationsVisualizer


class CameraFrame(QFrame):
    """
    It is a wrapper around QFrame that handles video capture and display.

    :param show_ai_analytics: bool - whether to show AI analytics on the video feed. If True, it will draw the detected hands and FPS on the video feed. It can be useful for debugging.
    """
    def __init__(self,
                 *,
                 show_ai_analytics: bool = False,
                 ):
        super().__init__()

        self._show_ai_analytics = show_ai_analytics
        self._last_frame_ts = None
        self._fps = 0.0

        self._visualizer = AnnotationsVisualizer()

        self._video_label = None
        self._alert_overlay = None
        self._alert_priority = None
        self._blur_effect = None
        self._alert_timer = None
        self._last_pixmap = None
        self._corner_radius = 20
        self._score_overlay = None
        self._video_pixmap_rect = None

        self._configure_frame()
        self._create_video_label()
        self._create_alert_overlay()
        self._create_score_overlay()
        self._create_alert_timer()
        self._build_layout()

    def _configure_frame(self) -> None:
        self.setObjectName("cameraFrame")
        self.setMinimumSize(1152, 648)
        self.setMaximumWidth(1200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 10)
        shadow.setColor(Qt.GlobalColor.black)
        self.setGraphicsEffect(shadow)

    def _create_video_label(self) -> None:
        self._video_label = QLabel("Waiting for camera...", self)
        self._video_label.setObjectName("cameraVideoLabel")
        self._video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def _create_alert_overlay(self) -> None:
        self._alert_overlay = QLabel("", self)
        self._alert_overlay.setObjectName("cameraAlert")
        self._alert_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._alert_overlay.setWordWrap(True)
        self._alert_overlay.hide()

    def _create_score_overlay(self) -> None:
        self._score_overlay = CameraScoreOverlay(self)

    def set_scores(self, player_score: int, computer_score: int) -> None:
        if self._score_overlay is None:
            return
        self._score_overlay.set_scores(player_score, computer_score)

    def _create_alert_timer(self) -> None:
        self._alert_timer = QTimer(self)
        self._alert_timer.setSingleShot(True)
        self._alert_timer.timeout.connect(self._hide_alert)

    def _build_layout(self) -> None:
        layout = QStackedLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        layout.addWidget(self._video_label)
        if self._score_overlay is not None:
            self._score_overlay.raise_()

    def show_alert(self,
                   message: str,
                   *,
                   duration: int = 2000,
                   priority: int = 0,
                   ) -> None:
        """
        It shows an alert message on the video feed for a specified duration.

        :param message: str - the message to be displayed on the video feed.
        :param duration: int - the duration in milliseconds for which the message should be displayed.
        :param priority: int - the priority of the alert. Higher priority alerts will override lower priority ones if they are displayed at the same time.
        :return:
        """
        if self._alert_priority is not None and priority < self._alert_priority:
            return

        self._alert_priority = priority

        if self._blur_effect is None:
            self._blur_effect = QGraphicsBlurEffect(self._video_label)
        self._blur_effect.setBlurRadius(12)
        self._video_label.setGraphicsEffect(self._blur_effect)

        self._alert_overlay.setText(message)
        self._alert_overlay.setGeometry(self._video_label.geometry())
        self._alert_overlay.raise_()
        if self._score_overlay is not None:
            self._score_overlay.raise_()
        self._alert_overlay.show()

        self._alert_timer.start(max(0, int(duration)))

    def update_frame(self, data: EventFrameChanged) -> None:
        """
        It updates the video feed by capturing a frame from the camera, processing it with the game controller,
        and displaying it on the label.
        If AI analytics are enabled, it also draws the analytics on the frame before displaying it.
        It also makes mirror effect on the frame to create a more natural user experience, as if looking into a mirror.

        :param data: EventFrameChanged - the data containing the frame and detected hands to be displayed on the video feed.
        :return:
        """
        mirror_frame = cv2.flip(data.frame, 1)

        if self._show_ai_analytics:
            self._update_fps()
            self._visualizer.draw_analytics(mirror_frame, self._fps, len(data.detected_hands))
            mirror_frame = self._visualizer.render(mirror_frame, data.detected_hands, mirror_display=True)

        rgb_frame = cv2.cvtColor(mirror_frame, cv2.COLOR_BGR2RGB)
        height, width, _ = rgb_frame.shape
        image = QImage(
            rgb_frame.data,
            width,
            height,
            width * 3,
            QImage.Format.Format_RGB888,
        )
        self._set_pixmap(QPixmap.fromImage(image))

    def _set_pixmap(self, pixmap: QPixmap) -> None:
        """
        It sets the pixmap on the label and scales it to fit the label size while keeping the aspect ratio.
        It also stores the last pixmap for later use when resizing the window.

        :return:
        """
        self._last_pixmap = pixmap
        scaled = pixmap.scaled(
            self._video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._video_label.setPixmap(self._rounded_pixmap(scaled))
        self._video_pixmap_rect = self._calculate_pixmap_rect(scaled)
        if self._score_overlay is not None:
            self._sync_score_overlay_geometry()

    def _calculate_pixmap_rect(self, pixmap: QPixmap) -> QRect:
        label_size = self._video_label.size()
        pixmap_size = pixmap.size()
        offset_x = max(0, (label_size.width() - pixmap_size.width()) // 2)
        offset_y = max(0, (label_size.height() - pixmap_size.height()) // 2)
        return QRect(offset_x, offset_y, pixmap_size.width(), pixmap_size.height())

    def _sync_score_overlay_geometry(self) -> None:
        if self._score_overlay is None:
            return
        if self._video_pixmap_rect is not None:
            top_left = self._video_label.mapToParent(self._video_pixmap_rect.topLeft())
            rect = QRect(top_left, self._video_pixmap_rect.size())
            self._score_overlay.setGeometry(rect)
        else:
            self._score_overlay.setGeometry(self._video_label.geometry())
        self._score_overlay.raise_()

    def _rounded_pixmap(self, pixmap: QPixmap) -> QPixmap:
        result = QPixmap(pixmap.size())
        result.fill(Qt.GlobalColor.transparent)

        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        rect = result.rect()
        path.addRoundedRect(rect, self._corner_radius, self._corner_radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return result

    def _hide_alert(self) -> None:
        if self._blur_effect is not None:
            self._video_label.setGraphicsEffect(None)
            self._blur_effect = None
        self._alert_overlay.hide()
        self._alert_priority = None

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

    def handle_resize(self) -> None:
        """
        It handles the resize event of the window by reapplying the last pixmap to the label. This ensures that the video feed is scaled correctly to fit the new size of the label.

        :return:
        """
        if self._last_pixmap is not None:
            self._set_pixmap(self._last_pixmap)
        if self._alert_overlay.isVisible():
            self._alert_overlay.setGeometry(self._video_label.geometry())
        if self._score_overlay is not None:
            self._sync_score_overlay_geometry()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.handle_resize()

    def reset(self):
        self._video_label.setText("Waiting for camera...")
        self._video_label.setPixmap(QPixmap())
        self._last_pixmap = None
        self._video_pixmap_rect = None
        self._hide_alert()
        if self._score_overlay is not None:
            self._score_overlay.reset_scores()