from PySide6.QtWidgets import QWidget

from src.ui.utils.bridge import EventGameRoundResult


class ScreenBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    @property
    def camera(self):
        raise NotImplementedError

    def update_scores(self, player_score: int, computer_score: int) -> None:
        pass

    def on_game_round_result(self, round_record: EventGameRoundResult) -> None:
        pass

    def update_game_over(self, player_score: int, computer_score: int) -> None:
        pass

    def reset(self) -> None:
        pass
