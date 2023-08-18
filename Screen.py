import pygame
import chess
from GameManager import GameManager
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTGRAY = (200, 200, 200)
DARKGRAY = (100, 100, 100)

# Screen settings
SCREEN_WIDTH = 1100  # 800 for board 300 for input boxes
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess")

# Helper function to display result
def display_result(text):
    font = pygame.font.Font(None, 72)  
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))  # Center the message on the screen
    screen.blit(label, label_rect)

def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHTGRAY if (row + col) % 2 == 0 else DARKGRAY
            pygame.draw.rect(screen, color, (col*100 + 300, row*100, 100, 100))  

def draw_pieces(board):
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            if piece:
                screen.blit(get_piece_image(piece), ((col)*TILE_SIZE + 300, (row)*TILE_SIZE)) 

TILE_SIZE = 100
def get_piece_image(piece):
    color = 'white' if piece.color == chess.WHITE else 'black'
    images = {
        'P': pygame.image.load(f"pieces/{color}_pawn.png"),
        'R': pygame.image.load(f"pieces/{color}_rook.png"),
        'N': pygame.image.load(f"pieces/{color}_knight.png"),
        'B': pygame.image.load(f"pieces/{color}_bishop.png"),
        'Q': pygame.image.load(f"pieces/{color}_queen.png"),
        'K': pygame.image.load(f"pieces/{color}_king.png"),
    }
    return pygame.transform.scale(images.get(piece.symbol().upper()), (TILE_SIZE, TILE_SIZE))

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = LIGHTGRAY
        self.color_active = DARKGRAY
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = pygame.font.Font(None, 32).render(text, True, self.color)
        self.active = False

    def handle_event(self, event, game_manager=None):
        # Key event handle
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    try:
                        move = chess.Move.from_uci(self.text)
                        if move in game_manager.board.legal_moves:
                            game_manager.board.push(move)
                            self.text = ''
                            game_manager.change_turn()  # switch player
                            self.color = LIGHTGRAY  # If there was invalid move than go back to pasive state.
                        else:
                            self.color = (255, 0, 0)  # Invalid move color feedback
                    except:
                        self.color = (255, 0, 0)  # Invalid move color feedback

                   
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = pygame.font.Font(None, 32).render(self.text, True, BLACK)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Render the text
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


input_boxes = [
    InputBox(30, 600, 140, 32, ""), 
    InputBox(30, 200, 140, 32, "")  
]

def draw_labels():
    font = pygame.font.Font(None, 32)
    label1 = font.render("Black Move:", True, BLACK)
    label2 = font.render("White Move:", True, BLACK)
    
    screen.blit(label1, (30, 170)) 
    screen.blit(label2, (30, 570))


game_manager = GameManager()

running = True
game_active = True 
while running:
    if game_active:
    
        screen.fill(WHITE)

        # Activate relevant input box
        if game_manager.current_turn == "White":
            input_boxes[0].active = True
            input_boxes[1].active = False
        else:
            input_boxes[0].active = False
            input_boxes[1].active = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            for box in input_boxes:
                box.handle_event(event, game_manager)  

        draw_board()
        draw_pieces(game_manager.board)
        draw_labels()
        

        
        if game_manager.is_checkmate():
            if game_manager.current_turn == "White":
                endgame_text = "Black Wins!"
                display_result(endgame_text)
            else:
                endgame_text = "White Wins!"
                display_result(endgame_text)
            game_active = False
        elif game_manager.is_stalemate():
            endgame_text = "Stalemate!"
            display_result(endgame_text)
            game_active = False

        for box in input_boxes:
            box.update()
            box.draw(screen)

        pygame.display.flip()
    else:
        display_result(endgame_text)
        pygame.display.flip()

        #If the game ends than wait for user to quit.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
pygame.quit()
