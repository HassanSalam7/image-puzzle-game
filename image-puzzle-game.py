import pygame
import random
import tkinter as tk
from tkinter import filedialog
import heapq
import time

# Initialize Pygame and Tkinter
pygame.init()
root = tk.Tk()
root.withdraw()  # Hide the Tkinter main window

# Screen configuration
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 450
GRID_SIZE = 3  
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE
BACKGROUND_COLOR = (240, 240, 240)
BORDER_COLOR = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sliding Puzzle Game")

# Fonts
TITLE_FONT = pygame.font.Font(None, 48)
BUTTON_FONT = pygame.font.Font(None, 36)
MESSAGE_FONT = pygame.font.Font(None, 24)

class PuzzleGame:
    def __init__(self):
        self.tiles = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.tile_images = [None] * (GRID_SIZE * GRID_SIZE)
        self.original_image = None
        self.game_won = False
        self.solving_message = None
        self.solving_start_time = None

    def choose_image(self):
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

        if file_path:
            # Load and prepare image
            self.original_image = pygame.image.load(file_path)
            self.original_image = pygame.transform.scale(self.original_image, (SCREEN_WIDTH, SCREEN_WIDTH))

            # Reset game state
            self.reset_puzzle()

    def reset_puzzle(self):
        global TILE_SIZE
        TILE_SIZE = SCREEN_WIDTH // GRID_SIZE  #############
        self.tiles = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.tile_images = [None] * (GRID_SIZE * GRID_SIZE)
        self.game_won = False
        self.solving_message = None
        self.solving_start_time = None

        # Slice image into tiles
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if row == GRID_SIZE - 1 and col == GRID_SIZE - 1:
                    continue  # Leave last tile as empty
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile_image = self.original_image.subsurface(rect)
                tile_number = row * GRID_SIZE + col + 1
                self.tiles[row][col] = tile_number
                self.tile_images[tile_number - 1] = tile_image

        # Shuffle tiles
        self.shuffle_tiles()

    def shuffle_tiles(self):
        # Flatten the grid, remove the zero, shuffle, then reconstruct
        flat_tiles = [tile for row in self.tiles for tile in row if tile != 0]
        random.shuffle(flat_tiles)
        flat_tiles.append(0)

        # Reconstruct the grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.tiles[row][col] = flat_tiles[row * GRID_SIZE + col]

    def find_empty_tile(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.tiles[row][col] == 0:
                    return row, col

    def move_tile(self, direction):
        if self.game_won:
            return

        empty_row, empty_col = self.find_empty_tile()

        # Define possible move directions
        moves = {
            'UP': (1, 0),
            'DOWN': (-1, 0),
            'LEFT': (0, 1),
            'RIGHT': (0, -1)
        }

        dx, dy = moves[direction]
        new_row = empty_row + dx
        new_col = empty_col + dy

        # Check if move is valid
        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            # Swap tiles
            self.tiles[empty_row][empty_col], self.tiles[new_row][new_col] = \
                self.tiles[new_row][new_col], self.tiles[empty_row][empty_col]

        # Check win condition
        self.check_win()

    def check_win(self):
        expected = 1
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if row == GRID_SIZE - 1 and col == GRID_SIZE - 1:
                    break
                if self.tiles[row][col] != expected:
                    return False
                expected += 1
        self.game_won = True
        return True

    def draw(self):
        screen.fill(BACKGROUND_COLOR)

        # Draw tiles
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                tile_number = self.tiles[row][col]
                if tile_number != 0:
                    image = self.tile_images[tile_number - 1]
                    screen.blit(image, (col * TILE_SIZE, row * TILE_SIZE))
                    pygame.draw.rect(screen, BORDER_COLOR,
                                     (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

        # Draw "Choose Image" button
        pygame.draw.rect(screen, (100, 150, 250), (10, SCREEN_WIDTH + 10, 180, 40))
        button_text = BUTTON_FONT.render("Choose Image", True, WHITE)
        screen.blit(button_text, (20, SCREEN_WIDTH + 15))

        # Draw "Solve Puzzle" button
        pygame.draw.rect(screen, (150, 200, 100), (210, SCREEN_WIDTH + 10, 180, 40))
        ai_button_text = BUTTON_FONT.render("Solve Puzzle", True, WHITE)
        screen.blit(ai_button_text, (220, SCREEN_WIDTH + 15))

        # Draw solving message if applicable
        if self.solving_message:
            message_text = MESSAGE_FONT.render(self.solving_message, True, RED)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_WIDTH + 80))
            screen.blit(message_text, message_rect)

        # Draw win message if game is won
        if self.game_won:
            win_text = TITLE_FONT.render("You Won!", True, GREEN)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_WIDTH // 2))
            screen.blit(win_text, win_rect)

        pygame.display.flip()

    def solve_with_ai(self):
        # First, check if an image is loaded
        if not self.original_image:
            self.solving_message = "Please choose an image first!"
            self.solving_start_time = time.time()
            return

        def manhattan_distance(tiles):
            distance = 0
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    tile = tiles[row][col]
                    if tile != 0:  # Ignore the empty tile
                        correct_row = (tile - 1) // GRID_SIZE
                        correct_col = (tile - 1) % GRID_SIZE
                        distance += abs(row - correct_row) + abs(col - correct_col)
            return distance

        def tiles_to_tuple(tiles):
            return tuple(tuple(row) for row in tiles)

        def get_neighbors(tiles):
            neighbors = []
            empty_row, empty_col = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if tiles[r][c] == 0][0]
            moves = {'UP': (1, 0), 'DOWN': (-1, 0), 'LEFT': (0, 1), 'RIGHT': (0, -1)}

            for move, (dx, dy) in moves.items():
                new_row, new_col = empty_row + dx, empty_col + dy
                if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                    new_tiles = [row[:] for row in tiles]
                    new_tiles[empty_row][empty_col], new_tiles[new_row][new_col] = \
                        new_tiles[new_row][new_col], new_tiles[empty_row][empty_col]
                    neighbors.append((new_tiles, move))
            return neighbors

        def solve_puzzle(initial_tiles):
            # Check if the puzzle is already solved
            if all(initial_tiles[row][col] == row * GRID_SIZE + col + 1 
                   for row in range(GRID_SIZE) for col in range(GRID_SIZE) 
                   if not (row == GRID_SIZE - 1 and col == GRID_SIZE - 1)):
                return []

            open_set = []
            heapq.heappush(open_set, (0, initial_tiles, []))
            closed_set = set()
            
            # Implement a time limit to prevent infinite solving
            start_time = time.time()
            timeout = 10  # 10 seconds timeout

            while open_set:
                # Check timeout
                if time.time() - start_time > timeout:
                    self.solving_message = "Solving timed out! Puzzle too complex."
                    self.solving_start_time = time.time()
                    return None

                _, current_tiles, path = heapq.heappop(open_set)
                current_tuple = tiles_to_tuple(current_tiles)

                # Skip already visited states
                if current_tuple in closed_set:
                    continue
                closed_set.add(current_tuple)

                # Check win condition
                if all(current_tiles[row][col] == row * GRID_SIZE + col + 1 
                       for row in range(GRID_SIZE) for col in range(GRID_SIZE) 
                       if not (row == GRID_SIZE - 1 and col == GRID_SIZE - 1)):
                    return path

                # Explore neighbors
                for neighbor, move in get_neighbors(current_tiles):
                    neighbor_tuple = tiles_to_tuple(neighbor)
                    if neighbor_tuple not in closed_set:
                        new_path = path + [move]
                        priority = len(new_path) + manhattan_distance(neighbor)
                        heapq.heappush(open_set, (priority, neighbor, new_path))

            # No solution found
            self.solving_message = "No solution found!"
            self.solving_start_time = time.time()
            return None

        # Attempt to solve the puzzle
        solution = solve_puzzle(self.tiles)
        
        if solution:
            # Animate the solution
            for move in solution:
                pygame.time.delay(200)  # Small delay between moves
                self.move_tile(move)
                self.draw()
                pygame.display.flip()
                for event in pygame.event.get():  # Handle events during solving
                    if event.type == pygame.QUIT:
                        return
        elif solution is None:
            # Message is set in the solve_puzzle method
            pass

# Main game loop
def main():
    global TILE_SIZE
    TILE_SIZE = SCREEN_WIDTH // GRID_SIZE
    game = PuzzleGame()
    clock = pygame.time.Clock()
    running = True

    while running:
        # Clear temporary messages after 2 seconds
        if game.solving_start_time and time.time() - game.solving_start_time > 2:
            game.solving_message = None
            game.solving_start_time = None

        game.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.move_tile('UP')
                elif event.key == pygame.K_DOWN:
                    game.move_tile('DOWN')
                elif event.key == pygame.K_LEFT:
                    game.move_tile('LEFT')
                elif event.key == pygame.K_RIGHT:
                    game.move_tile('RIGHT')

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if 10 < mouse_x < 190 and SCREEN_WIDTH + 10 < mouse_y < SCREEN_WIDTH + 50:
                    game.choose_image()
                elif 210 < mouse_x < 390 and SCREEN_WIDTH + 10 < mouse_y < SCREEN_WIDTH + 50:
                    game.solve_with_ai()

        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()