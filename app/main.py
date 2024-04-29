from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
import chess
import chess.svg
from app.Player import RandomPlayer
import time
from pydantic import BaseModel


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

# app.add_middleware(GZipMiddleware, minimum_size=1000)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Initialize players
player1 = None
player2 = None
game_board = chess.Board()


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

@app.get("/player_types")
def get_player_types():
    # Future implementation can fetch dynamically from a list of player classes
    return {"players": ["RandomPlayer"]}


class StartGameRequest(BaseModel):
    white_type: str
    black_type: str

@app.post("/start_game")
def start_game(request: StartGameRequest):
    global player1, player2, game_board
    player1 = RandomPlayer("RandomPlayer1", chess.WHITE) if request.white_type == "RandomPlayer" else None
    player2 = RandomPlayer("RandomPlayer2", chess.BLACK) if request.black_type == "RandomPlayer" else None
    game_board.reset()
    return {"message": "Game started with {} vs {}".format(request.white_type, request.black_type), "board": game_board.fen()}

class TestGameRequest(BaseModel):
    white_type: str = "RandomPlayer"
    black_type: str = "RandomPlayer"
    game_count: int = 100  # Default to 100 games if not specified

@app.post("/test_games")
async def test_games(request: TestGameRequest):    
    results = {
        "white_wins": 0,
        "black_wins": 0,
        "draws": 0
    }
    for _ in range(request.game_count):
        winner = await simulate_game(request.white_type, request.black_type)
        if winner == "white":
            results["white_wins"] += 1
        elif winner == "black":
            results["black_wins"] += 1
        else:
            results["draws"] += 1
    return results

async def simulate_game(white_type, black_type):
    player1 = create_player(white_type, chess.WHITE)
    player2 = create_player(black_type, chess.BLACK)
    game_board = chess.Board()
    while not game_board.is_game_over():
        player = player1 if game_board.turn == chess.WHITE else player2
        move = player.make_move(game_board, time=None)
        if move is None:  # No valid move available
            break
    if game_board.is_checkmate():
        return "white" if game_board.turn == chess.BLACK else "black"
    return "draw"

def create_player(player_type, color):
    if player_type == "RandomPlayer":
        return RandomPlayer(f"RandomPlayer{color}", color)
    # Add more player types as needed
    return None
