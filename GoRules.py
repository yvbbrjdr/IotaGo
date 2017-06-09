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
        self.setBoardList(GoBoard.getEmptyBoardList())
        if boardList != None:
            self.setBoardList(boardList)

    def setBoardList(self, boardList):
        if not GoBoard.isValidBoardList(boardList):
            print "GoBoard: error: invalid boardList"
            return False
        self.__boardList = deepcopy(boardList)
        return True

    def getBoardList(self):
        return deepcopy(self.__boardList)

    def setSpot(self, x, y, value):
        if not isinstance(x, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: error: invalid x coordinate"
            return False
        if not isinstance(y, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: error: invalid y coordinate"
            return False
        if not isinstance(value, int) or not GoBoard.white <= value <= GoBoard.black:
            print "GoBoard: error: invalid value"
            return False
        self.__boardList[x][y] = value
        return True

    def getSpot(self, x, y):
        if not isinstance(x, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: error: invalid x coordinate"
            return None
        if not isinstance(y, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: error: invalid y coordinate"
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
            print "GoBoard: error: invalid x coordinate"
            return (0, [])
        if not isinstance(y, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: error: invalid y coordinate"
            return (0, [])
        color = self.__boardList[x][y]
        if color == GoBoard.space:
            return (0, [])
        spot = []
        liberty = 0
        vis = GoBoard.getEmptyBoardList()
        que = Queue()
        que.put((x, y))
        while not que.empty():
            cur = que.get()
            if not 0 <= cur[0] < GoBoard.size or not 0 <= cur[1] < GoBoard.size or self.__boardList[cur[0]][cur[1]] == - color or vis[cur[0]][cur[1]] == 1:
                continue
            vis[cur[0]][cur[1]] = 1
            if self.__boardList[cur[0]][cur[1]] == GoBoard.space:
                liberty += 1
            else:
                spot.append((cur[0], cur[1]))
                for d in GoBoard.dxdy:
                    que.put((cur[0] + d[0], cur[1] + d[1]))
        return (liberty, spot)

    def countLiberty(self):
        ret = GoBoard.getEmptyBoardList()
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if ret[i][j] == 0 and self.__boardList[i][j] != GoBoard.space:
                    bfs = self.bfsFloodFill(i, j)
                    for spot in bfs[1]:
                        ret[spot[0]][spot[1]] = bfs[0]
        return ret

    def captureSpot(self, exception = None):
        ret = GoBoard.getEmptyBoardList()
        liberty = self.countLiberty()
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if liberty[i][j] == 0 and self.__boardList[i][j] != GoBoard.space:
                    ret[i][j] = self.__boardList[i][j]
        if isinstance(exception, tuple) and len(exception) == 2 and isinstance(exception[0], int) and isinstance(exception[1], int):
            god = self.bfsFloodFill(exception[0], exception[1])
            for spot in god[1]:
                ret[spot[0]][spot[1]] = 0
        elif exception != None:
            print "GoBoard: error: invalid exception"
        return ret

    def capture(self, exception = None):
        spot = self.captureSpot(exception)
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if spot[i][j] != 0:
                    self.__boardList[i][j] = GoBoard.space

    def move(self, x, y, value):
        if not isinstance(x, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: error: invalid x coordinate"
            return False
        if not isinstance(y, int) or not 0 <= x < GoBoard.size:
            print "GoBoard: error: invalid y coordinate"
            return False
        if not isinstance(value, int) or not GoBoard.white <= value <= GoBoard.black:
            print "GoBoard: error: invalid value"
            return False
        if self.__boardList[x][y] != GoBoard.space:
            print "GoBoard: error: occupied spot"
            return False
        original = self.getBoardList()
        self.setSpot(x, y, value)
        self.capture((x, y))
        self.capture()
        if self.__boardList[x][y] == GoBoard.space:
            print "GoBoard: error: invalid move"
            self.setBoardList(original)
            return False
        self.__fourHistory[0], self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3] = self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3], (x, y, value)
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

    def featureBlack(self):
        ret = self.getBoardList()
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if ret[i][j] == GoBoard.white:
                    ret[i][j] = 0
        return ret

    def featureWhite(self):
        ret = self.getBoardList()
        for i in range(GoBoard.size):
            for j in range(GoBoard.size):
                if ret[i][j] == GoBoard.black:
                    ret[i][j] = 0
                elif ret[i][j] == GoBoard.white:
                    ret[i][j] = 1
        return ret

    def featureCurrent(self):
        if self.__fourHistory[3] == None:
            return GoBoard.getEmptyBoardList()
        elif self.__fourHistory[3][2] == GoBoard.black:
            return self.featureWhite()
        elif self.__fourHistory[3][2] == GoBoard.white:
            return self.featureBlack()

    def featureOpponent(self):
        if self.__fourHistory[3] == None:
            return GoBoard.getEmptyBoardList()
        elif self.__fourHistory[3][2] == GoBoard.black:
            return self.featureBlack()
        elif self.__fourHistory[3][2] == GoBoard.white:
            return self.featureWhite()

    def featureEmpty(self):
        return GoBoard.getEmptyBoardList()

    def featureAllOne(self):
        return [[1] * GoBoard.size for i in range(GoBoard.size)]

    def featureFourLiberty(self):
        pass

    def featureFourHistory(self):
        ret = []
        for i in range(4):
            mat = GoBoard.getEmptyBoardList()
            if self.__fourHistory[i] != None:
                mat[self.__fourHistory[i][0]][self.__fourHistory[i][1]] = 1
            ret.append(mat)
        return ret

    def featureIllegal(self):
        pass

    def featureFourCapture(self):
        pass

def main():
    GoBoard.size = 5
    board = GoBoard()
    value = GoBoard.black
    while True:
        x = raw_input('x: ')
        y = raw_input('y: ')
        if board.move(int(x), int(y), value):
            value = - value
        board.printBoard()

if __name__ == '__main__':
    main()
