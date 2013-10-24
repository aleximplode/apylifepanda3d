from direct.showbase.ShowBase import ShowBase
from panda3d.core import Filename
from panda3d.core import Texture
from panda3d.core import CollisionNode
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionHandlerQueue
from panda3d.core import CollisionRay
from panda3d.core import BitMask32
from panda3d.core import Point3
from direct.gui.OnscreenText import OnscreenText
from direct.interval.LerpInterval import LerpPosHprInterval
import os
import sys
import copy


# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
BG_COLOUR = (255, 255, 255)
CELL_WIDTH = 40
CELL_HEIGHT = 40
TRANSITIONPERIOD = 1.5


class Life(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        base.disableMouse()
        base.setFrameRateMeter(True)

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

        self.worldnode = render.attachNewNode('worldnode')
        self.boxnode = self.worldnode.attachNewNode('boxnode')

        self.worldnode.setPos(0, 200, 0)

        for row in range(CELL_HEIGHT):
            for col in range(CELL_WIDTH):
                box = self.loader.loadModel(mydir + '/../models/cube')
                box.reparentTo(self.boxnode)
                box.setPos((CELL_WIDTH * -1) + (col * 2), 0, CELL_HEIGHT - (row * 2))
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

        # Setup initial event handling
        self.accept('escape', sys.exit)
        self.accept('enter', self.startgame)
        self.accept('mouse1', self.startgame)

        # Prep the main screen
        self.boxnode.setPosHpr(self.worldnode, -5, -160, 0, 60, -25, 0)
        self.readyText = OnscreenText(text='Life', pos=(0.91, 0.7), scale=0.2, fg=(255, 255, 255, 255),
                                      shadow=(0, 0, 0, 100))

    def mouserotation(self, task):
        if not self.editmode and base.mouseWatcherNode.hasMouse():
            self.boxnode.setH(self.worldnode, base.mouseWatcherNode.getMouseX() * 60)
            self.boxnode.setP(self.worldnode, -base.mouseWatcherNode.getMouseY() * 60)

        return task.cont

    def startgame(self):
        # Transition to the game start state
        taskMgr.add(self.transition, 'transition')
        interval = LerpPosHprInterval(self.boxnode, TRANSITIONPERIOD, Point3(0, 0, 0), Point3(0, 0, 0),
                                      other=self.worldnode, blendType='easeInOut')
        interval.start()

    def transition(self, task):
        self.ignore('enter')
        self.ignore('mouse1')
        self.readyText.setFg((255, 255, 255, (max(0, TRANSITIONPERIOD - task.time) / TRANSITIONPERIOD)))
        self.readyText.setShadow((0, 0, 0, (max(0, TRANSITIONPERIOD - task.time) / TRANSITIONPERIOD)))

        if task.time > TRANSITIONPERIOD:
            self.accept('enter', self.handleenter)
            self.accept('mouse1', self.selectpiece)
            taskMgr.add(self.mouserotation, 'mouserotation')
            return task.done
        else:
            return task.cont

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