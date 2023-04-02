from sudoku_utils import *

if __name__ == "__main__":
    board = generate_sudoku_board()
    clear_table = get_clear_table(percent_clear=40)

    # check if rows and cols are correct (no repeats in lines and 3x3 squares)
    print("vertical and horizontal lines check: {}\n3x3 squares check: {}"
        .format("OK" if checkRowsCols(board) else "BAD",
        "OK" if checkSquares(board) else "BAD"))

    board = [[el_b*el_c for el_b,el_c in zip(row_board,row_clear)] for row_board,row_clear in zip(board,clear_table)]
    print("sudoku board:")
    for row in board:
        print(row)
