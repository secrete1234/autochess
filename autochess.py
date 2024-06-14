import pyautogui
import time
import cv2
import numpy as np
import chess
import chess.engine
import os

# Initialize the chess board and engine
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci("C:\\Personal\\T\\stockfish-windows-x86-64-avx2\\stockfish\\stockfish-windows-x86-64-avx2.exe")

# Coordinates for cropping
left = 300
top = 275
right = 995
bottom = 780

# Template matching threshold
THRESHOLD = 0.8

# Dictionary to map piece symbols to template image paths
piece_templates = {
    'P': 'templates/wp.png',  # White Pawn
    'R': 'templates/wr.png',  # White Rook
    'N': 'templates/wn.png',  # White Knight
    'B': 'templates/wb.png',  # White Bishop
    'Q': 'templates/wq.png',  # White Queen
    'K': 'templates/wk.png',  # White King
    'p': 'templates/bp.png',  # Black Pawn
    'r': 'templates/br.png',  # Black Rook
    'n': 'templates/bn.png',  # Black Knight
    'b': 'templates/bb.png',  # Black Bishop
    'q': 'templates/bq.png',  # Black Queen
    'k': 'templates/bk.png'   # Black King
}

def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")

def crop_screenshot(image_path, left, top, right, bottom):
    image = cv2.imread(image_path)
    cropped_image = image[top:bottom, left:right]
    cv2.imwrite("cropped_image.png", cropped_image)

def update_board_from_screenshot(cropped_image_path):
    global board
    image = cv2.imread(cropped_image_path, 0)
    board = chess.Board()  # Reset the board

    # Iterate over piece templates
    for piece, template_path in piece_templates.items():
        template = cv2.imread(template_path, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= THRESHOLD)

        piece_found = False
        for pt in zip(*loc[::-1]):
            x, y = pt
            piece_found = True

            # Calculate the board position from the coordinates
            file = chr(ord('a') + (x // square_size))
            rank = 8 - (y // square_size)
            position = f"{file}{rank}"

            board.set_piece_at(chess.parse_square(position), chess.Piece.from_symbol(piece))
        
        if piece_found:
            print(f"Piece {piece} recognized.")

    # Display the board for debugging
    print(board)

def click_square(square):
    # Size of each square
    square_size = 78.125

    # Generate the coordinates for each square
    square_map = {}
    for rank in range(8):  # ranks 1 to 8 (0 to 7)
        for file in range(8):  # files 'a' to 'h' (0 to 7)
            square_name = chr(ord('a') + file) + str(8 - rank)  # e.g., 'a1', 'h8'
            x = int(file * square_size + square_size / 2) + left  # Center of the file (column)
            y = int(rank * square_size + square_size / 2) + top  # Center of the rank (row)
            square_map[square_name] = (x, y)

    x, y = square_map[square]
    pyautogui.moveTo(x, y)
    pyautogui.click()

    # Print the clicked coordinates for debugging
    print(f"Clicked on square {square} at coordinates ({x}, {y})")

def make_best_move():
    global board
    # Get the best move from Stockfish
    result = engine.play(board, chess.engine.Limit(time=2.0))
    print("Best move:", result.move)

    # Execute the move on the screen
    move = result.move
    click_square(move.uci()[:2])  # Click the piece to move
    click_square(move.uci()[2:])  # Click the destination square

time.sleep(5)

# Main loop
while True:
    # Take a screenshot
    take_screenshot()

    # Crop the screenshot to the chessboard
    image_path = "screenshot.png"
    cropped_image_path = "cropped_image.png"
    crop_screenshot(image_path, left, top, right, bottom)

    # Update the board position from the screenshot
    update_board_from_screenshot(cropped_image_path)

    # Make the best move
    make_best_move()

    # Wait for the next screenshot
    time.sleep(10)
    os.remove("screenshot.png")
    os.remove("cropped_image.png")

# Cleanup
engine.quit()
