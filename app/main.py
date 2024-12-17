from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
import chess
import chess.svg
from app.Player import Player
from app.Player import RandomPlayer, Level0ThinkerPlayer

import inspect
import sys

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

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific allowed origins if needed
    allow_methods=["*"],  # Allow all HTTP methods: GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Allow all headers
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Initialize players
player1 = None
player2 = None
game_board = chess.Board()


# Discover all Player subclasses dynamically
def get_player_classes():
    player_classes = {}
    for name, obj in inspect.getmembers(sys.modules['app.Player'], inspect.isclass):
        if issubclass(obj, Player) and obj is not Player:
            player_classes[name] = obj
    return player_classes

@app.get("/player_types")
def get_player_types():
    player_classes = get_player_classes()
    return {"players": list(player_classes.keys())}

def create_player(player_type, color):
    player_classes = get_player_classes()
    if player_type in player_classes:
        return player_classes[player_type](f"{player_type}{color}", color)
    return None

@app.get("/play_game")
def play_game():
    global game_board  # Make it explicit we're using the global board
    
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
    
    # Get the move
    move = player.make_move(game_board.copy(), time=None)  # Pass a copy to prevent state corruption
    
    # Verify the move is legal
    if move is None or move not in game_board.legal_moves:
        return {"move": None, "board": game_board.fen(), "message": "Illegal move attempted"}
    
    # Make the move on the actual board
    game_board.push(move)
    
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

class StartGameRequest(BaseModel):
    white_type: str
    black_type: str

@app.post("/start_game")
def start_game(request: StartGameRequest):
    global player1, player2, game_board
    player1 = create_player(request.white_type, chess.WHITE)
    player2 = create_player(request.black_type, chess.BLACK)
    game_board.reset()
    return {"message": f"Game started with {request.white_type} vs {request.black_type}", "board": game_board.fen()}


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
    elif player_type == "Level0ThinkerPlayer":
        return Level0ThinkerPlayer(f"Level0ThinkerPlayer{color}", color)
    return None
