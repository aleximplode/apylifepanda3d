from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename
import os
import sys
import copy


# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
BG_COLOUR = (255, 255, 255)
CELL_WIDTH = 40
CELL_HEIGHT = 40


class Life(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)

        mydir = os.path.abspath(sys.path[0])
        mydir = Filename.fromOsSpecific(mydir).getFullpath()

        self.box = self.loader.loadModel(mydir + '/../models/cube')
        self.box.reparentTo(self.render)

        self.box.setScale(0.25, 0.25, 0.25)
        self.box.setPos(0, 8, 0)


#def start():
#    pygame.init()
#    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
#    clock = pygame.time.Clock()
#
#    cells = [[0 for x in range(CELL_WIDTH)] for x in range(CELL_HEIGHT)]
#
#    cells[3][6] = 1
#    cells[4][7] = 1
#    cells[5][5] = 1
#    cells[5][6] = 1
#    cells[5][7] = 1
#
#    editMode = False
#
#    while True:
#        deltaTime = clock.tick(15)
#
#        # Event handling
#        for event in pygame.event.get():
#            if event.type == pygame.QUIT:
#                pygame.quit()
#                sys.exit()
#            elif event.type == pygame.KEYUP:
#                if event.key == pygame.K_RETURN:
#                    editMode = not editMode
#            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and editMode:
#                row = event.pos[1] / (SCREEN_HEIGHT / CELL_HEIGHT)
#                col = event.pos[0] / (SCREEN_WIDTH / CELL_WIDTH)
#                cells[row][col] = (cells[row][col] + 1) % 2
#
#        if not editMode:
#            processCells(cells)
#
#        screen.fill(BG_COLOUR)
#
#        render(screen, cells)
#
#        pygame.display.flip()
#
#
def countSiblingCells(cells, x, y):
    return cells[y-1][x-1] + \
        cells[y][x-1] + \
        cells[(y+1) % CELL_HEIGHT][x-1] + \
        cells[y-1][x] + \
        cells[(y+1) % CELL_HEIGHT][x] + \
        cells[y-1][(x+1) % CELL_WIDTH] + \
        cells[y][(x+1) % CELL_WIDTH] + \
        cells[(y+1) % CELL_HEIGHT][(x+1) % CELL_WIDTH]

def processCells(cells):
    newCells = copy.deepcopy(cells)

    for row in range(CELL_HEIGHT):
        for col in range(CELL_WIDTH):
            neighbours = countSiblingCells(newCells, col, row)

            if newCells[row][col] == 1:
                if neighbours < 2:
                    cells[row][col] = 0
                elif 2 <= neighbours <= 3:
                    pass
                elif neighbours > 3:
                    cells[row][col] = 0
            else:
                if neighbours == 3:
                    cells[row][col] = 1

#def render(screen, cells):
#    for row in range(CELL_HEIGHT):
#        for col in range(CELL_WIDTH):
#            cell = pygame.Rect(col * (SCREEN_WIDTH / CELL_WIDTH), row * (SCREEN_HEIGHT / CELL_HEIGHT),
#                               SCREEN_WIDTH / CELL_WIDTH, SCREEN_HEIGHT / CELL_HEIGHT)
#            colour = (0, 0, 0)
#
#            border = 1
#            if cells[row][col] == 1:
#                border = 0
#
#            pygame.draw.rect(screen, colour, cell, border)


app = Life()
app.run()