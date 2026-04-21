import pygame
import random
from enum import Enum

pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 20
GAME_AREA_LEFT = 50
GAME_AREA_TOP = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

PIECE_COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

class Tetromino(Enum):
    I = 0
    O = 1
    T = 2
    S = 3
    Z = 4
    J = 5
    L = 6

# SRS (Super Rotation System) rotation data
ROTATIONS = {
    Tetromino.I: [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(1, -1), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, -1), (2, 0), (2, 1), (2, 2)]
    ],
    Tetromino.O: [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)]
    ],
    Tetromino.T: [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)]
    ],
    Tetromino.S: [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)]
    ],
    Tetromino.Z: [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)]
    ],
    Tetromino.J: [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)]
    ],
    Tetromino.L: [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)]
    ]
}

class Piece:
    def __init__(self, tetromino_type):
        self.type = tetromino_type
        self.rotation = 0
        self.x = 3
        self.y = 0
        self.color = PIECE_COLORS[tetromino_type.value]

    def get_blocks(self):
        rotations = ROTATIONS[self.type]
        rotation_data = rotations[self.rotation % len(rotations)]
        return [(self.x + dx, self.y + dy) for dx, dy in rotation_data]

    def rotate(self):
        rotations = ROTATIONS[self.type]
        self.rotation = (self.rotation + 1) % len(rotations)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.spawn_piece()
        self.next_piece = self.spawn_piece()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.font = pygame.font.Font(None, 36)

    def spawn_piece(self):
        return Piece(random.choice(list(Tetromino)))

    def is_valid_move(self, piece):
        for x, y in piece.get_blocks():
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def place_piece(self):
        for x, y in self.current_piece.get_blocks():
            if y >= 0:
                self.grid[y][x] = self.current_piece.color

    def clear_lines(self):
        rows_to_clear = [i for i in range(GRID_HEIGHT) if all(self.grid[i])]
        lines = len(rows_to_clear)
        if lines:
            for i in rows_to_clear:
                del self.grid[i]
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])
            self.lines_cleared += lines
            self.score += [40, 100, 300, 1200][lines - 1] * self.level
            self.level = 1 + self.lines_cleared // 10

    def update(self):
        self.current_piece.move(0, 1)
        if not self.is_valid_move(self.current_piece):
            self.current_piece.move(0, -1)
            self.place_piece()
            self.clear_lines()
            self.current_piece = self.next_piece
            self.next_piece = self.spawn_piece()
            if not self.is_valid_move(self.current_piece):
                return False
        return True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.current_piece.move(-1, 0)
                    if not self.is_valid_move(self.current_piece):
                        self.current_piece.move(1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.current_piece.move(1, 0)
                    if not self.is_valid_move(self.current_piece):
                        self.current_piece.move(-1, 0)
                elif event.key == pygame.K_UP:
                    self.current_piece.rotate()
                    if not self.is_valid_move(self.current_piece):
                        self.current_piece.rotate()
                        self.current_piece.rotate()
                        self.current_piece.rotate()
        return True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(GAME_AREA_LEFT + x * CELL_SIZE,
                                  GAME_AREA_TOP + y * CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x], rect)

        # Draw current piece
        for x, y in self.current_piece.get_blocks():
            if y >= 0:
                rect = pygame.Rect(GAME_AREA_LEFT + x * CELL_SIZE,
                                  GAME_AREA_TOP + y * CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, self.current_piece.color, rect)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(score_text, (GAME_AREA_LEFT + GRID_WIDTH * CELL_SIZE + 30, 50))
        self.screen.blit(level_text, (GAME_AREA_LEFT + GRID_WIDTH * CELL_SIZE + 30, 100))
        self.screen.blit(lines_text, (GAME_AREA_LEFT + GRID_WIDTH * CELL_SIZE + 30, 150))

        # Draw next piece preview
        next_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (GAME_AREA_LEFT + GRID_WIDTH * CELL_SIZE + 30, 200))
        for x, y in self.next_piece.get_blocks():
            rect = pygame.Rect(GAME_AREA_LEFT + GRID_WIDTH * CELL_SIZE + 30 + x * CELL_SIZE,
                              250 + y * CELL_SIZE,
                              CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, self.next_piece.color, rect)

        pygame.display.flip()

    def run(self):
        running = True
        drop_time = 0
        drop_speed = max(100, 1000 - self.level * 50)

        while running:
            dt = self.clock.tick(60) / 1000
            drop_time += dt * 1000

            running = self.handle_input()
            if drop_time >= drop_speed:
                running = self.update() and running
                drop_speed = max(100, 1000 - self.level * 50)
                drop_time = 0

            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()