import pygame
import chess
import time
import math


# Thiết lập Pygame
pygame.init()

# Kích thước cửa sổ và màu sắc
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (118, 150, 86)
BROWN = (238, 238, 210)
DEPTH = 4

# Tạo cửa sổ hiển thị
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Load hình ảnh các quân cờ
pieces = {
    "r": pygame.image.load("./images/chess/bR.png"),
    "n": pygame.image.load("./images/chess/bN.png"),
    "b": pygame.image.load("./images/chess/bB.png"),
    "q": pygame.image.load("./images/chess/bQ.png"),
    "k": pygame.image.load("./images/chess/bK.png"),
    "p": pygame.image.load("./images/chess/bP.png"),
    "R": pygame.image.load("./images/chess/wR.png"),
    "N": pygame.image.load("./images/chess/wN.png"),
    "B": pygame.image.load("./images/chess/wB.png"),
    "Q": pygame.image.load("./images/chess/wQ.png"),
    "K": pygame.image.load("./images/chess/wK.png"),
    "P": pygame.image.load("./images/chess/wP.png"),
}

# Thay đổi kích thước hình ảnh quân cờ
for key in pieces:
    pieces[key] = pygame.transform.scale(
        pieces[key], (SQUARE_SIZE, SQUARE_SIZE))

# Khởi tạo bàn cờ cờ vua
board = chess.Board()

# Vẽ bàn cờ


def draw_board():
    for row in range(8):
        for col in range(8):
            color = GREEN if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, pygame.Rect(
                col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Vẽ quân cờ lên bàn cờ


def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                screen.blit(pieces[piece.symbol()], pygame.Rect(
                    col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def evaluate_move(board, move):
    score = 0
    if board.gives_check(move):
        score += 100  # Bonus for giving check
    # Correct attribute is to_square
    captured_piece = board.piece_at(move.to_square)
    if captured_piece:
        score += captured_piece.piece_type * 10
    # Add more scoring criteria as needed
    return score


def order_moves(board):
    # Prioritize moves that give check, capture pieces, or control key squares
    moves = list(board.legal_moves)
    moves.sort(key=lambda move: (
        board.gives_check(move),
        board.piece_at(move.to_square).piece_type if board.piece_at(
            move.to_square) else 0,
        board.piece_at(move.from_square).piece_type if board.piece_at(
            move.from_square) else 0,
        evaluate_move(board, move),
    ), reverse=True)
    return moves


def evaluate_board(board):
    # Replace this with a full evaluation of the board state
    score = 0
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # Vua không có giá trị trong đánh giá
    }

    for piece in piece_values:
        score += len(board.pieces(piece, chess.WHITE)) * piece_values[piece]
        score -= len(board.pieces(piece, chess.BLACK)) * piece_values[piece]

    # Optionally add more complex heuristics for positional scoring, checkmates, etc.

    return score


def alpha_beta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        # Sử dụng hàm đánh giá toàn bộ bàn cờ khi đạt độ sâu 0 hoặc trò chơi kết thúc
        # Trả về cả giá trị đánh giá và nước đi tốt nhất
        return evaluate_board(board), None

    # Lấy danh sách các nước đi hợp lệ đã được sắp xếp
    moves = order_moves(board)
    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for move in moves:
            board.push(move)
            eval_score, _ = alpha_beta(
                board, depth - 1, alpha, beta, False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                if depth == DEPTH:  # Nếu đạt độ sâu cần thiết, lưu lại nước đi tốt nhất
                    best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Cắt tỉa alpha-beta
        return max_eval, best_move  # Trả về giá trị đánh giá và nước đi tốt nhất
    else:
        min_eval = float('inf')
        best_move = None
        for move in moves:
            board.push(move)
            eval_score, _ = alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                if depth == 4:  # Nếu đạt độ sâu cần thiết, lưu lại nước đi tốt nhất
                    best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Cắt tỉa alpha-beta
        return min_eval, best_move  # Trả về giá trị đánh giá và nước đi tốt nhất


# Chọn nước đi của người chơi


def get_square_under_mouse():
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    x, y = [int(v // SQUARE_SIZE) for v in mouse_pos]
    if x >= 0 and x < 8 and y >= 0 and y < 8:
        return chess.square(x, 7 - y)
    return None


def get_legal_moves(square):
    """
    Lấy các nước đi hợp lệ của quân cờ tại ô được chọn.
    """
    legal_moves = []
    for move in board.legal_moves:
        if move.from_square == square:
            legal_moves.append(move.to_square)
    return legal_moves


def draw_legal_moves(moves):
    """
    Vẽ các nước đi hợp lệ của quân cờ.
    """
    for move in moves:
        row = 7 - chess.square_rank(move)
        col = chess.square_file(move)
        pygame.draw.circle(screen, (0, 255, 0),
                           (col * SQUARE_SIZE + SQUARE_SIZE // 2,
                            row * SQUARE_SIZE + SQUARE_SIZE // 2),
                           SQUARE_SIZE // 6)  # Vẽ hình tròn nhỏ tại các ô hợp lệ


# Hàm chính


def main():
    running = True
    selected_square = None
    AI_Play = False

    while running:
        draw_board()
        draw_pieces()
        if selected_square is not None:
            draw_legal_moves(legal_moves_display)
        icon = pygame.image.load('./images/icon.jpg')
        pygame.display.set_icon(icon)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if AI_Play == False:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if selected_square is None:
                        selected_square = get_square_under_mouse()
                        # Kiểm tra nếu ô đã chọn có quân cờ và là quân cờ của người chơi
                        if board.piece_at(selected_square) is None or board.piece_at(selected_square).color != board.turn:
                            selected_square = None  # Không chọn ô nếu không hợp lệ
                        else:
                            legal_moves_display = get_legal_moves(
                                selected_square)
                    else:
                        move_square = get_square_under_mouse()

                        if board.piece_at(selected_square).piece_type == chess.PAWN and \
                                (chess.square_rank(move_square) == 0 or chess.square_rank(move_square) == 7):
                            # Nếu tốt đến hàng cuối, thực hiện phong cấp (ở đây mặc định thành Hậu)
                            move = chess.Move(
                                selected_square, move_square, promotion=chess.QUEEN)
                        else:
                            # Nước đi bình thường
                            move = chess.Move(selected_square, move_square)

                        if move in board.legal_moves:
                            board.push(move)
                            AI_Play = True
                        selected_square = None
            else:
                _, move = alpha_beta(board, DEPTH, float(
                    '-inf'), float('inf'), False)
                if move in board.legal_moves:
                    board.push(move)
                    AI_Play = False

        if board.is_game_over():
            print(f"Game over! Result: {board.result()}")
            running = False

        pygame.time.delay(100)

    pygame.quit()


if __name__ == "__main__":
    main()
