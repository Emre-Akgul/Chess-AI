from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
import chess
import chess.svg
from app.Player import RandomPlayer
import time

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Initialize players
player1 = RandomPlayer("RandomPlayer1", chess.WHITE)
player2 = RandomPlayer("RandomPlayer2", chess.BLACK)
game_board = chess.Board()

time_white = 60.0  # 10 minutes in seconds
time_black = 60.0

@app.get("/start_game")
def start_game():
    global game_board, time_white, time_black
    game_board.reset()  # Resets the board to the initial position
    time_white = 60.0  # Reset the timer for white
    time_black = 60.0  # Reset the timer for black
    return {"message": "Game started", "board": game_board.fen(), "time_white": time_white, "time_black": time_black}

@app.get("/play_game")
def play_game():
    if game_board.is_game_over():
        result = "Game over"
        if game_board.is_checkmate():
            result += ": checkmate"
        elif game_board.is_stalemate():
            result += ": stalemate"
        else:
            result += ": draw"
        return {"move": None, "board": game_board.fen(), "message": result}
    
    # Decide who's turn it is
    player = player1 if game_board.turn == chess.WHITE else player2
    move = player.make_move(game_board, time=None)
    
    return {"move": move.uci(), "board": game_board.fen(), "message": "Move made"}


@app.get("/")
def read_root():
    return {"message": "Welcome to Chess AI"}

@app.get("/board")
def get_board():
    return {"board": game_board.fen()}

@app.get("/board/image")
def get_board_image():
    # Generate SVG from the current board state
    board_svg = chess.svg.board(board=game_board)
    return Response(content=board_svg, media_type="image/svg+xml")

@app.get("/move/random")
def make_random_move():
    # Decide who's turn it is
    player = player1 if game_board.turn == chess.WHITE else player2
    move = player.make_move(game_board, time=None)
    return {"move": str(move), "board": game_board.fen()}

@app.get("/board/image/png")
def get_board_image_png():
    # Generate SVG from the current board state
    board_svg = chess.svg.board(board=game_board)
    # Convert SVG to PNG
    png_image = cairosvg.svg2png(bytestring=board_svg)
    return Response(content=png_image, media_type="image/png")

@app.get("/get_time")
def get_time():
    global time_white, time_black
    return {"time_white": round(time_white), "time_black": round(time_black)}