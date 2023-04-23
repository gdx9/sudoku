import pygame
from sudoku_utils import *
from dataclasses import dataclass
from enum import Enum

class CellType(Enum):
    CHANGEABLE = 0
    NON_CHANGEABLE = 1
    HINTED = 2
    CHECKED_WRONG = 3

@dataclass
class BoardCell:
    value: int
    cell_type: CellType

@dataclass
class MouseData:
    position: (int,int)
    pressed: bool = False
    pressed_grid_position: (int,int) = None
    pressed_number_cell: int = None
    pressed_hint: bool = False
    pressed_check_correct: bool = False
    restart: bool = False

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
    def __init__(self, screen_pointer, y,x, height, width, font_size=16, rectangle_text="", is_bold=False):
        self.screen_pointer = screen_pointer
        self.font = pygame.font.SysFont('Arial', font_size, bold=is_bold)
        self.font_render = self.font.render(rectangle_text, True, ((20,20,20)))

        self.surface = pygame.Surface((width, height))
        self.rect = pygame.Rect(x, y, width, height)

    def get_color(self, color_type: ColorType):
        raise NotImplementedError()

    def process(self, color_type, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and ColorType.PRESSED != color_type:
            color_type = ColorType.HOVER

        self.surface.fill(self.get_color(color_type))
        self.surface.blit(self.font_render, [
            self.rect.width/2 - self.font_render.get_rect().width/2,
            self.rect.height/2 - self.font_render.get_rect().height/2
        ])
        self.screen_pointer.blit(self.surface, self.rect)

class GridCell(GuiRectangle):
    background_colors = BackgroundColors('#F5EBE0', '#F0DBDB', '#F0E1D1')

    @staticmethod
    def get_text_color(cell_type):
        if cell_type == CellType.HINTED:
            return ((208,184,168))
        elif cell_type == CellType.NON_CHANGEABLE:
            return ((247,124,44))
        elif cell_type == CellType.CHECKED_WRONG:
            return ((255,0,0))
        else:
            return ((20,20,20))

    def __init__(self,screen_pointer,y,x,height,width,grid_pos_y,grid_pos_x,
                    cell_data):
        super().__init__(screen_pointer,y,x,height,width,16, str(cell_data.value) if cell_data.value != 0 else "",is_bold=True)
        self.cell_data = BoardCell(cell_data.value, cell_data.cell_type)

        self.font_render = self.font.render(str(cell_data.value) if cell_data.value != 0 else "", True, GridCell.get_text_color(cell_data.cell_type))

        self.grid_pos_y = grid_pos_y
        self.grid_pos_x = grid_pos_x

    def get_color(self, color_type: ColorType):
        return GridCell.background_colors.get_color(color_type)

    def reset_cell_data(self, new_cell_data :BoardCell):
        self.cell_data.value = new_cell_data.value
        self.cell_data.cell_type = new_cell_data.cell_type

        self.font_render = self.font.render(str(self.cell_data.value) if self.cell_data.value != 0 else "", True, GridCell.get_text_color(self.cell_data.cell_type))


    def update_cell_text(self, game_board_value, cell_type: CellType):
        if game_board_value == 0:
            return
        if game_board_value != self.cell_data.value or cell_type != self.cell_data.cell_type:
            self.cell_data.value = game_board_value
            self.cell_data.cell_type = cell_type

            text_color = GridCell.get_text_color(self.cell_data.cell_type)

            self.font_render = self.font.render(str(self.cell_data.value), True, text_color)

class NumberCell(GuiRectangle):
    background_colors = BackgroundColors('#F0DBDB', '#D0DBDB', '#D9A4A4')

    def __init__(self,screen_pointer,y,x,height,width,num):
        super().__init__(screen_pointer,y,x,height,width, 16, str(num))
        self.num = num

    def get_color(self, color_type: ColorType):
        return NumberCell.background_colors.get_color(color_type)

class GuiButton(GuiRectangle):
    background_colors = BackgroundColors('#DBA39A', '#EACDC5', '#BC5443')

    def __init__(self,screen_pointer,y,x,height,width,text, is_toggable=False):
        super().__init__(screen_pointer,y,x,height,width, 32, text)
        self.is_toggable = is_toggable
        self.is_active = False

    def get_color(self, color_type: ColorType):
        if self.is_toggable and self.is_active:
            color_type = ColorType.PRESSED

        return GuiButton.background_colors.get_color(color_type)

class SudokuGui:
    def __init__(self, game_board):
        self.fps = 60
        self.fps_clock = pygame.time.Clock()
        width_screen, height_screen = 640, 480
        self.screen = pygame.display.set_mode([width_screen, height_screen])
        self.grid_cells = []
        self.number_cells = []

        # generate board
        grid_cell_margin = 10
        margin_default = 5
        width_cell, height_cell = 40, 40
        for y in range(0,9):
            margin_y = 0 if y == 0 else margin_default
            pos_y = y * (height_cell + margin_y) + grid_cell_margin

            for x in range(0,9):
                margin_x = 0 if x == 0 else margin_default
                pos_x = x * (width_cell + margin_x) + grid_cell_margin

                self.grid_cells.append(GridCell(self.screen,pos_y, pos_x,
                        height_cell, width_cell, y, x, game_board[y][x]))


        # board grid lines TODO:
        self.grid_lines = list()
        # vertical lines
        grid_line_y_start = grid_cell_margin
        grid_line_y_end = grid_cell_margin + 9 * height_cell + margin_default * 8
        for block_num in [3,6]:
            grid_line_x = grid_cell_margin+block_num*width_cell+margin_default*(block_num-1)+margin_default//2
            self.grid_lines.append((grid_line_x,grid_line_y_start,grid_line_x,grid_line_y_end))

        # horizontal lines
        grid_line_x_start = grid_cell_margin
        grid_line_x_end = grid_cell_margin + 9 * width_cell + margin_default * 8
        for block_num in [3,6]:
            grid_line_y = grid_cell_margin+block_num*height_cell+margin_default*(block_num-1)+margin_default//2
            self.grid_lines.append((grid_line_x_start,grid_line_y,grid_line_x_end,grid_line_y))


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
                                            setting_button_height, 200, 'Start/Restart')
        setting_button_pos_y += setting_button_height+setting_button_mergin
        self.button_hint          = GuiButton(self.screen,setting_button_pos_y,  setting_button_pos_x,
                                            setting_button_height, 80, 'Hint')
        setting_button_pos_y += setting_button_height+setting_button_mergin
        self.button_check_correct = GuiButton(self.screen,setting_button_pos_y, setting_button_pos_x,
                                            setting_button_height, 120, 'Check', True)

    def reset_table(self, game_board):
        for y in range(0,9):
            for x in range(0,9):
                self.grid_cells[y*9+x].reset_cell_data(game_board[y][x])


    def check_gui_elements_interaction(self, mouse_pos, is_mouse_pressed):
        mouse_data = MouseData(position=mouse_pos)

        if is_mouse_pressed:
            mouse_data.pressed = True

            for cell in self.grid_cells:
                if cell.rect.collidepoint(mouse_pos):
                    mouse_data.pressed_grid_position = (cell.grid_pos_y, cell.grid_pos_x)

            for number_cell in self.number_cells:
                if number_cell.rect.collidepoint(mouse_pos):
                    mouse_data.pressed_number_cell = number_cell.num

            if self.button_hint.rect.collidepoint(mouse_pos):
                mouse_data.pressed_hint = True

            if self.button_check_correct.rect.collidepoint(mouse_pos):
                mouse_data.pressed_check_correct = True

            if self.button_start_reset.rect.collidepoint(mouse_pos):
                mouse_data.restart = True

        return mouse_data

    def check_events(self):
        is_quit = False
        mouse_pos = None
        is_mouse_pressed = False

        all_events = pygame.event.get()
        for event in all_events:
            if event.type == pygame.QUIT:
                is_quit = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                is_mouse_pressed = True
        mouse_pos = pygame.mouse.get_pos()

        return is_quit,mouse_pos,is_mouse_pressed

    def update_gui(self, game_board, current_num, mouse_data, highlight_incorrect):
        mouse_pos = mouse_data.position

        self.screen.fill(((254, 252, 243))) # FEFCF3

        for btn in self.grid_cells:
            # check if y and x coordinates same as in gui
            game_board_value = game_board[btn.grid_pos_y][btn.grid_pos_x].value
            btn.update_cell_text(game_board_value, game_board[btn.grid_pos_y][btn.grid_pos_x].cell_type)

            fill_type = ColorType.PRESSED if mouse_data.pressed_grid_position is not None\
                and mouse_data.pressed_grid_position == (btn.grid_pos_y,btn.grid_pos_x)\
                else ColorType.NORMAL
            btn.process(fill_type, mouse_pos)

        for (x_start,y_start,x_end,y_end) in self.grid_lines:
            pygame.draw.line(self.screen, (0,0,0), (x_start,y_start),(x_end,y_end), 1)

        for num_cell in self.number_cells:
            fill_type = ColorType.PRESSED if current_num == num_cell.num else ColorType.NORMAL
            num_cell.process(fill_type, mouse_pos)

        # gui buttons
        self.button_start_reset.process(ColorType.NORMAL, mouse_pos)

        self.button_hint.process(ColorType.NORMAL, mouse_pos)

        self.button_check_correct.is_active = highlight_incorrect
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
        self.clear_table = get_clear_table(percent_clear=10)# erase some numbers

        #self.game_board = [[el_b*el_c for el_b,el_c in zip(row_board,row_clear)]
        #        for row_board,row_clear in zip(self.solved_board,self.clear_table)]
        self.game_board = [[BoardCell(el_b*el_c, CellType.CHANGEABLE if el_c == 0 else CellType.NON_CHANGEABLE)
            for el_b,el_c in zip(row_board,row_clear)]
                for row_board,row_clear in zip(self.solved_board,self.clear_table)]


    def update_cell(self, grid_pos_y,grid_pos_x, cell_value):
        cell_type = self.game_board[grid_pos_y][grid_pos_x].cell_type
        if cell_type == CellType.CHANGEABLE or cell_type == CellType.CHECKED_WRONG:
            self.game_board[grid_pos_y][grid_pos_x].value = cell_value

    def add_hint_value(self):
        # find a value which is in solved_board, but not in game_board yet
        for y in range(9):
            for x in range(9):
                if self.game_board[y][x].value != self.solved_board[y][x]:
                    self.game_board[y][x].value = self.solved_board[y][x]
                    self.game_board[y][x].cell_type = CellType.HINTED

                    return

    def update_correct_values(self, highlight_incorrect):
        for y in range(9):
            for x in range(9):
                cell_type = self.game_board[y][x].cell_type
                if cell_type == CellType.CHANGEABLE or cell_type == CellType.CHECKED_WRONG:
                    if highlight_incorrect:
                        if self.game_board[y][x].value != 0:
                            if self.game_board[y][x].value != self.solved_board[y][x]:
                                self.game_board[y][x].cell_type = CellType.CHECKED_WRONG
                            else:
                                self.game_board[y][x].cell_type = CellType.CHANGEABLE
                    else:
                        self.game_board[y][x].cell_type = CellType.CHANGEABLE

    def is_puzzle_solved(self):
        game_board_values = [[el.value
            for el in row_board]
                for row_board in self.game_board]
        if checkRowsCols(game_board_values) and checkSquares(game_board_values):
            return True
        return False

# controller
class SudokuGame():
    def __init__(self):
        pygame.init()
        self.running = True
        self.current_number = None
        self.highlight_incorrect = False

        self.create_game_model()

        # create gui
        self.sudoku_gui = SudokuGui(self.sudoku_model.game_board)

    def run_game(self):
        # start a game
        # run gui cycle
        while self.running:
            # check if quit clicked
            is_quit, mouse_pos, is_mouse_pressed = self.sudoku_gui.check_events()
            if is_quit:
                self.running = False
                # program exit
                break

            # get data of mouse event
            mouse_data = self.sudoku_gui.check_gui_elements_interaction(mouse_pos, is_mouse_pressed)

            if mouse_data.restart:
                self.restart_game()

            # check results in model
            if mouse_data.pressed_hint:
                # get non-cleared value
                self.sudoku_model.add_hint_value()

            if mouse_data.pressed_check_correct:
                self.highlight_incorrect = not self.highlight_incorrect

            self.sudoku_model.update_correct_values(self.highlight_incorrect)


            if mouse_data.pressed_grid_position is not None:
                grid_pos_y,grid_pos_x = mouse_data.pressed_grid_position
                if self.current_number is not None:
                    self.sudoku_model.update_cell(grid_pos_y,grid_pos_x, self.current_number)
                    #self.log_callback(str(grid_pos_y) + "x" + str(grid_pos_x) + ": " + str(self.current_number))
            elif mouse_data.pressed_number_cell is not None:
                self.current_number = mouse_data.pressed_number_cell
                #self.log_callback("chosen number: " + str(self.current_number))

            # update gui
            self.sudoku_gui.update_gui(self.sudoku_model.game_board,
                self.current_number,
                mouse_data, self.highlight_incorrect)

            # check if game completed
            if self.sudoku_model.is_puzzle_solved():
                self.log_callback("congratulations")
                self.running = False
                break

        self.log_callback("finish game")
        pygame.quit()

    def log_callback(self, log_text):
        print(log_text)

    def create_game_model(self):
        try:
            self.sudoku_model = SudokuLogic()
        except Exception as e:
            print(e)
            self.running = False

    def restart_game(self):
        del self.sudoku_model
        # create new game model
        self.create_game_model()

        # reset gui values
        self.sudoku_gui.reset_table(self.sudoku_model.game_board)

    #def clean_board():
    #    pass
    #def check_results():
    #    pass

if __name__ == "__main__":
    game = SudokuGame()
    game.run_game()
