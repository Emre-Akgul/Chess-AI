from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
import chess
import chess.svg
from app.Player import RandomPlayer
import time


from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class StaticFilesMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static"):  # Adjust path as needed
            response.headers['Cache-Control'] = 'public, max-age=604800'  # One week
        return response
# Add to FastAPI app
middleware = [
    Middleware(StaticFilesMiddleware)
]
app = FastAPI(middleware=middleware)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Initialize players
player1 = RandomPlayer("RandomPlayer1", chess.WHITE)
player2 = RandomPlayer("RandomPlayer2", chess.BLACK)
game_board = chess.Board()


@app.get("/start_game")
def start_game():
    global game_board, time_white, time_black
    game_board.reset()  # Resets the board to the initial position
    return {"message": "Game started", "board": game_board.fen()}

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
async def get_board():
    return {"board": game_board.fen()}

@app.get("/board/image")
async def get_board_image():
    board_svg = chess.svg.board(board=game_board)
    return Response(content=board_svg, media_type="image/svg+xml")
