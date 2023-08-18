from Player import Player
class HumanPlayer(Player):
    def __init__(self, name, color):
        super().__init__(name, color)

    def make_move(self, board):
        move = input(f"{self.name} ({self.color}), enter your move in uci notation (e.g. 'e2e4'): ")
        return move


