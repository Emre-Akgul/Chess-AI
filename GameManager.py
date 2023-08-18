from HumanPlayer import HumanPlayer
import chess

class GameManager:
    def __init__(self):
        self.board = chess.Board()
        
        self.players = {
            "White": HumanPlayer("Player1", "White"),
            "Black": HumanPlayer("Player2", "Black")
        }
        
        self.current_turn = "White"

    def change_turn(self):
        self.current_turn = "Black" if self.current_turn == "White" else "White"

    
    def is_checkmate(self):
        return self.board.is_checkmate()
    
    def is_stalemate(self):
        return self.board.is_stalemate()

#GameManager().play()