import random
import chess
class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def make_move(self, board, time):
        # This method should be overridden by subclasses
        pass

class RandomPlayer(Player):
    def __init__(self, name, color):
        super().__init__(name, color)

    def make_move(self, board, time):
        # Get a list of all legal moves
        legal_moves = list(board.legal_moves)
        # Choose a random move from the legal moves
        if legal_moves:
            move = random.choice(legal_moves)
            # Make the move on the board
            board.push(move)
            return move
        return None  # No legal moves available