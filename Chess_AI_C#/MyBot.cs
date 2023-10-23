using System;
using System.Linq;
using System.Numerics;
using System.Runtime.InteropServices;
using ChessChallenge.API;

public class MyBot : IChessBot{  

    public Move Think(Board board, Timer timer)
    {
        bool isMaximizing = board.IsWhiteToMove;
        Move[] legalMoves = board.GetLegalMoves();
        // Sort the moves
        Array.Sort(legalMoves, CompareMoves);

        Move bestMove = Move.NullMove;
        int bestValue = isMaximizing ? int.MinValue : int.MaxValue;

        // Define a maximum depth based on your needs, or adjust it based on the timer.
        int maxDepth = 5;
        
        for (int depth = 1; depth <= maxDepth; depth++)
        {
            int alpha = int.MinValue;
            int beta = int.MaxValue;

            for (int i = 0; i < legalMoves.Length; i++)
            {
                board.MakeMove(legalMoves[i]);
                int moveValue = Minimax(board, depth - 1, !isMaximizing, alpha, beta);
                board.UndoMove(legalMoves[i]);

                if (isMaximizing && moveValue > bestValue)
                {
                    bestValue = moveValue;
                    bestMove = legalMoves[i];
                }
                else if (!isMaximizing && moveValue < bestValue)
                {
                    bestValue = moveValue;
                    bestMove = legalMoves[i];
                }

                // Alpha-Beta Pruning
                if (isMaximizing)
                {
                    alpha = Math.Max(alpha, bestValue);
                }
                else
                {
                    beta = Math.Min(beta, bestValue);
                }

                // If beta <= alpha, break out of the loop.
                if (beta <= alpha)
                {
                    break;
                }
            }
        }

        return bestMove;
    }

        private const int None = 0;
        private const int PAWN_SCORE = 100;
        private const int KNIGHT_SCORE = 300;
        private const int BISHOP_SCORE = 320;
        private const int ROOK_SCORE = 500;
        private const int QUEEN_SCORE = 900;
        private const int KING_SCORE = 100000;

        private int[] pieceScores = new int[]
        {
            None, PAWN_SCORE, KNIGHT_SCORE, BISHOP_SCORE, ROOK_SCORE, QUEEN_SCORE, KING_SCORE
        };

        public int CompareMoves(Move move1, Move move2)
        {
            // Compare PromotionPieceType
            int comparison = move2.PromotionPieceType.CompareTo(move1.PromotionPieceType);
            if (comparison != 0) return comparison;

            // MVV-LVA heuristic for captures
            if (move1.CapturePieceType != PieceType.None && move2.CapturePieceType != PieceType.None)
            {
                int move1Value = pieceScores[(int)move1.CapturePieceType] - pieceScores[(int)move1.MovePieceType];
                int move2Value = pieceScores[(int)move2.CapturePieceType] - pieceScores[(int)move2.MovePieceType];
                comparison = move2Value.CompareTo(move1Value);
                if (comparison != 0) return comparison;
            }
            else if (move1.CapturePieceType != PieceType.None) // Only move1 is a capture
            {
                return -1;
            }
            else if (move2.CapturePieceType != PieceType.None) // Only move2 is a capture
            {
                return 1;
            }

            // Compare MovePieceType
            return move2.MovePieceType.CompareTo(move1.MovePieceType);
        }


        private int Minimax(Board board, int depth, bool isMaximizing, int alpha, int beta){   
            if (board.IsDraw()){
                return 0;
            }else if(board.IsInCheckmate()){
                return isMaximizing ? int.MinValue : int.MaxValue;
            }

            if (depth == 0)
            {
                return EvaluateBoard(board);
            }

            int bestValue = isMaximizing ? int.MinValue : int.MaxValue;
            Move[] legalMoves = board.GetLegalMoves();
            Array.Sort(legalMoves, CompareMoves);

            Move bestMove = Move.NullMove;
            int bestEval = isMaximizing ? int.MinValue : int.MaxValue;
            foreach (Move move in legalMoves)
            {   
                board.MakeMove(move);
                int value = Minimax(board, depth - 1, !isMaximizing, alpha, beta);
                board.UndoMove(move);

                if(isMaximizing){
                    bestValue = Math.Max(bestValue, value);
                    alpha = Math.Max(alpha,bestValue);
                }else{
                    bestValue = Math.Min(bestValue,value);
                    beta = Math.Min(bestValue,value);
                }

                if(beta < alpha){
                    break;
                }
            }
            return bestValue;
        }      
        private int EvaluateBoard(Board board)
        {
            int score = 0;

            int whiteBishops = 0, blackBishops = 0;
            int whitePawns = 0, blackPawns = 0;

            foreach (var pieceList in board.GetAllPieceLists())
            {
                for (int pieceIndex = 0; pieceIndex < pieceList.Count; pieceIndex++)
                {
                    var piece = pieceList[pieceIndex];
                    var pieceSquare = piece.Square;
                    var attacks = BitboardHelper.GetPieceAttacks(piece.PieceType, pieceSquare, board, pieceList.IsWhitePieceList);

                    // Base piece value
                    score += pieceScores[(int)piece.PieceType] * (pieceList.IsWhitePieceList ? 1 : -1);

                    // Pawns moving forward
                    /*if (piece.IsPawn)
                    {
                        if (pieceList.IsWhitePieceList)
                        {
                            score += pieceSquare.Rank;
                            whitePawns++;
                        }
                        else
                        {
                            score -= 7 - pieceSquare.Rank;
                            blackPawns++;
                        }
                    }
                    */
                    // Mobility
                    //score += 50 * BitboardHelper.GetNumberOfSetBits(attacks) * (pieceList.IsWhitePieceList ? 1 : -1);

                    // Attack/Defense
                    //score += 150 * BitboardHelper.GetNumberOfSetBits(attacks & board.AllPiecesBitboard) * (pieceList.IsWhitePieceList ? 1 : -1);

                    // Bishops (to count them for the bishop pair bonus)
                    if (piece.PieceType == PieceType.Bishop)
                    {
                        if (pieceList.IsWhitePieceList) whiteBishops++;
                        else blackBishops++;
                    }
                }
            }

            // Bishop Pair Bonus
            if (whiteBishops > 1) score += 50; // half a pawn bonus
            if (blackBishops > 1) score -= 50;

            // Penalize doubled pawns
            if (whitePawns > 8) score -= 15 * (whitePawns - 8);
            if (blackPawns > 8) score += 15 * (blackPawns - 8);

            // TODO: Add evaluations for isolated and passed pawns.
            // TODO: Add evaluations for center control.
            // TODO: Add evaluations for king safety.

            return score;
        }
}
