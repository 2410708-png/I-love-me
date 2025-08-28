pip install pygame
import pygame
import random

# --- 게임 설정 ---
WINDOW_WIDTH, WINDOW_HEIGHT = 300, 600
GRID_SIZE = 30
COLS, ROWS = WINDOW_WIDTH // GRID_SIZE, WINDOW_HEIGHT // GRID_SIZE

# 색상 정의
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # I
    (255, 255, 0),  # O
    (128, 0, 128),  # T
    (255, 165, 0),  # L
    (0, 0, 255),    # J
    (0, 255, 0),    # S
    (255, 0, 0)     # Z
]

# --- 블록 정의 ---
SHAPES = [
    [[1, 1, 1, 1]],                       # I
    [[1, 1], [1, 1]],                     # O
    [[0, 1, 0], [1, 1, 1]],               # T
    [[1, 0, 0], [1, 1, 1]],               # L
    [[0, 0, 1], [1, 1, 1]],               # J
    [[0, 1, 1], [1, 1, 0]],               # S
    [[1, 1, 0], [0, 1, 1]]                # Z
]


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)


def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (col, row), color in locked_positions.items():
        if row >= 0:
            grid[row][col] = color
    return grid


def convert_shape_format(piece):
    positions = []
    shape_format = piece.image()

    for i, row in enumerate(shape_format):
        for j, val in enumerate(row):
            if val == 1:
                positions.append((piece.x + j, piece.y + i))
    return positions


def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(COLS) if grid[i][j] == BLACK] for i in range(ROWS)]
    accepted_positions = [j for sub in accepted_positions for j in sub]

    formatted = convert_shape_format(piece)
    for pos in formatted:
        if pos not in accepted_positions and pos[1] >= 0:
            return False
    return True


def check_lost(positions):
    for (col, row) in positions:
        if row < 1:
            return True
    return False


def get_shape():
    return Piece(COLS // 2 - 2, 0, random.choice(SHAPES))


def clear_rows(grid, locked):
    cleared = 0
    for i in range(ROWS - 1, -1, -1):
        if BLACK not in grid[i]:
            cleared += 1
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except:
                    continue
            for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
                x, y = key
                if y < i:
                    locked[(x, y + 1)] = locked.pop((x, y))
    return cleared


def draw_grid(surface, grid):
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, grid[i][j], (j * GRID_SIZE, i * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)

    # 격자선
    for i in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, i * GRID_SIZE), (WINDOW_WIDTH, i * GRID_SIZE))
    for j in range(COLS):
        pygame.draw.line(surface, GRAY, (j * GRID_SIZE, 0), (j * GRID_SIZE, WINDOW_HEIGHT))


def draw_next_shape(piece, surface):
    font = pygame.font.SysFont("arial", 24)
    label = font.render("Next Shape", True, WHITE)

    start_x = WINDOW_WIDTH + 10
    start_y = WINDOW_HEIGHT // 2 - 100

    surface.blit(label, (start_x, start_y - 30))
    shape = piece.image()

    for i, row in enumerate(shape):
        for j, val in enumerate(row):
            if val == 1:
                pygame.draw.rect(surface, piece.color,
                                 (start_x + j * GRID_SIZE, start_y + i * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)


def draw_window(surface, grid, score=0, level=1):
    surface.fill(BLACK)
    draw_grid(surface, grid)

    font = pygame.font.SysFont("arial", 24)
    score_label = font.render(f"Score: {score}", True, WHITE)
    level_label = font.render(f"Level: {level}", True, WHITE)

    surface.blit(score_label, (WINDOW_WIDTH + 10, 20))
    surface.blit(level_label, (WINDOW_WIDTH + 10, 60))


def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0

    score = 0
    level = 1
    speed = 0.5

    screen = pygame.display.set_mode((WINDOW_WIDTH + 200, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris")

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        shape_pos = convert_shape_format(current_piece)
        for x, y in shape_pos:
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                score += cleared * 100
                if score // 500 >= level:  # 500점마다 레벨업
                    level += 1
                    speed = max(0.1, speed - 0.05)

        draw_window(screen, grid, score, level)
        draw_next_shape(next_piece, screen)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    main()
