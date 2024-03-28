import pygame
import random

palette = [
    (10, 10, 10),
    (130, 45, 175),
    (105, 175, 175),
    (75, 35, 30),
    (75, 130, 25),
    (175, 35, 25),
    (175, 45, 115),
]


class Block:
    posX = 0
    posY = 0

    block_shapes = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, posX, posY):
        self.posX = posX
        self.posY = posY
        self.shape = random.randint(0, len(self.block_shapes) - 1)
        self.color = random.randint(1, len(palette) - 1)
        self.rotation_state = 0

    def current_shape(self):
        return self.block_shapes[self.shape][self.rotation_state]

    def rotate_shape(self):
        self.rotation_state = (self.rotation_state + 1) % len(self.block_shapes[self.shape])


class Pytris:
    def __init__(self, height, width):
        self.score = 0
        self.game_state = "start"
        self.grid = []
        self.height = height
        self.width = width
        self.init_game()

    def init_game(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.current_block = None
        self.score = 0
        self.game_state = "start"

    def spawn_block(self):
        self.current_block = Block(3, 0)

    def check_collision(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.current_block.current_shape():
                    if i + self.current_block.posY > self.height - 1 or \
                            j + self.current_block.posX > self.width - 1 or \
                            j + self.current_block.posX < 0 or \
                            self.grid[i + self.current_block.posY][j + self.current_block.posX] > 0:
                        return True
        return False

    def remove_lines(self):
        lines_removed = 0
        for row in range(1, self.height):
            if 0 not in self.grid[row]:
                lines_removed += 1
                del self.grid[row]
                self.grid.insert(0, [0 for _ in range(self.width)])
        self.score += lines_removed ** 2

    def drop_block(self):
        self.current_block.posY += 1
        if self.check_collision():
            self.current_block.posY -= 1
            self.place_block()

    def place_block(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.current_block.current_shape():
                    self.grid[i + self.current_block.posY][j + self.current_block.posX] = self.current_block.color
        self.remove_lines()
        self.spawn_block()
        if self.check_collision():
            self.game_state = "game_over"

    def move_block(self, dx):
        starting_x = self.current_block.posX
        self.current_block.posX += dx
        if self.check_collision():
            self.current_block.posX = starting_x

    def rotate_block(self):
        previous_rotation = self.current_block.rotation_state
        self.current_block.rotate_shape()
        if self.check_collision():
            self.current_block.rotation_state = previous_rotation



pygame.init()


screen_size = (400, 500)
screen = pygame.display.set_mode(screen_size)

pygame.display.set_caption("Pytris")


is_running = False
game_clock = pygame.time.Clock()
game_fps = 25
game_instance = Pytris(20, 10)
frame_counter = 0

is_pressing_down = False

while not is_running:
    if game_instance.current_block is None:
        game_instance.spawn_block()
    frame_counter += 1
    if frame_counter > 100000:
        frame_counter = 0

    if frame_counter % (game_fps // 2) == 0 or is_pressing_down:
        if game_instance.game_state == "start":
            game_instance.drop_block()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game_instance.rotate_block()
            if event.key == pygame.K_DOWN:
                is_pressing_down = True
            if event.key == pygame.K_LEFT:
                game_instance.move_block(-1)
            if event.key == pygame.K_RIGHT:
                game_instance.move_block(1)
            if event.key == pygame.K_SPACE:
                game_instance.place_block()
            if event.key == pygame.K_ESCAPE:
                game_instance.init_game()

    if event.type == pygame.KEYUP:
        if event.key == pygame.K_DOWN:
            is_pressing_down = False

    screen.fill((255, 255, 255))  # White background


    for i in range(game_instance.height):
        for j in range(game_instance.width):
            pygame.draw.rect(screen, (128, 128, 128), [100 + 20 * j, 60 + 20 * i, 20, 20], 1)
            if game_instance.grid[i][j] > 0:
                pygame.draw.rect(screen, palette[game_instance.grid[i][j]],
                                 [101 + 20 * j, 61 + 20 * i, 18, 19])

    if game_instance.current_block is not None:
        for i in range(4):
            for j in range(4):
                if i * 4 + j in game_instance.current_block.current_shape():
                    pygame.draw.rect(screen, palette[game_instance.current_block.color],
                                     [101 + 20 * (j + game_instance.current_block.posX),
                                      61 + 20 * (i + game_instance.current_block.posY), 18, 18])


    score_font = pygame.font.SysFont('Calibri', 25, True, False)
    score_text = score_font.render("Score: " + str(game_instance.score), True, (0, 0, 0))
    screen.blit(score_text, [0, 0])


    if game_instance.game_state == "game_over":
        game_over_font = pygame.font.SysFont('Calibri', 65, True, False)
        game_over_text = game_over_font.render("Game Over", True, (255, 125, 0))
        restart_text = game_over_font.render("Press ESC", True, (255, 215, 0))
        screen.blit(game_over_text, [20, 200])
        screen.blit(restart_text, [25, 265])

    pygame.display.flip()
    game_clock.tick(game_fps)

pygame.quit()
