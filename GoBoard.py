#!/usr/bin/env python

from copy import deepcopy
from Queue import Queue

class GoBoard(object):

    size = 19
    black = 1
    space = 0
    white = -1
    printDic = {space : '.', black : 'B', white : 'W'}
    dxdy = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def __init__(self, boardList = None):
        self.__fourHistory = [None] * 4
        self.__hashHistory = []
        if boardList == None or not self.setBoardList(boardList):
            self.setBoardList(GoBoard.getEmptyBoardList())

    def setBoardList(self, boardList):
        if not GoBoard.isValidBoardList(boardList):
            print "GoBoard: setBoardList: error: invalid boardList"
            return False
        self.__boardList = deepcopy(boardList)
        return True

    def getBoardList(self):
        return deepcopy(self.__boardList)

    def setSpot(self, x, y, value):
        if not isinstance(x, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: setSpot: error: invalid x coordinate"
            return False
        if not isinstance(y, int) or not 0 <= y < GoBoard.size:
            print "GoBoard: setSpot: error: invalid y coordinate"
            return False
        if not isinstance(value, int) or not GoBoard.white <= value <= GoBoard.black:
            print "GoBoard: setSpot: error: invalid value"
            return False
        self.__boardList[x][y] = value
        return True

    def getSpot(self, x, y):
        if not isinstance(x, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: getSpot: error: invalid x coordinate"
            return None
        if not isinstance(y, int) or not 0 <= y < GoBoard.size:
            print "GoBoard: getSpot: error: invalid y coordinate"
            return None
        return self.__boardList[x][y]

    def printBoard(self):
        for row in self.__boardList:
            for spot in row:
                print GoBoard.printDic[spot],
            print

    def hash(self):
        s = ''
        for row in self.__boardList:
            for spot in row:
                s += str(spot + 1)
        return long(s, 3)

    def bfsFloodFill(self, x, y):
        if not isinstance(x, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: bfsFloodFill: error: invalid x coordinate"
            return ([], [])
        if not isinstance(y, int) or not 0 <= y < GoBoard.size:
            print "GoBoard: bfsFloodFill: error: invalid y coordinate"
            return ([], [])
        color = self.__boardList[x][y]
        if color == GoBoard.space:
            return ([], [])
        stonespot = []
        libertyspot = []
        vis = GoBoard.getEmptyBoardList()
        que = Queue()
        que.put((x, y))
        while not que.empty():
            cur = que.get()
            if not 0 <= cur[0] < GoBoard.size or not 0 <= cur[1] < GoBoard.size or self.__boardList[cur[0]][cur[1]] == - color or vis[cur[0]][cur[1]] == 1:
                continue
            vis[cur[0]][cur[1]] = 1
            if self.__boardList[cur[0]][cur[1]] == GoBoard.space:
                libertyspot.append((cur[0], cur[1]))
            else:
                stonespot.append((cur[0], cur[1]))
                for d in GoBoard.dxdy:
                    que.put((cur[0] + d[0], cur[1] + d[1]))
        return (stonespot, libertyspot)

    def countLiberty(self):
        ret = [[-1] * GoBoard.size for i in range(GoBoard.size)]
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if ret[i][j] == -1 and self.__boardList[i][j] != GoBoard.space:
                    bfs = self.bfsFloodFill(i, j)
                    liberty = len(bfs[1])
                    for spot in bfs[0]:
                        ret[spot[0]][spot[1]] = liberty
                elif self.__boardList[i][j] == GoBoard.space:
                    ret[i][j] = 0
        return ret

    def captureSpot(self, exception = None):
        ret = []
        mat = GoBoard.getEmptyBoardList()
        liberty = self.countLiberty()
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if liberty[i][j] == 0 and self.__boardList[i][j] != GoBoard.space:
                    mat[i][j] = 1
        if isinstance(exception, tuple) and len(exception) == 2:
            god = self.bfsFloodFill(exception[0], exception[1])
            for spot in god[0]:
                mat[spot[0]][spot[1]] = 0
        elif exception != None:
            print "GoBoard: captureSpot: error: invalid exception"
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if mat[i][j] == 1:
                    ret.append((i, j))
        return ret

    def capture(self, exception = None):
        spots = self.captureSpot(exception)
        for spot in spots:
            self.__boardList[spot[0]][spot[1]] = GoBoard.space

    def isValidMove(self, x, y, color):
        if not isinstance(x, int) or not 0 <= x < GoBoard.size or not isinstance(y, int) or not 0 <= y < GoBoard.size or not isinstance(color, int) or color != GoBoard.white and color != GoBoard.black or self.__boardList[x][y] != GoBoard.space:
            return False
        for k in GoBoard.dxdy:
            i = x + k[0]
            j = y + k[1]
            if 0 <= i < GoBoard.size and 0 <= j < GoBoard.size and self.__boardList[i][j] == GoBoard.space:
                return True
        tempBoard = GoBoard(self.__boardList)
        tempBoard.setSpot(x, y, color)
        tempBoard.capture((x, y))
        if len(tempBoard.bfsFloodFill(x, y)[1]) == 0:
            return False
        if tempBoard.hash() in self.__hashHistory:
            return False
        return True

    def move(self, x, y, color):
        if not isinstance(x, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: move: error: invalid x coordinate"
            return False
        if not isinstance(y, int) or not 0 <= y < GoBoard.size:
            print "GoBoard: move: error: invalid y coordinate"
            return False
        if not isinstance(color, int) or color != GoBoard.white and color != GoBoard.black:
            print "GoBoard: move: error: invalid color"
            return False
        if self.__boardList[x][y] != GoBoard.space:
            print "GoBoard: move: error: occupied spot"
            return False
        for k in GoBoard.dxdy:
            i = x + k[0]
            j = y + k[1]
            if 0 <= i < GoBoard.size and 0 <= j < GoBoard.size and self.__boardList[i][j] == GoBoard.space:
                self.setSpot(x, y, color)
                self.capture()
                self.__fourHistory[0], self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3] = self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3], (x, y, color)
                self.__hashHistory.append(self.hash())
                return True
        tempBoard = GoBoard(self.__boardList)
        tempBoard.setSpot(x, y, color)
        tempBoard.capture((x, y))
        if len(tempBoard.bfsFloodFill(x, y)[1]) == 0:
            print "GoBoard: move: error: invalid move"
            return False
        if tempBoard.hash() in self.__hashHistory:
            print "GoBoard: move: error: reappeared state"
            return False
        self.setBoardList(tempBoard.getBoardList())
        self.__fourHistory[0], self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3] = self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3], (x, y, color)
        self.__hashHistory.append(self.hash())
        return True

    @staticmethod
    def isValidBoardList(boardList):
        if not isinstance(boardList, list) or len(boardList) != GoBoard.size:
            return False
        for row in boardList:
            if not isinstance(row, list) or len(row) != GoBoard.size:
                return False
            for spot in row:
                if not isinstance(spot, int) or not GoBoard.white <= spot <= GoBoard.black:
                    return False
        return True

    @staticmethod
    def getEmptyBoardList():
        return [[GoBoard.space] * GoBoard.size for i in range(GoBoard.size)]

    def featureColor(self, color):
        if not isinstance(color, int) or not GoBoard.white <= color <= GoBoard.black:
            print "GoBoard: featureColor: error: invalid color"
            return GoBoard.getEmptyBoardList()
        ret = GoBoard.getEmptyBoardList()
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if self.__boardList[i][j] == color:
                    ret[i][j] = 1
        return ret

    def featureCurrent(self):
        if self.__fourHistory[3] == None:
            return GoBoard.getEmptyBoardList()
        else:
            return self.featureColor(- self.__fourHistory[3][2])

    def featureOpponent(self):
        if self.__fourHistory[3] == None:
            return GoBoard.getEmptyBoardList()
        else:
            return self.featureColor(self.__fourHistory[3][2])

    def featureEmpty(self):
        return self.featureColor(GoBoard.space)

    def featureAllZeros(self):
        return GoBoard.getEmptyBoardList()

    def featureAllOnes(self):
        return [[1] * GoBoard.size for i in range(GoBoard.size)]

    def featureFourLiberty(self):
        ret = [GoBoard.getEmptyBoardList() for i in range(8)]
        color = GoBoard.black
        if self.__fourHistory[3] != None:
            color = - self.__fourHistory[3][2]
        liberty = self.countLiberty()
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if self.__boardList[i][j] == color:
                    if liberty[i][j] == 1:
                        ret[0][i][j] = 1
                    elif liberty[i][j] == 2:
                        ret[1][i][j] = 1
                    elif liberty[i][j] == 3:
                        ret[2][i][j] = 1
                    elif liberty[i][j] >= 4:
                        ret[3][i][j] = 1
                elif self.__boardList[i][j] == - color:
                    if liberty[i][j] == 1:
                        ret[4][i][j] = 1
                    elif liberty[i][j] == 2:
                        ret[5][i][j] = 1
                    elif liberty[i][j] == 3:
                        ret[6][i][j] = 1
                    elif liberty[i][j] >= 4:
                        ret[7][i][j] = 1
        return ret

    def featureFourHistory(self):
        ret = []
        for i in range(4):
            mat = GoBoard.getEmptyBoardList()
            if self.__fourHistory[i] != None:
                mat[self.__fourHistory[i][0]][self.__fourHistory[i][1]] = 1
            ret.append(mat)
        return ret

    def featureIllegal(self):
        ret = GoBoard.getEmptyBoardList()
        color = GoBoard.black
        if self.__fourHistory[3] != None:
            color = - self.__fourHistory[3][2]
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if not self.isValidMove(i, j, color):
                    ret[i][j] = 1
        return ret

    def featureFourCapture(self):
        ret = [GoBoard.getEmptyBoardList() for i in range(4)]
        color = GoBoard.black
        if self.__fourHistory[3] != None:
            color = - self.__fourHistory[3][2]
        vis = GoBoard.getEmptyBoardList()
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if vis[i][j] == 0 and self.__boardList[i][j] == - color:
                    bfs = self.bfsFloodFill(i, j)
                    if len(bfs[1]) == 1:
                        x = bfs[1][0][0]
                        y = bfs[1][0][1]
                        self.setSpot(x, y, color)
                        count = len(self.captureSpot((x, y)))
                        if count == 1:
                            ret[0][x][y] = 1
                        elif count == 2:
                            ret[1][x][y] = 1
                        elif count == 3:
                            ret[2][x][y] = 1
                        elif count >= 4:
                            ret[3][x][y] = 1
                        self.setSpot(x, y, GoBoard.space)
                    for spot in bfs[0]:
                        vis[spot[0]][spot[1]] = 1
        return ret

    def allFeatures(self):
        ret = []
        ret.append(self.featureCurrent())
        ret.append(self.featureOpponent())
        ret.append(self.featureEmpty())
        ret.append(self.featureAllZeros())
        ret.append(self.featureAllOnes())
        ret += self.featureFourLiberty()
        ret += self.featureFourHistory()
        ret.append(self.featureIllegal())
        ret += self.featureFourCapture()
        return ret

def rPrint(arg):
    if isinstance(arg, list):
        for item in arg:
            rPrint(item)
        print
    else:
        print arg,

def test():
    GoBoard.size = int(raw_input('Board size: '))
    board = GoBoard()
    color = GoBoard.black
    while True:
        board.printBoard()
        if color == GoBoard.black:
            print "Black's turn"
        else:
            print "White's turn"
        x = raw_input('x: ')
        y = raw_input('y: ')
        if x == '' and y == '':
            color = - color
            continue
        if board.move(int(x), int(y), color):
            board.printBoard()
            while True:
                feature = raw_input('Feature: ')
                if feature == '':
                    break
                if hasattr(board, 'feature' + feature):
                    rPrint(getattr(board, 'feature' + feature)())
                else:
                    print "Feature not found!"
            color = - color

if __name__ == '__main__':
    test()
