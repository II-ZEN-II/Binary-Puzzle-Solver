import sys
import os
import time
import threading
import copy
import pygame

# custom library
from button import *

pygame.init()
clock = pygame.time.Clock()

# Window Setup
FPS = 60
RESOLUTION = (500,500)
SCREEN = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption('BINARY PUZZLE')

# Colours
WHITE = (240,240,240)
PINK = (242,5,116)
GREEN = (5,242,131)
LIGHT_GREY = (100,100,100)
GREY = (50,51,48)
DARK_GREY = (39,40,33)
BLACK = (22,23,20)

# Global Variables
puzzle_path = '14V.txt' # the filepath of the puzzle
debug_font = pygame.font.SysFont("Arial", 16)
debug_font_colour = (255,0,255)

# Classes
class Square():
    '''An object for each grid square'''

    # Colours
    inner_border_colour = WHITE
    hovered_colour = PINK
    uneditable_colour = LIGHT_GREY
    font_colour = WHITE
    
    possible_values = ('_','0','1') # possible values to cycle through when clicking

    def __init__(self, position, dimensions, border_width, font, value):
        self.font = font

        self.position = position
        self.dimensions = dimensions
        self.border_width = border_width

        self.value = value
        self.value_index = self.possible_values.index(self.value) # for cycling through values

        self.editable = (value  == '_') # bool if the square can be edited by the player
        self.hovered = False

        self.rect = pygame.Rect(position, dimensions)
        self.text_surface = font.render(self.value, True, self.font_colour)
        self.text_rect = self.text_surface.get_rect(center = self.rect.center) # stores text position 

    # Draws the square to the screen (called every frame)
    def draw(self, surface):
        if not self.editable:
            pygame.draw.rect(surface, self.uneditable_colour, self.rect)
        elif self.hovered:
            pygame.draw.rect(surface, self.hovered_colour, self.rect)
            self.hovered = False
        
        pygame.draw.rect(surface, self.inner_border_colour, self.rect, self.border_width)

        self.text_surface = self.font.render(self.value.replace('_',''), True, self.font_colour)
        self.text_rect = self.text_surface.get_rect(center = self.rect.center)
        surface.blit(self.text_surface, self.text_rect) 
        ## could this be optimised by drawing all of the text at once using surface.blits() ?
    
    # Cycles through possible values when left clicked and sets to 0 when right clicked
    def clicked(self, click_type):
        if self.editable:
            if click_type == 'LEFT':
                self.value_index = (self.value_index+1) % len(self.possible_values) # increments the value cyclically within the array's bounds
            elif click_type == 'RIGHT':
                self.value_index = 0
            self.value = self.possible_values[self.value_index] # redefines stored value


class Puzzle():
    '''An object for the puzzle'''

    # colours
    outer_border_colour = WHITE
    solved_border_colour = GREEN
    board_colour = DARK_GREY

    solve_delay = 0.01 # seconds
    max_draw_steps = 200 # max total iterations to solve without sacrificing visuals is this value -1 (525)
    total_solve_iterations = 525
    solved_board = None
    is_player_solve = False

    def __init__(self, path):
        self.input_path = os.path.join('puzzles', path)
        self.size, self.starting_board = self.load_puzzle()

        # dynamic UI based on window resolution
        self.grid_spacing = min(RESOLUTION) / 6
        self.button_spacing = self.grid_spacing / 2
        self.square_size = round(min((
            (RESOLUTION[0]-self.grid_spacing) / self.size,
            (RESOLUTION[1]-self.grid_spacing-self.button_spacing) / self.size
            )))
        
        self.board_dimensions = (self.size * self.square_size, self.size * self.square_size) 
        self.border_width = max(1, round(self.square_size / 24))
        self.outer_border_width = self.border_width * 3
        self.square_font = pygame.font.SysFont("Arial",round(self.square_size/2))

        # offset to center the board
        self.offset = (
            (RESOLUTION[0]-self.board_dimensions[0])/2,
            (RESOLUTION[1]-self.board_dimensions[1]-self.button_spacing)/2
            )
        
        # rectangles for the board
        self.board_rect = pygame.Rect(self.offset, self.board_dimensions)
        self.outer_border_rect = pygame.Rect(
            self.offset[0] - self.outer_border_width/2,
            self.offset[1] - self.outer_border_width/2,
            self.board_dimensions[0] + self.outer_border_width,
            self.board_dimensions[1] + self.outer_border_width)

        # store all the instatiated squares (2D Array/Matrix)
        self.board = self.create_squares(self.starting_board)

        # initial solve, stores total number of iterations and final solved board
        self.start_solve()

    # Loads puzzle from the given path, stores puzzle size and initial values
    def load_puzzle(self):
        file = open(self.input_path,'r')
        data = file.readlines()
        file.close()

        size = len(data)

        # stub
        if size % 2 != 0 or size < 6 or size > 14:
            print("Invalid Puzzle File")

        loaded_board = []
        for line in data:
            line = line.strip()
            line = line.replace(' ','')
            line = line.split(',')
            loaded_board.append(line)
        
        return size, loaded_board

    # Create and return all the squares
    def create_squares(self, loaded_board):
        matrix = []
        for y in range(self.size):
            row = []
            for x in range(self.size):
                square_pos = (x * self.square_size + self.offset[0], y * self.square_size + self.offset[1])
                square_size = (self.square_size,self.square_size)
                square_value = loaded_board[y][x]

                square = Square(
                    square_pos,
                    square_size,
                    self.border_width, 
                    self.square_font, 
                    square_value
                    )

                row.append(square)
            matrix.append(row)
        return matrix
    
    # Draws the board, outline and squares (called every frame)
    def update(self, surface, mouse_position, click_type):
        self.mouse_check(mouse_position, click_type)
        
        pygame.draw.rect(surface, self.board_colour, self.board_rect) # draws background
        

        # draw all squares
        for row in self.board:
            for square in row:
                square.draw(surface)

        # check if solved
        solved = (self.solved_board != None)
        if solved:
            for row in range(self.size):
                for column in range(self.size):
                    if self.board[row][column].value != self.solved_board[row][column]:
                        solved = False

        if solved:
            pygame.draw.rect(surface, self.solved_border_colour, self.outer_border_rect, self.outer_border_width) # draws puzzle outline
        else:
            pygame.draw.rect(surface, self.outer_border_colour, self.outer_border_rect, self.outer_border_width) # draws puzzle outline

    # Detects mouse hover and clicks
    def mouse_check(self, mouse_position, click_type):
        square_position = self.mouse_to_square(mouse_position)
        if square_position != None:
            self.board[square_position[1]][square_position[0]].hovered = True

            if click_type != None:
                self.board[square_position[1]][square_position[0]].clicked(click_type)
                   
    # Converts mouse position to matrix coordinates    
    def mouse_to_square(self,mouse_position):
        # if mouse cursor within board
        if self.board_rect.collidepoint(mouse_position):
            x = int((mouse_position[0]-self.offset[0]) / self.square_size)
            y = int((mouse_position[1]-self.offset[1]) / self.square_size)
            return (x,y)
        else:
            return None

    # Creates a new thread for solving and begins the solving process
    def start_solve(self):
        self.solved = False # stops thread once the puzzle is solved
        self.is_solving = True # prevents multiple threads at once

        self.solving_board = copy.deepcopy(self.starting_board)
        self.current_solve_iterations = 0

        self.stop_thread = False

        if __name__ == "__main__": # if the file that is run is this file
            self.solve_thread = threading.Thread(target=self.solve_manual, daemon=True)
            self.solve_thread.start()
            print('Thread Started')
        

    # Fills in squares using basic logic
    def solve_manual(self):
        board = self.solving_board
        empty = '_'
        fixed = True
        while fixed:
            print('Manual Looped')
            fixed = False
            for row in range(self.size):
                for column in range(self.size):
                    square = board[row][column]

                    if square != empty:
                        # horizontal two in a row
                        if column + 1 < self.size and square == board[row][column+1]:
                            if column > 0 and board[row][column-1] == empty:
                                board[row][column-1] = self.toggle(square)
                                self.draw_step(board)
                                fixed = True
                            if column < self.size -2 and board[row][column+2] == empty:
                                board[row][column+2] = self.toggle(square)
                                self.draw_step(board)
                                fixed = True
                        
                        #vertical two in a row
                        if row + 1 < self.size and square == board[row+1][column]:
                            if row > 0 and board[row-1][column] == empty:
                                board[row-1][column] = self.toggle(square)
                                self.draw_step(board)
                                fixed = True
                            if row < self.size -2 and board[row+2][column] == empty:
                                board[row+2][column] = self.toggle(square)
                                self.draw_step(board)
                                fixed = True
                        
                        #potential triplets horizontal
                        if column + 2 < self.size and square == board[row][column+2]:
                            if board[row][column+1] == empty:
                                board[row][column+1] = self.toggle(square)
                                self.draw_step(board)
                                fixed = True

                        #potential triplets vertical
                        if row + 2 < self.size and square == board[row+2][column]:
                            if board[row+1][column] == empty:
                                board[row+1][column] = self.toggle(square)
                                self.draw_step(board)
                                fixed = True

        print('Finished Manual')
        self.recursive_solve()

    # Searches for possible solutions to a given starting board using recursive backtracking
    def recursive_solve(self):
        if not self.stop_thread: # stops thread if needed
            for row in range(self.size): 
                for column in range(self.size):
                    if self.solving_board[row][column] == '_':
                        for number in range(2):
                            if not self.solved: #prevents the puzzle from being reset once the puzzle is solved
                                self.current_solve_iterations += 1
                                self.solving_board[row][column] = str(number) # tries new value

                                # draws frames evenly across iterations for a max of max_draw_steps (always draws last frame)
                                if (self.is_player_solve and 
                                        (self.current_solve_iterations % max(round(self.total_solve_iterations / (self.max_draw_steps/1.5)), 1) == 0 or
                                        self.current_solve_iterations == self.total_solve_iterations)):
                                    self.draw_step(self.solving_board)

                                # recurses if the new board is possible
                                if self.possible(self.solving_board, row, column, str(number)): # test if the new number is possible
                                    self.recursive_solve()
                                    
                                if not self.solved: # prevents the puzzle from being reset once the puzzle is solved
                                    self.solving_board[row][column] = '_'
                        return
                        
            self.solved = True
            self.is_solving = False

            self.total_solve_iterations = copy.deepcopy(self.current_solve_iterations)
            self.solved_board = copy.deepcopy(self.solving_board)
            print('Thread Finished | Iterations:', self.current_solve_iterations)

    # Draws the board during solve
    def draw_step(self, current_board):
        if self.is_player_solve:
            time.sleep(self.solve_delay)
            for row in range(self.size):
                for column in range(self.size):
                    self.board[row][column].value = current_board[row][column]
                    self.board[row][column].value_index = self.board[row][column].possible_values.index(current_board[row][column])
    
    # Checks if a given board state follows the rules of binary puzzles
    def possible(self, board, row, column, number):
        consecutiveX = 0 # 3 in a row x
        consecutiveY = 0 # 3 in a row y
        countX = 0 # amount in row
        countY = 0 # amount in column

        current_row = board[row]
        for i in range(self.size):
            # 3 in a row for rows & more than half total
            if current_row[i] == number: 
                consecutiveX += 1
                countX += 1
                if consecutiveX >= 3 or countX > self.size/2:
                    return False
            else: consecutiveX = 0
            
            # 3 in a row for columns & more than half total
            if board[i][column] == number: 
                consecutiveY += 1
                countY += 1
                if consecutiveY >= 3 or countY > self.size/2:
                    return False
            else: consecutiveY = 0
            
        # unique rows test
        times = 0
        if current_row.count('_') == 0:
            for i in board:
                if i.count('_') == 0:
                    if current_row == i:
                        times += 1
                        if times >= 2:
                            return False
        
        return True

    # Returns the opposite value (binary) if a value is given.
    def toggle(self, current):
        if current == '0':
            return '1'
        elif current == '1':
            return '0'
        else:
            return None

# Global Functions
def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = debug_font.render(fps, True, debug_font_colour)
    return fps_text

def restart_method(object):
    object.stop_thread = True
    main()

def solve_method(object):
    if not object.is_solving:
        object.is_player_solve = True
        object.start_solve()

# Scenes
def splash_screen():
    bg_colour = BLACK
    splash_font_colour = WHITE
    
    logo = pygame.image.load(os.path.join('assets','logo.png')).convert_alpha()

    # scale image to fit resolution
    scale_ratio = min(RESOLUTION[0]/logo.get_width(), RESOLUTION[1]/logo.get_height()) / 2
    logo = pygame.transform.scale(logo, (logo.get_width()*scale_ratio, logo.get_height()*scale_ratio)) 
    
    splash_font = pygame.font.Font(os.path.join('assets','font.ttf'), round(min(RESOLUTION)/20))
    splash_text_surface = splash_font.render("PRESS [ ENTER ] TO START", True, splash_font_colour)
    splash_text_rect = splash_text_surface.get_rect(center = (RESOLUTION[0]/2, RESOLUTION[1]/2 + logo.get_height()/1.5))
    
    idle = True
    
    # GAME LOOP
    while idle:
        SCREEN.fill(bg_colour)

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    idle = False
        
        # Visuals
        SCREEN.blit(logo, ((RESOLUTION[0]-logo.get_width()) / 2, (RESOLUTION[1]-logo.get_height()) / 2))
        SCREEN.blit(splash_text_surface, splash_text_rect)

        pygame.display.flip()
        clock.tick(FPS)
    
    # transition --> main game
    main()

def main():
    bg_colour = BLACK
    puzzle = Puzzle(puzzle_path)
    UI_font = pygame.font.Font(os.path.join('assets','font.ttf'), round(puzzle.button_spacing / 2.5))

    # Buttons
    button_width = (puzzle.outer_border_rect.width - puzzle.button_spacing/2) / 2
    button_height = puzzle.button_spacing

    restart_button = Button(
        "Restart [R]",
        (puzzle.outer_border_rect.left, puzzle.outer_border_rect.bottom + puzzle.button_spacing/2),
        (button_width, button_height),
        GREY,
        PINK,
        GREY,
        UI_font,
        WHITE
        )
    
    solve_button = Button(
        "Solve [S]",
        (puzzle.outer_border_rect.right - button_width, puzzle.outer_border_rect.bottom + puzzle.button_spacing/2),
        (button_width, button_height),
        GREY,
        GREEN,
        GREY,
        UI_font,
        WHITE
        )
    
    # GAME LOOP
    while True:
        SCREEN.fill(bg_colour)
        SCREEN.blit(update_fps(), (5,2))

        # Input
        mouse_position = pygame.mouse.get_pos()
        click_type = None

        for event in pygame.event.get():
            # window input
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_s:
                    solve_method(puzzle)
                if event.key == pygame.K_r:
                    restart_method(puzzle)

            # mouse input        
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_type = 'LEFT'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                click_type = 'RIGHT'

        # Visuals
        puzzle.update(SCREEN, mouse_position, click_type)

        restart_button.detect(mouse_position, restart_method, puzzle)
        solve_button.detect(mouse_position, solve_method, puzzle)
        restart_button.draw(SCREEN)
        solve_button.draw(SCREEN)
        
        pygame.display.flip()
        clock.tick(FPS)

# First scene to load
splash_screen()
#main()

