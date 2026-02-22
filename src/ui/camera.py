import time

import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QPainter, QPainterPath
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QSizePolicy

from src.core.game_controller import GameController
from src.ui.visualizer import AnnotationsVisualizer


class CameraFrame:
    """
    It is a wrapper around QFrame that handles video capture and display.
    """
    def __init__(self,
                 frame: QFrame,
                 game_controller: GameController,
                 *,
                 show_ai_analytics: bool = False,
                 camera_index: int = 0,
                 ):
        self._show_ai_analytics = show_ai_analytics
        self._frame = frame
        self._camera_index = camera_index
        self._last_frame_ts = None
        self._fps = 0.0
        self._cap = None

        self._controller = game_controller
        self._visualizer = AnnotationsVisualizer()

        self._timer = QTimer(self._frame)
        self._timer.timeout.connect(self._update_frame)

        self._video_label = QLabel("Waiting for camera...", self._frame)
        self._video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_label.setStyleSheet("color: rgba(248, 250, 252, 0.6);")
        self._video_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QVBoxLayout(self._frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._video_label)

        self._last_pixmap = None
        self._corner_radius = 20



    def start(self) -> None:
        """
        It starts the video capture and updates the video feed every 33ms (30 FPS). If the camera is not available, it shows an error message.

        :return:
        """
        if self._cap is not None:
            return
        self._cap = cv2.VideoCapture(self._camera_index)
        if not self._cap.isOpened():
            self._video_label.setText("Kamera jest niedostępna")
            self._cap = None
            return
        self._timer.start(33)


    def stop(self) -> None:
        """
        It stops the video capture and releases the camera resource. It also closes the hand detector to free up any resources it may be using.

        :return:
        """
        if self._timer.isActive():
            self._timer.stop()
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self._controller.close_detector()


    def _update_frame(self) -> None:
        """
        It updates the video feed by capturing a frame from the camera, processing it with the game controller, and displaying it on the label.
        If AI analytics are enabled, it also draws the analytics on the frame before displaying it.

        :return:
        """
        if self._cap is None:
            return
        ok, frame = self._cap.read()
        if not ok:
            self._video_label.setText("Kamera jest niedostępna")
            return

        frame = cv2.flip(frame, 1)

        detected_hands = self._controller.process_frame(frame)

        if self._show_ai_analytics:
            self._update_fps()
            self._visualizer.draw_analytics(frame, self._fps, len(detected_hands))
            frame = self._visualizer.render(frame, detected_hands, mirror_display=False)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
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
