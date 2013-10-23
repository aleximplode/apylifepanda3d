from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename
from panda3d.core import Texture
from panda3d.core import CollisionNode
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionRay
from panda3d.core import BitMask32
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

        self.bgmusic = self.loader.loadMusic(mydir + '/../sounds/bgmusic.ogg')
        self.bgmusic.play()

        # Setup collision for 3d picking
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        # Make a collision node for our picker ray
        self.pickerNode = CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        #   relative to it
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        # Everything to be picked will use bit 1. This way if we were doing other
        #   collision we could separate it
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)
        #self.picker.showCollisions(render)

        # Configure boxes and textures
        self.box = [[None for x in range(CELL_WIDTH)] for x in range(CELL_HEIGHT)]
        self.textureempty = self.loader.loadTexture(mydir + '/../textures/box.png')
        self.texturefull = self.loader.loadTexture(mydir + '/../textures/boxfull.png')

        self.textureempty.setMagfilter(Texture.FTLinear)
        self.textureempty.setMinfilter(Texture.FTLinearMipmapLinear)
        self.texturefull.setMagfilter(Texture.FTLinear)
        self.texturefull.setMinfilter(Texture.FTLinearMipmapLinear)

        self.boxnode = render.attachNewNode('boxnode')

        for row in range(CELL_HEIGHT):
            for col in range(CELL_WIDTH):
                box = self.loader.loadModel(mydir + '/../models/cube')
                box.reparentTo(self.boxnode)
                box.setPos((CELL_WIDTH * -1) + (col * 2), 200, CELL_HEIGHT - (row * 2))
                box.setTexture(self.textureempty)

                # Cube is the name of the polygon set in blender
                box.find("**/Cube").node().setIntoCollideMask(BitMask32.bit(1))
                box.find("**/Cube").node().setTag('square', str(row) + '-' + str(col))

                self.box[row][col] = box

        # Configure cell data
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
        self.accept("mouse1", self.selectpiece)

    def selectpiece(self):
        if self.editmode:
            mpos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())

            #Do the actual collision pass (Do it only on the squares for
            #efficiency purposes)
            self.picker.traverse(self.boxnode)
            if self.pq.getNumEntries() > 0:
                # If we have hit something, sort the hits so that the closest
                #   is first, and highlight that node
                self.pq.sortEntries()
                tag = self.pq.getEntry(0).getIntoNode().getTag('square')
                tagsplit = tag.split('-')
                row = int(tagsplit[0])
                col = int(tagsplit[1])

                # Set the highlight on the picked square
                self.cells[row][col] = (0 if self.cells[row][col] == 1 else 1)

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

        if self.editmode:
            base.disableMouse()
        else:
            base.enableMouse()

    @staticmethod
    def countsiblingcells(cells, x, y):
        return cells[y - 1][x - 1] + \
               cells[y][x - 1] + \
               cells[(y + 1) % CELL_HEIGHT][x - 1] + \
               cells[y - 1][x] + \
               cells[(y + 1) % CELL_HEIGHT][x] + \
               cells[y - 1][(x + 1) % CELL_WIDTH] + \
               cells[y][(x + 1) % CELL_WIDTH] + \
               cells[(y + 1) % CELL_HEIGHT][(x + 1) % CELL_WIDTH]

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


app = Life()
app.run()