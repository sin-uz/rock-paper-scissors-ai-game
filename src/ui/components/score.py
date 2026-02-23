from PySide6.QtWidgets import QFrame


class ScoreFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("scoreFrame")

    def set_computer_score(self, score: int):
        self.setProperty("computerScore", score)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_player_score(self, score: int):
        self.setProperty("playerScore", score)

    def update_scores(self, player_score: int, computer_score: int):
        self.set_player_score(player_score)

    def set_game_started(self, started: bool):
        self.setProperty("gameStarted", started)
        self.style().unpolish(self)
        self.style().polish(self)

