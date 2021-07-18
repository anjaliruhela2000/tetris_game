import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from modules.misc import *
from modules.shapes import *
from PyQt5.QtWidgets import QFrame

class InnerBoard():
    def __init__(self, width=10, height=22):
        self.width = width
        self.height = height
        self.reset()

    def ableMove(self, coord, direction=None):
        assert len(coord) == 2
        if direction is None:
            direction = self.current_direction
        for x, y in self.current_tetris.getAbsoluteCoords(direction, coord[0], coord[1]):
            if x >= self.width or x < 0 or y >= self.height or y < 0:
                return False
            if self.getCoordValue([x, y]) > 0:
                return False
        return True

    def moveRight(self):
        if self.ableMove([self.current_coord[0]+1, self.current_coord[1]]):
            self.current_coord[0] += 1

    def moveLeft(self):
        if self.ableMove([self.current_coord[0]-1, self.current_coord[1]]):
            self.current_coord[0] -= 1

    def rotateClockwise(self):
        if self.ableMove(self.current_coord, (self.current_direction-1) % 4):
            self.current_direction = (self.current_direction-1) % 4

    def rotateAnticlockwise(self):
        if self.ableMove(self.current_coord, (self.current_direction+1) % 4):
            self.current_direction = (self.current_direction+1) % 4

    def moveDown(self):
        removed_lines = 0
        if self.ableMove([self.current_coord[0], self.current_coord[1]+1]):
            self.current_coord[1] += 1
        else:
            x_min, x_max, y_min, y_max = self.current_tetris.getRelativeBoundary(self.current_direction)
            if self.current_coord[1] + y_min < 0:
                self.is_gameover = True
                return removed_lines
            self.mergeTetris()
            removed_lines = self.removeFullLines()
            self.createNewTetris()
        return removed_lines

    def dropDown(self):
        removed_lines = 0
        while self.ableMove([self.current_coord[0], self.current_coord[1]+1]):
            self.current_coord[1] += 1
        x_min, x_max, y_min, y_max = self.current_tetris.getRelativeBoundary(self.current_direction)
        if self.current_coord[1] + y_min < 0:
            self.is_gameover = True
            return removed_lines
        self.mergeTetris()
        removed_lines = self.removeFullLines()
        self.createNewTetris()
        return removed_lines

    def mergeTetris(self):
        for x, y in self.current_tetris.getAbsoluteCoords(self.current_direction, self.current_coord[0], self.current_coord[1]):
            self.board_data[x + y*self.width] = self.current_tetris.shape
        self.current_coord = [-1, -1]
        self.current_direction = 0
        self.current_tetris = tetrisShape()

    def removeFullLines(self):
        new_board_data = [0]*self.width*self.height
        new_y = self.height - 1
        removed_lines = 0
        for y in range(self.height-1, -1, -1):
            cell_count = sum([1 if self.board_data[x + y*self.width] > 0 else 0 for x in range(self.width)])
            if cell_count < self.width:
                for x in range(self.width):
                    new_board_data[x + new_y*self.width] = self.board_data[x + y*self.width]
                new_y -= 1
            else:
                removed_lines += 1
        self.board_data = new_board_data
        return removed_lines

    def createNewTetris(self):
        x_min, x_max, y_min, y_max = self.next_tetris.getRelativeBoundary(0)
        if self.ableMove([self.init_x, -y_min]):
            self.current_coord = [self.init_x, -y_min]
            self.current_tetris = self.getNextTetris()
        else:
            self.is_gameover = True
        self.shape_statistics[self.current_tetris.shape] += 1

    def getNextTetris(self):
        return tetrisShape(random.randint(1, 7))

    def getBoardData(self):
        return self.board_data

    def getCoordValue(self, coord):
        return self.board_data[coord[0] + coord[1]*self.width]

    def getCurrentTetrisCoords(self):
        return self.current_tetris.getAbsoluteCoords(self.current_direction, self.current_coord[0], self.current_coord[1])

    def reset(self):
        self.board_data = [0]*self.width*self.height
        self.current_direction = 0
        self.current_coord = [-1, -1]
        self.next_tetris = self.getNextTetris()
        self.current_tetris = tetrisShape()
        self.is_gameover = False
        self.init_x = self.width//2
        self.shape_statistics = [0]*8

class ExternalBoard(QFrame):
    score_signal = pyqtSignal(str)
    def __init__(self, parent, grid_size, inner_board):
        super(ExternalBoard, self).__init__(parent)
        self.grid_size = grid_size
        self.inner_board = inner_board
        self.setFixedSize(grid_size*inner_board.width, grid_size*inner_board.height)
        self.initExternalBoard()

    def initExternalBoard(self):
        self.score = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        for x in range(self.inner_board.width):
            for y in range(self.inner_board.height):
                shape = self.inner_board.getCoordValue([x, y])
                drawCell(painter, x*self.grid_size, y*self.grid_size, shape, self.grid_size)
        for x, y in self.inner_board.getCurrentTetrisCoords():
            shape = self.inner_board.current_tetris.shape
            drawCell(painter, x*self.grid_size, y*self.grid_size, shape, self.grid_size)
        painter.setPen(QColor(0x777777))
        painter.drawLine(0, self.height()-1, self.width(), self.height()-1)
        painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
        painter.setPen(QColor(0xCCCCCC))
        painter.drawLine(self.width(), 0, self.width(), self.height())
        painter.drawLine(0, self.height(), self.width(), self.height())

    def updateData(self):
        self.score_signal.emit(str(self.score))
        self.update()

class sidePanel(QFrame):
    def __init__(self, parent, grid_size, inner_board):
        super(sidePanel, self).__init__(parent)
        self.grid_size = grid_size
        self.inner_board = inner_board
        self.setFixedSize(grid_size*5, grid_size*inner_board.height)
        self.move(grid_size*inner_board.width, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        x_min, x_max, y_min, y_max = self.inner_board.next_tetris.getRelativeBoundary(0)
        dy = 3*self.grid_size
        dx = (self.width() - (x_max - x_min)*self.grid_size)/2
        shape = self.inner_board.next_tetris.shape
        for x, y in self.inner_board.next_tetris.getAbsoluteCoords(0, 0, -y_min):
            drawCell(painter, x*self.grid_size + dx, y*self.grid_size + dy, shape, self.grid_size)

    def updateData(self):
        self.update()
