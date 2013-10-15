from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename
from panda3d.core import Texture

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

        # configure boxes and textures
        self.box = [[None for x in range(CELL_WIDTH)] for x in range(CELL_HEIGHT)]
        self.textureempty = self.loader.loadTexture(mydir + '/../textures/box.png')
        self.texturefull = self.loader.loadTexture(mydir + '/../textures/boxfull.png')

        self.textureempty.setMagfilter(Texture.FTLinear)
        self.textureempty.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texturefull.setMagfilter(Texture.FTLinear)
        self.texturefull.setMinfilter(Texture.FTLinearMipmapLinear)

        for row in range(CELL_HEIGHT):
            for col in range(CELL_WIDTH):
                box = self.loader.loadModel(mydir + '/../models/cube')
                box.reparentTo(self.render)
                box.setPos((CELL_WIDTH * -1) + (col * 2), 200, CELL_HEIGHT - (row * 2))
                box.setTexture(self.textureempty)

                self.box[row][col] = box

        # configure cell data
        self.cells = [[0 for x in range(CELL_WIDTH)] for x in range(CELL_HEIGHT)]
        self.cells[3][6] = 1
        self.cells[4][7] = 1
        self.cells[5][5] = 1
        self.cells[5][6] = 1
        self.cells[5][7] = 1

        self.editmode = False

        taskMgr.add(self.start, 'start')

        # setup event handling
        self.accept('enter', self.handleenter)
        self.accept('escape', sys.exit)

    def start(self, task):
        if not self.editmode:
            self.processcells(self.cells)

        for row in range(CELL_HEIGHT):
            for col in range(CELL_WIDTH):
                if self.cells[row][col] == 1:
                    self.box[row][col].setTexture(self.texturefull)
                else:
                    self.box[row][col].setTexture(self.textureempty)

        return task.cont

    def handleenter(self):
        self.editmode = not self.editmode
        #    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and editMode:
        #        row = event.pos[1] / (SCREEN_HEIGHT / CELL_HEIGHT)
        #        col = event.pos[0] / (SCREEN_WIDTH / CELL_WIDTH)
        #        cells[row][col] = (cells[row][col] + 1) % 2

    @staticmethod
    def countsiblingcells(cells, x, y):
        return cells[y-1][x-1] + \
            cells[y][x-1] + \
            cells[(y+1) % CELL_HEIGHT][x-1] + \
            cells[y-1][x] + \
            cells[(y+1) % CELL_HEIGHT][x] + \
            cells[y-1][(x+1) % CELL_WIDTH] + \
            cells[y][(x+1) % CELL_WIDTH] + \
            cells[(y+1) % CELL_HEIGHT][(x+1) % CELL_WIDTH]

    def processcells(self, cells):
        newcells = copy.deepcopy(cells)

        for row in range(CELL_HEIGHT):
            for col in range(CELL_WIDTH):
                neighbours = self.countsiblingcells(newcells, col, row)

                if newcells[row][col] == 1:
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