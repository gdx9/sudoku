import pygame
from sudoku_utils import *
from dataclasses import dataclass
from enum import Enum

@dataclass
class MouseData:
    position: (int,int)
    pressed: bool = False
    pressed_grid_position: (int,int) = None
    pressed_number_cell: int = None

class ColorType(Enum):
    NORMAL = 0
    HOVER = 1
    PRESSED = 2

class BackgroundColors:
    def __init__(self, color_normal: str, color_hover: str, color_pressed: str):
        self.color_normal = color_normal
        self.color_hover = color_hover
        self.color_pressed = color_pressed

    def get_color(self, color_type: ColorType):
        if ColorType.HOVER == color_type:
            return self.color_hover
        elif ColorType.PRESSED == color_type:
            return self.color_pressed
        else:
            return self.color_normal

class GuiRectangle:
    def __init__(self, screen_pointer, y,x, height, width, font_size=16, rectangle_text=""):
        self.screen_pointer = screen_pointer
        self.font = pygame.font.SysFont('Arial', font_size)
        self.font_render = self.font.render(rectangle_text, True, (20,20,20))

        self.surface = pygame.Surface((width, height))
        self.rect = pygame.Rect(x, y, width, height)

    def get_color(self, color_type: ColorType):
        raise NotImplementedError()

    def process(self, color_type, mouse_pos):# TODO: enum
        if self.rect.collidepoint(mouse_pos) and ColorType.PRESSED != color_type:
            color_type = ColorType.HOVER

        self.surface.fill(self.get_color(color_type))
        self.surface.blit(self.font_render, [
            self.rect.width/2 - self.font_render.get_rect().width/2,
            self.rect.height/2 - self.font_render.get_rect().height/2
        ])
        self.screen_pointer.blit(self.surface, self.rect)

class GridCell(GuiRectangle):
    background_colors = BackgroundColors('#ffffff', '#666666', '#333333')

    def __init__(self,screen_pointer,y,x,height,width,grid_pos_y,grid_pos_x,num=0):# TODO: 0 -> None
        super().__init__(screen_pointer,y,x,height,width, 16, str(num) if num != 0 else "")
        self.num = num

        self.grid_pos_y = grid_pos_y
        self.grid_pos_x = grid_pos_x

    def get_color(self, color_type: ColorType):
        return GridCell.background_colors.get_color(color_type)

    def update_cell_text(self):
        self.font_render = self.font.render(str(self.num), True, (20,20,20))

class NumberCell(GuiRectangle):
    background_colors = BackgroundColors('#dddddd', '#555555', '#222222')

    def __init__(self,screen_pointer,y,x,height,width,num):
        super().__init__(screen_pointer,y,x,height,width, 16, str(num))
        self.num = num

    def get_color(self, color_type: ColorType):
        return NumberCell.background_colors.get_color(color_type)

class GuiButton(GuiRectangle):
    background_colors = BackgroundColors('#dd11dd', '#556655', '#223322')

    def __init__(self,screen_pointer,y,x,height,width,text):
        super().__init__(screen_pointer,y,x,height,width, 42, text)

    def get_color(self, color_type: ColorType):
        return GuiButton.background_colors.get_color(color_type)

class SudokuGui:
    def __init__(self):
        self.fps = 60
        self.fps_clock = pygame.time.Clock()
        width_screen, height_screen = 640, 480
        self.screen = pygame.display.set_mode([width_screen, height_screen])
        self.grid_cells = []
        self.number_cells = []

        # generate board
        grid_cell_margin = 10
        width_cell, height_cell = 40, 40
        for y in range(0,9):
            margin_y = 0 if y == 0 else 5
            pos_y = y * (height_cell + margin_y) + grid_cell_margin

            for x in range(0,9):
                margin_x = 0 if x == 0 else 5
                pos_x = x * (width_cell + margin_x) + grid_cell_margin

                self.grid_cells.append(GridCell(self.screen,pos_y, pos_x, height_cell, width_cell, y, x))

        # cell nums
        num_cell_margin = 10
        pos_y = 480 - height_cell - num_cell_margin
        for num in range(1, 10):
            margin_x = 0 if x == 0 else 5
            pos_x = (num-1) * (width_cell + margin_x) + num_cell_margin
            self.number_cells.append(NumberCell(self.screen,pos_y, pos_x, height_cell, width_cell, num))

        grid_setting_button_distance = 20
        setting_button_mergin = 10
        setting_button_height = 60
        setting_button_pos_x = pos_x+width_cell+grid_setting_button_distance
        setting_button_pos_y = grid_cell_margin
        self.button_start_reset   = GuiButton(self.screen,setting_button_pos_y,  setting_button_pos_x,
                                            setting_button_height, 220, 'Start/Restart')
        setting_button_pos_y += setting_button_height+setting_button_mergin
        self.button_hint          = GuiButton(self.screen,setting_button_pos_y,  setting_button_pos_x,
                                            setting_button_height, 80, 'Hint')
        setting_button_pos_y += setting_button_height+setting_button_mergin
        self.button_check_correct = GuiButton(self.screen,setting_button_pos_y, setting_button_pos_x,
                                            setting_button_height, 120, 'Check')

    def get_mouse_data(self):
        mouse_pos = pygame.mouse.get_pos()
        is_mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)[0]

        mouse_data = MouseData(position=mouse_pos)
        if is_mouse_pressed:
            mouse_data.pressed = True
            #mouse_data.update({'pressed' : True})
            for cell in self.grid_cells:
                if cell.rect.collidepoint(mouse_pos):
                    mouse_data.pressed_grid_position = (cell.grid_pos_y, cell.grid_pos_x)

            for number_cell in self.number_cells:
                if number_cell.rect.collidepoint(mouse_pos):
                    mouse_data.pressed_number_cell = number_cell.num

        return mouse_data

    def is_quit_clicked(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    def update_gui(self, game_board, current_num, mouse_data):
        mouse_pos = mouse_data.position

        self.screen.fill((20, 20, 20))

        for btn in self.grid_cells:
            # check if y and x coordinates same as in gui
            game_board_value = game_board[btn.grid_pos_y][btn.grid_pos_x]
            if game_board_value != 0 and game_board_value != btn.num:
                btn.num = game_board_value
                btn.update_cell_text()

            fill_type = ColorType.PRESSED if mouse_data.pressed_grid_position is not None\
                and mouse_data.pressed_grid_position == (btn.grid_pos_y,btn.grid_pos_x)\
                else ColorType.NORMAL
            btn.process(fill_type, mouse_pos)

        for num_cell in self.number_cells:
            fill_type = ColorType.PRESSED if current_num == num_cell.num else ColorType.NORMAL
            num_cell.process(fill_type, mouse_pos)

        # gui buttons
        self.button_start_reset.process(ColorType.NORMAL, mouse_pos)

        self.button_hint.process(ColorType.NORMAL, mouse_pos)

        self.button_check_correct.process(ColorType.NORMAL, mouse_pos)

        pygame.display.flip()
        self.fps_clock.tick(self.fps)

    #def write_notification():
    #    pass

class SudokuLogic():
    def __init__(self):
        self.solved_board = generate_sudoku_board()

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

            # get data of mouse event
            mouse_data = self.sudoku_gui.get_mouse_data()

            # check results in model
            if mouse_data.pressed_grid_position is not None:
                grid_pos_y,grid_pos_x = mouse_data.pressed_grid_position
                if self.current_number is not None:
                    self.sudoku_model.update_cell(grid_pos_y,grid_pos_x, self.current_number)
                    self.log_callback(str(grid_pos_y) + "x" + str(grid_pos_x) + ": " + str(self.current_number))
            elif mouse_data.pressed_number_cell is not None:
                self.current_number = mouse_data.pressed_number_cell
                self.log_callback("chosen number: " + str(self.current_number))

            # update gui
            self.sudoku_gui.update_gui(self.sudoku_model.game_board,
                self.current_number,
                mouse_data)

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
