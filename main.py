import pygame
import chess

# Pygame settings
WIDTH, HEIGHT = 600, 600
CELL_SIZE = WIDTH // 8
FPS = 30

# Colors
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
BUTTON_COLOR = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 100))  # Extra space for buttons
pygame.display.set_caption("Chess Puzzle Solver")
clock = pygame.time.Clock()

# Load chess piece images
piece_images = {}
piece_names = ["bB", "bK", "bN", "bp", "bQ", "bR", "wB", "wK", "wN", "wp", "wQ", "wR"]
for name in piece_names:
    piece_images[name] = pygame.transform.scale(
        pygame.image.load(f"images/{name}.png"), (CELL_SIZE, CELL_SIZE)
    )

# Convert chess pieces to image keys
def piece_to_image_key(piece):
    if not piece:
        return None
    color = "w" if piece.color == chess.WHITE else "b"
    piece_map = {
        chess.PAWN: "p",
        chess.KNIGHT: "N",
        chess.BISHOP: "B",
        chess.ROOK: "R",
        chess.QUEEN: "Q",
        chess.KING: "K",
    }
    return color + piece_map[piece.piece_type]

# Draw the chessboard
def draw_board(board, selected_square=None):
    for rank in range(8):
        for file in range(8):
            rect = pygame.Rect(file * CELL_SIZE, rank * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = WHITE if (rank + file) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, rect)

            # Highlight selected square
            if selected_square == (file, rank):
                pygame.draw.rect(screen, (200, 200, 0), rect)

            # Draw the piece
            square = chess.square(file, 7 - rank)
            piece = board.piece_at(square)
            image_key = piece_to_image_key(piece)
            if image_key:
                screen.blit(piece_images[image_key], rect.topleft)

# Draw buttons
def draw_buttons():
    font = pygame.font.Font(None, 36)
    solve_white_rect = pygame.Rect(50, HEIGHT + 20, 200, 50)
    solve_black_rect = pygame.Rect(350, HEIGHT + 20, 200, 50)

    pygame.draw.rect(screen, BUTTON_COLOR, solve_white_rect)
    pygame.draw.rect(screen, BUTTON_COLOR, solve_black_rect)

    solve_white_text = font.render("Solve for White", True, TEXT_COLOR)
    solve_black_text = font.render("Solve for Black", True, TEXT_COLOR)

    screen.blit(solve_white_text, (solve_white_rect.x + 13, solve_white_rect.y + 10))
    screen.blit(solve_black_text, (solve_black_rect.x + 16, solve_black_rect.y + 10))

    return solve_white_rect, solve_black_rect

# Get the square based on mouse position
def get_square_from_mouse(pos):
    x, y = pos
    if y >= HEIGHT:  # Ignore clicks below the board
        return None
    file = x // CELL_SIZE
    rank = y // CELL_SIZE
    return chess.square(file, 7 - rank)

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing:
        max_eval = float("-inf")
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

# Simple board evaluation function
def evaluate_board(board):
    return sum(piece_value(piece) for piece in board.piece_map().values())

def piece_value(piece):
    values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
    return values[piece.piece_type] * (1 if piece.color == chess.WHITE else -1)

# Check if the puzzle is solved
def check_puzzle_solved(board):
    if board.is_checkmate():
        return "Checkmate! Puzzle solved."
    elif board.is_stalemate():
        return "Stalemate! Puzzle solved."
    return None

# Show a pop-up message
def show_popup_message(message):
    font = pygame.font.Font(None, 48)
    text = font.render(message, True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Semi-transparent overlay

    screen.blit(overlay, (0, 0))
    screen.blit(text, text_rect)

    pygame.display.flip()
    pygame.time.wait(2000)  # Wait for 2 seconds

# Make the best move for the given side
def make_best_move(board, depth, side):
    if board.is_game_over():
        return  # No moves to make if the puzzle is already solved

    best_move = None
    best_value = float("-inf") if side == chess.WHITE else float("inf")

    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, float("-inf"), float("inf"), side != chess.WHITE)
        board.pop()

        if (side == chess.WHITE and board_value > best_value) or (side == chess.BLACK and board_value < best_value):
            best_value = board_value
            best_move = move

    if best_move:
        board.push(best_move)

    # Check if the puzzle is solved after the move
    puzzle_solved = check_puzzle_solved(board)
    if puzzle_solved:
        show_popup_message(puzzle_solved)  # Display GUI pop-up message

# Main Chess Puzzle Solver
class ChessPuzzleSolver:
    def __init__(self):
        self.board = chess.Board()
        self.selected_square = None

    def handle_click(self, pos, button):
        clicked_square = get_square_from_mouse(pos)
        if clicked_square is not None:
            if button == 1:  # Left-click: Move pieces
                if self.selected_square is None:
                    piece = self.board.piece_at(clicked_square)
                    if piece:
                        self.selected_square = clicked_square
                else:
                    if clicked_square != self.selected_square:
                        self.board.set_piece_at(
                            clicked_square, self.board.piece_at(self.selected_square)
                        )
                        self.board.remove_piece_at(self.selected_square)
                    self.selected_square = None
            elif button == 3:  # Right-click: Remove pieces
                self.board.remove_piece_at(clicked_square)

    def draw(self):
        draw_board(self.board, self.selected_square)

# Main loop
def main():
    game = ChessPuzzleSolver()
    running = True

    while running:
        screen.fill((0, 0, 0))

        solve_white_rect, solve_black_rect = draw_buttons()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if solve_white_rect.collidepoint(event.pos):
                    make_best_move(game.board, 5, chess.WHITE)
                elif solve_black_rect.collidepoint(event.pos):
                    make_best_move(game.board, 5, chess.BLACK)
                else:
                    game.handle_click(event.pos, event.button)

        # Check if the puzzle is solved
        puzzle_solved_message = check_puzzle_solved(game.board)
        if puzzle_solved_message:
            show_popup_message(puzzle_solved_message)
            running = False

        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
