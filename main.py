import pygame
from sudoku_utils import *

class Cell():
    def __init__(self, y,x,height,width,num):
        self.y = y
        self.x = x
        self.height = height
        self.width = width
        self.num = num
        self.font = pygame.font.SysFont('Arial', 16)

        self.cell_surface = pygame.Surface((self.width, self.height))
        self.cell_rect = pygame.Rect(self.x, self.y, self.width, self.height)


    def update_cell_text(self):
        self.cell_font_render = self.font.render(str(self.num), True, (20,20,20))

class GridCell(Cell):
    def __init__(self, y,x,height,width,grid_pos_y,grid_pos_x, num=0):# TODO: 0 -> None
        super().__init__(y,x,height,width,num)

        self.grid_pos_y = grid_pos_y
        self.grid_pos_x = grid_pos_x
        self.cell_font_render = self.font.render(str(self.num) if self.num != 0 else "",
            True, (20,20,20)
        )

class NumberCell(Cell):
    def __init__(self, y,x,height,width, num):
        super().__init__(y,x,height,width, num)

        self.cell_font_render = self.font.render(str(num), True, (20,20,20))

class SudokuGui():
    def __init__(self):
        self.fps = 60
        self.fps_clock = pygame.time.Clock()
        width_screen, height_screen = 640, 480
        self.screen = pygame.display.set_mode([width_screen, height_screen])
        self.grid_cells = []
        self.number_cells = []

        # generate board
        width_cell, height_cell = 20, 20
        for y in range(0,9):
            margin_y = 0 if y == 0 else 5
            pos_y = y * (height_cell + margin_y)

            for x in range(0,9):
                margin_x = 0 if x == 0 else 5
                pos_x = x * (width_cell + margin_x)

                self.grid_cells.append(GridCell(pos_y, pos_x, height_cell, width_cell, y, x))

        # cell nums
        pos_y = 480-height_cell
        for num in range(1, 10):
            margin_x = 0 if x == 0 else 5
            pos_x = num * (width_cell + margin_x)
            self.number_cells.append(NumberCell(pos_y, pos_x, height_cell, width_cell, num))

        self.fill_colors ={
            'normal'  : '#ffffff',
            'hover'   : '#666666',
            'pressed' : '#333333'
        }

    def get_mouse_cell_action(self):
        mouse_pos = pygame.mouse.get_pos()
        is_mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)[0]

        for cell in self.grid_cells:
            if cell.cell_rect.collidepoint(mouse_pos):
                # check if pressed cell
                if is_mouse_pressed:
                    return {'grid_cell_pressed' : (cell.grid_pos_y, cell.grid_pos_x)}
                else:
                    return {'grid_cell_highlight' : (cell.grid_pos_y, cell.grid_pos_x)}

        for number_cell in self.number_cells:
            if number_cell.cell_rect.collidepoint(mouse_pos):
                # check if pressed cell
                if is_mouse_pressed:
                    return {'number_cell_chosen' : number_cell.num}


    def is_quit_clicked(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    def update_gui(self, game_board, current_num, update_gui_data):
        highlight_cell_pos_y, highlight_cell_pos_x = None, None
        if 'highlight_cell' in update_gui_data:
            highlight_cell_pos_y, highlight_cell_pos_x = update_gui_data['highlight_cell']
        pressed_cell_pos_y, pressed_cell_pos_x = None, None
        if 'pressed_cell' in update_gui_data:
            pressed_cell_pos_y, pressed_cell_pos_x = update_gui_data['pressed_cell']

        self.screen.fill((20, 20, 20))

        for btn in self.grid_cells:
            grid_y, grid_x = btn.grid_pos_y, btn.grid_pos_x

            if highlight_cell_pos_y == grid_y and highlight_cell_pos_x == grid_x:
                fill_type = 'hover'
            elif pressed_cell_pos_y == grid_y and pressed_cell_pos_x == grid_x:
                fill_type = 'pressed'
            else:
                fill_type = 'normal'

            btn.cell_surface.fill(self.fill_colors[fill_type])

            # check if y and x coordinates same as in gui
            game_board_value = game_board[grid_y][grid_x]
            if game_board_value != 0 and game_board_value != btn.num:
                btn.num = game_board_value
                btn.update_cell_text()

            btn.cell_surface.blit(btn.cell_font_render, [
                btn.cell_rect.width/2 - btn.cell_font_render.get_rect().width/2,
                btn.cell_rect.height/2 - btn.cell_font_render.get_rect().height/2
            ])
            self.screen.blit(btn.cell_surface, btn.cell_rect)

        for num_cell in self.number_cells:
            if current_num == num_cell.num:
                fill_type = 'pressed'
            else:
                fill_type = 'normal'

            num_cell.cell_surface.fill(self.fill_colors[fill_type])

            num_cell.cell_surface.blit(num_cell.cell_font_render, [
                num_cell.cell_rect.width/2 - num_cell.cell_font_render.get_rect().width/2,
                num_cell.cell_rect.height/2 - num_cell.cell_font_render.get_rect().height/2
            ])
            self.screen.blit(num_cell.cell_surface, num_cell.cell_rect)

        pygame.display.flip()
        self.fps_clock.tick(self.fps)

    #def write_notification():
    #    pass

class SudokuLogic():
    def __init__(self):
        self.solved_board = generate_sudoku_board()

        #for y in range(9):
        #    print(self.solved_board[y])


        if False == checkRowsCols(self.solved_board) or False == checkSquares(self.solved_board):
            raise Exception("board generation failed")
        clear_table = get_clear_table(percent_clear=10)# erase some numbers

        self.game_board = [[el_b*el_c for el_b,el_c in zip(row_board,row_clear)]
                for row_board,row_clear in zip(self.solved_board,clear_table)]

    def update_cell(self, grid_pos_y,grid_pos_x, cell_value):
        self.game_board[grid_pos_y][grid_pos_x] = cell_value

    def is_puzzle_solved(self):
        if checkRowsCols(self.game_board) and checkSquares(self.game_board):
            return True
        return False

# controller
class SudokuGame():
    def __init__(self):
        pygame.init()
        self.running = True
        self.current_number = None

        # create gui
        self.sudoku_gui = SudokuGui()

        try:
            self.sudoku_model = SudokuLogic()
        except Exception as e:
            print(e)
            self.running = False


    def run_game(self):
        # start a game
        # run gui cycle
        while self.running:
            # check if quit clicked
            is_quit = self.sudoku_gui.is_quit_clicked()
            if is_quit:
                self.running = False
                # program exit
                break

            # check if there's mouse-cell interaction
            cell_action = self.sudoku_gui.get_mouse_cell_action()
            update_gui_data = {}

            # check results in model
            if cell_action is not None:
                # update values in model
                if 'grid_cell_pressed' in cell_action:
                    grid_pos_y,grid_pos_x = cell_action['grid_cell_pressed']
                    if self.current_number is not None:
                        self.sudoku_model.update_cell(grid_pos_y,grid_pos_x, self.current_number)
                        self.log_callback(str(grid_pos_y) + "x" + str(grid_pos_x) + ": " + str(self.current_number))

                    update_gui_data['pressed_cell'] = (grid_pos_y,grid_pos_x)

                elif 'grid_cell_highlight' in cell_action:
                    update_gui_data['highlight_cell'] = cell_action['grid_cell_highlight']

                elif 'number_cell_chosen' in cell_action:
                    self.current_number = cell_action['number_cell_chosen']
                    self.log_callback("chosen number: " + str(self.current_number))


            # update gui
            self.sudoku_gui.update_gui(self.sudoku_model.game_board,
                self.current_number,
                update_gui_data)

            # check if game completed
            if self.sudoku_model.is_puzzle_solved():
                self.log_callback("congratulations")
                self.running = False
                break

        self.log_callback("finish game")
        pygame.quit()

    def log_callback(self, log_text):
        print(log_text)


    #def create_game():
    #    pass
    #def reset_game():# aka finish game
    #    pass
    #def clean_board():
    #    pass
    #def check_results():
    #    pass


if __name__ == "__main__":
    game = SudokuGame()
    game.run_game()
