from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget



class Header(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("header")
            layout = QHBoxLayout(self)
            layout.setContentsMargins(24, 12, 24, 12)
            layout.setSpacing(16)

            center_group = QFrame()
            left_layout = QHBoxLayout(center_group)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(12)

            left_layout.addWidget(self._helper_logo("./src/ui/assets/sinuz.png"))
            left_layout.addWidget(self._helper_logo("./src/ui/assets/issi.png"))
            left_layout.addWidget(self._helper_logo("./src/ui/assets/uz.png"))

            layout.addStretch(1)
            layout.addWidget(center_group)
            layout.addStretch(1)

        @staticmethod
        def _helper_logo(src: str) -> QFrame:
            """
            It's helper function that creates a QFrame containing a logo image. It takes the path to the image as an argument and returns a
            QFrame with the image scaled to a height of 64 pixels.

            :param src: The path to the image file that you want to display as a logo in the header of the application.
            :return: A QFrame containing a QLabel with the logo image scaled to a height of 64 pixels.
            """

            chip = QFrame()
            chip.setObjectName("logo")
            layout = QHBoxLayout(chip)
            layout.setContentsMargins(6, 2, 6, 2)
            label = QLabel()
            pixmap = QPixmap(src)
            if not pixmap.isNull():
                label.setPixmap(pixmap.scaledToHeight(64, Qt.TransformationMode.SmoothTransformation))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return chip

# def build_header() -> QFrame:
#     """
#     It builds the header of the application, which includes the logos of sinuz, uz, issi.
#
#     :return: A QFrame containing the header of the application, which includes the logos of sinuz, uz, issi
#     """
#
#     header = QFrame()
#     header.setObjectName("header")
#     layout = QHBoxLayout(header)
#     layout.setContentsMargins(24, 12, 24, 12)
#     layout.setSpacing(16)
#
#     left_group = QFrame()
#     left_layout = QHBoxLayout(left_group)
#     left_layout.setContentsMargins(0, 0, 0, 0)
#     left_layout.setSpacing(12)
#
#     left_layout.addWidget(__helper_logo("./src/ui/assets/sinuz.png"))
#     left_layout.addWidget(divider())
#     left_layout.addWidget(__helper_logo("./src/ui/assets/issi.png"))
#     left_layout.addWidget(divider())
#     left_layout.addWidget(__helper_logo("./src/ui/assets/uz.png"))
#
#     layout.addStretch(1)
#     layout.addWidget(left_group)
#     layout.addStretch(1)
#
#     return header
#
# def __helper_logo(src: str) -> QFrame:
#     """
#     It's helper function that creates a QFrame containing a logo image. It takes the path to the image as an argument and returns a
#     QFrame with the image scaled to a height of 64 pixels.
#
#     :param src: The path to the image file that you want to display as a logo in the header of the application.
#     :return: A QFrame containing a QLabel with the logo image scaled to a height of 64 pixels.
#     """
#
#     chip = QFrame()
#     chip.setObjectName("logo")
#     layout = QHBoxLayout(chip)
#     layout.setContentsMargins(6, 2, 6, 2)
#     label = QLabel()
#     pixmap = QPixmap(src)
#     if not pixmap.isNull():
#         label.setPixmap(pixmap.scaledToHeight(64, Qt.TransformationMode.SmoothTransformation))
#     label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#     layout.addWidget(label)
#     return chip