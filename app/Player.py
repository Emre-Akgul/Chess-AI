import random
import chess
import numpy as np
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

class Level0ThinkerPlayer(Player):
    def __init__(self, name, color):
        super().__init__(name, color)

        self.piece_values = np.zeros(7, dtype=np.float32)
        self.piece_values[chess.PAWN] = 1.0
        self.piece_values[chess.KNIGHT] = 3.0
        self.piece_values[chess.BISHOP] = 3.0
        self.piece_values[chess.ROOK] = 5.0
        self.piece_values[chess.QUEEN] = 9.0
        self.piece_values[chess.KING] = 0.0  # King's value is set to 0 because it cannot be captured

        # Position tables remain unchanged
        self.pawn_table = np.array([
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            [0.1, 0.1, 0.2, 0.3, 0.3, 0.2, 0.1, 0.1],
            [0.05, 0.05, 0.1, 0.25, 0.25, 0.1, 0.05, 0.05],
            [0.0, 0.0, 0.0, 0.2, 0.2, 0.0, 0.0, 0.0],
            [0.05, -0.05, -0.1, 0.0, 0.0, -0.1, -0.05, 0.05],
            [0.05, 0.1, 0.1, -0.25, -0.25, 0.1, 0.1, 0.05],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ])

        self.knight_table = np.array([
            [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5],
            [-0.4, -0.2, 0.0, 0.0, 0.0, 0.0, -0.2, -0.4],
            [-0.3, 0.0, 0.1, 0.15, 0.15, 0.1, 0.0, -0.3],
            [-0.3, 0.05, 0.15, 0.2, 0.2, 0.15, 0.05, -0.3],
            [-0.3, 0.0, 0.15, 0.2, 0.2, 0.15, 0.0, -0.3],
            [-0.3, 0.05, 0.1, 0.15, 0.15, 0.1, 0.05, -0.3],
            [-0.4, -0.2, 0.0, 0.05, 0.05, 0.0, -0.2, -0.4],
            [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5]
        ])

        self.king_table = np.array([
            [-0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3],
            [-0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3],
            [-0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3],
            [-0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3],
            [-0.2, -0.3, -0.3, -0.4, -0.4, -0.3, -0.3, -0.2],
            [-0.1, -0.2, -0.2, -0.2, -0.2, -0.2, -0.2, -0.1],
            [0.2, 0.2, 0.0, 0.0, 0.0, 0.0, 0.2, 0.2],
            [0.2, 0.3, 0.1, 0.0, 0.0, 0.1, 0.3, 0.2]
        ])

    def evaluate_board(self, board):
        """
        An enhanced evaluation function that considers material balance, 
        checkmate, stalemate, and positional advantages for pawns, knights, and kings.
        Positive score favors white, negative favors black.
        """
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return -float('inf')  # White is checkmated
            else:
                return float('inf')  # Black is checkmated
        
        if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
            return 0  # Draw positions are neutral

        score = 0
        # Instead of iterating over piece_values dict, iterate over piece types directly
        for piece_type in range(1, 7):  # 1=PAWN through 6=KING
            for square in board.pieces(piece_type, chess.WHITE):
                score += self.piece_values[piece_type]
                # Apply position piece matrices for White
                if piece_type == chess.PAWN:
                    row, col = self.square_to_index(square)
                    score += self.pawn_table[row, col]
                elif piece_type == chess.KNIGHT:
                    row, col = self.square_to_index(square)
                    score += self.knight_table[row, col]
                elif piece_type == chess.KING:
                    row, col = self.square_to_index(square)
                    score += self.king_table[row, col]

            for square in board.pieces(piece_type, chess.BLACK):
                score -= self.piece_values[piece_type]
                # Apply position piece matrices for Black (mirror the table)
                if piece_type == chess.PAWN:
                    row, col = self.square_to_index(square)
                    score -= self.pawn_table[7 - row, col]
                elif piece_type == chess.KNIGHT:
                    row, col = self.square_to_index(square)
                    score -= self.knight_table[7 - row, col]
                elif piece_type == chess.KING:
                    row, col = self.square_to_index(square)
                    score -= self.king_table[7 - row, col]

        return score

    def move_sort_key(self, board, move):
        """
        Sorting key function to prioritize moves based on an advanced hierarchical order:
        1. Checks (priority 0)
        2. Favorable captures (using MVV-LVA: Most Valuable Victim - Least Valuable Attacker) scaled to 0-2
        3. Promotions (priority 3)
        4. Threats (moves that attack high-value pieces) (priority 4)
        5. Center control (priority 5)
        6. King safety (priority 6)
        7. Quiet moves (priority 7)
        """
        # Capture attacker and captured pieces BEFORE pushing the move
        attacker_piece = board.piece_at(move.from_square)
        captured_piece = board.piece_at(move.to_square)

        # Priority 1: Checks (moves that put the opponent's king in check)
        board.push(move)
        if board.is_check():
            board.pop()
            return 0

        # Priority 2: Captures with MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
        if captured_piece and attacker_piece:
            attacker_value = self.piece_values[attacker_piece.piece_type]  # Direct array access
            captured_value = self.piece_values[captured_piece.piece_type]  # Direct array access

            # MVV-LVA calculation: prioritize capturing higher-value pieces with lower-value pieces
            mvv_lva_value = captured_value - attacker_value  # Range: [-8, 8]

            # Scale the mvv_lva_value to a range between 0 and 2
            # [-8, 8] -> [0.1, 1.9]
            scaled_value = ((mvv_lva_value + 8) / 16) * (1.9)
            board.pop()
            return 2 - scaled_value


        # Priority 3: Promotions (check if the move is a promotion)
        if move.promotion:
            board.pop()
            return 3  # Promotions have a mid-range priority

        # Priority 4: Threats (moves that attack high-value pieces), scaled to 0-2
        attacked_piece = board.piece_at(move.to_square)
        if attacked_piece:
            attacked_value = self.piece_values[attacker_piece.piece_type] 

            # Scale the attacked piece value to a range between 0 and 2
            # Pawn attack (1) should be lower than a Queen attack (9)
            threat_priority = (attacked_value / 9) * 2  # Max value = 9 (queen), scale to [0, 2]

            board.pop()
            return 5 - threat_priority  # Higher value threats get higher priority

        # Priority 5: Center control (move pieces toward central squares)
        central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        if move.to_square in central_squares:
            board.pop()
            return 5

        # Priority 6: King safety (castling or moving king to a safer square)
        piece_moved = board.piece_at(move.from_square)
        if piece_moved and piece_moved.piece_type == chess.KING:
            if move.to_square in [chess.G1, chess.G8, chess.C1, chess.C8]:
                board.pop()
                return 6

        # Priority 7: Quiet moves (non-capturing, non-checking moves that improve position)
        board.pop()
        return 7
    
    # Convert square to (row, col) in the 8x8 board representation
    def square_to_index(self, square):
        row = 7 - (square // 8)
        col = square % 8
        return row, col

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        """
        Minimax function with alpha-beta pruning and aggressive pruning using
        Principal Variation Search (PVS).
        """
        if depth == 0 or board.is_game_over():
            eval = self.evaluate_board(board)
            return eval

        legal_moves = list(board.legal_moves)
        # Sort moves to ensure better moves (checks, captures, etc.) are evaluated first
        legal_moves.sort(key=lambda move: self.move_sort_key(board, move))

        if is_maximizing:
            max_eval = float('-inf')
            for i, move in enumerate(legal_moves):
                board.push(move)
                
                if i == 0:
                    # Principal variation search (PVS) assumes the first move is the best
                    eval = self.minimax(board, depth - 1, alpha, beta, False)
                else:
                    # Use a smaller search window for subsequent moves (PVS optimization)
                    eval = self.minimax(board, depth - 1, alpha, alpha + 1, False)
                    # If this search fails, perform a normal search
                    if eval > alpha and eval < beta:
                        eval = self.minimax(board, depth - 1, alpha, beta, False)

                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Alpha-beta pruning: cut off further evaluation

            return max_eval

        else:
            min_eval = float('inf')
            for i, move in enumerate(legal_moves):
                board.push(move)
                
                if i == 0:
                    # Principal variation search (PVS) assumes the first move is the best
                    eval = self.minimax(board, depth - 1, alpha, beta, True)
                else:
                    # Use a smaller search window for subsequent moves (PVS optimization)
                    eval = self.minimax(board, depth - 1, beta - 1, beta, True)
                    # If this search fails, perform a normal search
                    if eval > alpha and eval < beta:
                        eval = self.minimax(board, depth - 1, alpha, beta, True)

                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha-beta pruning: cut off further evaluation

            return min_eval



    def make_move(self, board, time):
        """
        Implements a minimax strategy with alpha-beta pruning and move sorting
        at a fixed depth of 3 moves.
        """
        depth = 3  # Fixed depth instead of iterative deepening
        best_move = None
        best_value = float('-inf') if self.color == chess.WHITE else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        equal_moves = []

        legal_moves = list(board.legal_moves)
        # Sort moves based on the defined hierarchy: checks > captures > promotions > other
        legal_moves.sort(key=lambda move: self.move_sort_key(board, move))
        
        for move in legal_moves:
            board.push(move)
            board_value = self.minimax(board, depth - 1, alpha, beta, board.turn == chess.WHITE)
            board.pop()

            if self.color == chess.WHITE:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
                    equal_moves = [move]
                elif board_value == best_value:
                    equal_moves.append(move)
            else:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move
                    equal_moves = [move]
                elif board_value == best_value:
                    equal_moves.append(move)

        # If multiple moves have the same score, pick one randomly
        if equal_moves:
            best_move = random.choice(equal_moves)

        # Print final evaluation
        if self.color == chess.WHITE:
            print(f"Turn of White - Evaluation: {best_value}", flush=True)
        else:
            print(f"Turn of Black - Evaluation: {best_value}", flush=True)

        if best_move:
            board.push(best_move)
            return best_move
        return None  # No legal moves available


