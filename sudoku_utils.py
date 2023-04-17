import random

def checkRowsCols(board):
    """
        numbers in rows and cols are unique and not None
    """
    for i in range(9):
        rows_nums = [None] * 9# for elements from 1 to 9
        cols_nums = [None] * 9# for elements from 1 to 9
        for j in range(9):
            val_rows = board[i][j]
            val_cols = board[j][i]

            # rows
            if val_rows is not None and val_rows <= 9 and val_rows >= 1:
                if rows_nums[val_rows-1] is None:
                    rows_nums[val_rows-1] = True
                else:
                    #print("found repeated value")
                    return False
            else:
                #print("value in board is non-valid")
                return False

            # cols
            if val_cols is not None and val_cols <= 9 and val_cols >= 1:
                if cols_nums[val_cols-1] is None:
                    cols_nums[val_cols-1] = True
                else:
                    #print("found repeated value")
                    return False
            else:
                #print("value in board is non-valid")
                return False
    return True

def checkSquares(board):
    """
        check 3 by 3 squares for unique values and non-None
    """
    for row in [v for v in range(0,9,3)]:# row_begin coordinates
        for col in [v for v in range(0,9,3)]:# col_begin coordinates
            nums = [None]*9# for elements from 1 to 9
            for row_step in range(3):
                y = row + row_step
                for col_step in range(3):
                    x = col + col_step
                    val = board[y][x]
                    if val is not None and val <= 9 and val >= 1:
                        if nums[val-1] is None:
                            nums[val-1] = True
                        else:
                            #print("found repeated value")
                            return False
                    else:
                        #print("value in board is non-valid")
                        return False
    return True

def generate_sudoku_board(square_size=3):
    width = square_size*square_size
    height = square_size*square_size

    def get_random_positions(square_size=3):
        """
            get random shuffled groups of [0,1,2] [3,4,5] [6,7,8]
        """
        #[random_square_pos for random_square_pos in shuffle([i for i in range(square_size)])]
        grid_pos = [i for i in range(square_size)]
        pos_in_grid = [i for i in range(square_size)]
        random.shuffle(pos_in_grid)
        random.shuffle(grid_pos)

        return [random_pos_in_grid*3 + random_square_pos
                for random_pos_in_grid in pos_in_grid
                    for random_square_pos in grid_pos]

    # create rows. every row is shifted by y-value : 1,2,3,...;4,5,6,...;7,8,9,...; 2,3,4,...;5,6,7,...;8,9,1,...
    board = [[(y*square_size+x+y//square_size)%width+1 for x in range(width)] for y in range(height)]

    # get exchanged row positions
    new_row_positions = get_random_positions()

    # get exchanged column positions
    new_col_positions = get_random_positions()

    shuffled_board = [[None]*width for _ in range(height)]

    # exchange rows
    for x_orig in range(width):
        x_new = new_col_positions[x_orig]
        for y_orig in range(height):
            y_new = new_row_positions[y_orig]
            shuffled_board[y_new][x_new] = board[y_orig][x_orig]

    return shuffled_board

def get_clear_table(percent_clear=40, square_size=3):
    width = square_size*square_size
    height = square_size*square_size

    total_digits = height * width
    num_clear = total_digits * percent_clear // 100

    clear_table = [0 for _ in range(num_clear)] + [1 for _ in range(total_digits - num_clear)]
    random.shuffle(clear_table)
    clear_table = [clear_table[9*n:9*n+9] for n in range(9)]# 1D -> 2D
    print(len(clear_table))

    return clear_table
