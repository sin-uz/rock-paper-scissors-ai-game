import sys
import threading

from PySide6.QtWidgets import QApplication

from src.core.game_controller import GameController
from src.ml.gesture_classifier import VectorBasedClassifier
from src.core.round_synchronizer import RoundSynchronizer
from src.core.strategies import ResearchBasedStrategy
from src.ui.utils.bridge import UiBridge
from src.ui.window import Window
from src.util.config import Config


def main():
    config = Config.load_config()

    app = QApplication(sys.argv)
    bridge = UiBridge()

    classifier = VectorBasedClassifier()
    synchronizer = RoundSynchronizer(classifier)
    computer_strategy = ResearchBasedStrategy()

    controller = GameController(
        classifier=classifier,
        synchronizer=synchronizer,
        computer_strategy=computer_strategy,
        bridge=bridge,
        detection_camera_index=config.detection_camera,
        showing_camera_index=config.showing_camera
    )
    game_window = Window(
        controller,
        show_ai_analytics=config.show_ai_analysis,
        mirror_camera=config.mirror_camera
    )

    bridge.event_frame_changed.connect(
        game_window.content_frame.update_camera_frame
    )
    bridge.event_score_changed.connect(
        game_window.on_score_change
    )
    bridge.event_game_over.connect(
        game_window.on_game_over
    )
    bridge.event_game_idle.connect(
        game_window.on_game_idle
    )
    bridge.event_game_countdown.connect(
        game_window.on_game_countdown
    )
    bridge.event_game_round_active.connect(
        game_window.on_game_round_active
    )
    bridge.event_game_round_result.connect(
        game_window.on_game_round_result
    )
    bridge.event_gesture_progress.connect(
        game_window.on_gesture_progress
    )
    bridge.event_game_started.connect(
        game_window.on_game_started
    )

    game_window.show()

    threading.Thread(target=controller.start, daemon=True).start()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
