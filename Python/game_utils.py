import pygame
import sys

BLACK = (0, 0, 0)
WHITE = (230, 230, 230)
GRAY = (50,50,50)
ORANGE = (200,69,0)
GREEN = (0,200,0)
WINDOW_HEIGHT = 300
WINDOW_WIDTH = 500
font = None

pygame.init()
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
CLOCK = pygame.time.Clock()
SCREEN.fill(BLACK)

font = pygame.font.SysFont(None, 75)

def resetGrid():
    SCREEN.fill(BLACK)

def drawGrid(word_grid, result_grid, answer):
    global font

    # SCREEN.fill(BLACK)  # reset

    w = len(word_grid)
    h = len(word_grid[0])

    blockSize = 50 #Set the size of the grid block
    for x in range(0, w*blockSize, blockSize):
        for y in range(0, h*blockSize, blockSize):
            actualX = int(x/blockSize)
            actualY = int(y/blockSize)

            color = BLACK
            type = result_grid[actualX][actualY]
            if type == 0:
                color = GRAY
            elif type == 1:
                color = ORANGE
            elif type == 2:
                color = GREEN

            rect = pygame.draw.rect(SCREEN, color, (y, x, blockSize, blockSize))

            pygame.draw.rect(SCREEN, WHITE, rect, 1)

            img = font.render(word_grid[actualX][actualY], True, WHITE)
            SCREEN.blit(img, img.get_rect(center=rect.center))
    img = font.render(answer, True, WHITE)
    SCREEN.blit(img, (270, 0))


def show_game(word_grid, result_grid, answer):
    drawGrid(word_grid, result_grid, answer)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()