#!/usr/bin/env python

from copy import deepcopy
from queue import Queue
from pickle import dump, load
from colorama import init, Fore, Style

class GoBoard(object):

    black = 1
    space = 0
    white = -1
    featureCount = 26
    printDic = {space : '.', black : 'B', white : 'W'}
    colorDic = {space : Fore.WHITE + Style.BRIGHT, black : Fore.RED + Style.BRIGHT, white : Fore.WHITE + Style.BRIGHT, 'last' : Fore.CYAN + Style.BRIGHT, 'reset' : Style.RESET_ALL}
    dxdy = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def __init__(self, size = 19):
        init()
        if not isinstance(size, int) or size <= 0:
            raise Exception("GoBoard: __init__: error: invalid size")
        self.__size = size
        self.__fourHistory = [None] * 4
        self.__hashHistory = []
        self.__boardList = self.getEmptyBoardList()

    def save(self, filename):
        if not isinstance(filename, str):
            raise Exception("GoBoard: save: error: invalid filename")
        with open(filename, "wb") as f:
            dump(self.__dict__, f, 2)
        return True

    def load(self, filename):
        if not isinstance(filename, str):
            raise Exception("GoBoard: load: error: invalid filename")
        with open(filename, "rb") as f:
            self.__dict__.update(load(f))
        return True

    def getSize(self):
        return self.__size

    def getHistoryCount(self):
        return len(self.__hashHistory)

    def setBoardList(self, boardList):
        if not self.isValidBoardList(boardList):
            raise Exception("GoBoard: setBoardList: error: invalid boardList")
        self.__boardList = deepcopy(boardList)
        return True

    def getBoardList(self, history = None):
        if history == None:
            return deepcopy(self.__boardList)
        else:
            if not isinstance(history, int) or not 0 <= history < len(self.__hashHistory):
                raise Exception("GoBoard: getBoardList: error: invalid history")
            else:
                tempBoard = GoBoard(self.__size)
                tempBoard.setBoardListFromHash(self.__hashHistory[history])
                return tempBoard.getBoardList()

    def setSpot(self, x, y, value):
        if not isinstance(x, int) or not 0 <= x < self.__size:
            raise Exception("GoBoard: setSpot: error: invalid x coordinate")
        if not isinstance(y, int) or not 0 <= y < self.__size:
            raise Exception("GoBoard: setSpot: error: invalid y coordinate")
        if not isinstance(value, int) or not GoBoard.white <= value <= GoBoard.black:
            raise Exception("GoBoard: setSpot: error: invalid value")
        self.__boardList[x][y] = value
        return True

    def getSpot(self, x, y):
        if not isinstance(x, int) or not 0 <= x < self.__size:
            raise Exception("GoBoard: getSpot: error: invalid x coordinate")
        if not isinstance(y, int) or not 0 <= y < self.__size:
            raise Exception("GoBoard: getSpot: error: invalid y coordinate")
        return self.__boardList[x][y]

    def printBoard(self):
        print(GoBoard.colorDic[GoBoard.space] + '+' + '-' * (self.__size * 2 + 1) + '+')
        for i in range(self.__size):
            print(GoBoard.colorDic[GoBoard.space] + '|', end = ' ')
            for j in range(self.__size):
                if self.__fourHistory[3] != None and self.__fourHistory[3][0] == i and self.__fourHistory[3][1] == j:
                    print(GoBoard.colorDic['last'] + GoBoard.printDic[self.__boardList[i][j]], end = ' ')
                else:
                    print(GoBoard.colorDic[self.__boardList[i][j]] + GoBoard.printDic[self.__boardList[i][j]], end = ' ')
            print(GoBoard.colorDic[GoBoard.space] + '|')
        print(GoBoard.colorDic[GoBoard.space] + '+' + '-' * (self.__size * 2 + 1) + '+' + Style.RESET_ALL)

    def hash(self):
        s = ''
        for row in self.__boardList:
            for spot in row:
                s += str(spot + 1)
        return int(s, 3)

    def setBoardListFromHash(self, h):
        if not isinstance(h, int):
            raise Exception("GoBoard: setBoardListFromHash: error: invalid hash")
        s = ''
        while h > 0:
            s = str(h % 3) + s
            h /= 3
        if len(s) < self.__size ** 2:
            s = '0' * (self.__size ** 2 - len(s)) + s
        elif len(s) > self.__size ** 2:
            raise Exception("GoBoard: setBoardListFromHash: error: invalid hash")
        for i in range(self.__size):
            for j in range(self.__size):
                self.__boardList[i][j] = int(s[i * self.__size + j]) - 1
        return True

    def bfsFloodFill(self, x, y):
        if not isinstance(x, int) or not 0 <= x < self.__size:
            raise Exception("GoBoard: bfsFloodFill: error: invalid x coordinate")
        if not isinstance(y, int) or not 0 <= y < self.__size:
            raise Exception("GoBoard: bfsFloodFill: error: invalid y coordinate")
        color = self.__boardList[x][y]
        if color == GoBoard.space:
            return ([], [])
        stonespot = []
        libertyspot = []
        vis = self.getEmptyBoardList()
        que = Queue()
        que.put((x, y))
        while not que.empty():
            cur = que.get()
            if not 0 <= cur[0] < self.__size or not 0 <= cur[1] < self.__size or self.__boardList[cur[0]][cur[1]] == - color or vis[cur[0]][cur[1]] == 1:
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
        ret = [[-1] * self.__size for _ in range(self.__size)]
        for i in range(self.__size):
            for j in range(self.__size):
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
        mat = self.getEmptyBoardList()
        liberty = self.countLiberty()
        for i in range(self.__size):
            for j in range(self.__size):
                if liberty[i][j] == 0 and self.__boardList[i][j] != GoBoard.space:
                    mat[i][j] = 1
        if isinstance(exception, tuple) and len(exception) == 2:
            god = self.bfsFloodFill(exception[0], exception[1])
            for spot in god[0]:
                mat[spot[0]][spot[1]] = 0
        elif exception != None:
            raise Exception("GoBoard: captureSpot: error: invalid exception")
        for i in range(self.__size):
            for j in range(self.__size):
                if mat[i][j] == 1:
                    ret.append((i, j))
        return ret

    def capture(self, exception = None):
        spots = self.captureSpot(exception)
        for spot in spots:
            self.__boardList[spot[0]][spot[1]] = GoBoard.space

    def isValidMove(self, x, y, color):
        if not isinstance(x, int) or not 0 <= x < self.__size or not isinstance(y, int) or not 0 <= y < self.__size or not isinstance(color, int) or color != GoBoard.white and color != GoBoard.black or self.__boardList[x][y] != GoBoard.space:
            return False
        for k in GoBoard.dxdy:
            i = x + k[0]
            j = y + k[1]
            if 0 <= i < self.__size and 0 <= j < self.__size and self.__boardList[i][j] == GoBoard.space:
                return True
        tempBoard = GoBoard(self.__size)
        tempBoard.setBoardList(self.__boardList)
        tempBoard.setSpot(x, y, color)
        tempBoard.capture((x, y))
        if len(tempBoard.bfsFloodFill(x, y)[1]) == 0:
            return False
        if tempBoard.hash() in self.__hashHistory:
            return False
        return True

    def move(self, x, y, color):
        if not isinstance(x, int) or not 0 <= x < self.__size:
            raise Exception("GoBoard: move: error: invalid x coordinate")
        if not isinstance(y, int) or not 0 <= y < self.__size:
            raise Exception("GoBoard: move: error: invalid y coordinate")
        if not isinstance(color, int) or color != GoBoard.white and color != GoBoard.black:
            raise Exception("GoBoard: move: error: invalid color")
        if self.__boardList[x][y] != GoBoard.space:
            raise Exception("GoBoard: move: error: occupied spot")
        for k in GoBoard.dxdy:
            i = x + k[0]
            j = y + k[1]
            if 0 <= i < self.__size and 0 <= j < self.__size and self.__boardList[i][j] == GoBoard.space:
                self.__boardList[x][y] = color
                self.capture()
                self.__fourHistory[0], self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3] = self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3], (x, y, color)
                self.__hashHistory.append(self.hash())
                return True
        tempBoard = GoBoard(self.__size)
        tempBoard.setBoardList(self.__boardList)
        tempBoard.setSpot(x, y, color)
        tempBoard.capture((x, y))
        if len(tempBoard.bfsFloodFill(x, y)[1]) == 0:
            raise Exception("GoBoard: move: error: invalid move")
        if tempBoard.hash() in self.__hashHistory:
            raise Exception("GoBoard: move: error: reappeared state")
        self.__boardList = tempBoard.getBoardList()
        self.__fourHistory[0], self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3] = self.__fourHistory[1], self.__fourHistory[2], self.__fourHistory[3], (x, y, color)
        self.__hashHistory.append(self.hash())
        return True

    def isValidBoardList(self, boardList):
        if not isinstance(boardList, list) or len(boardList) != self.__size:
            return False
        for row in boardList:
            if not isinstance(row, list) or len(row) != self.__size:
                return False
            for spot in row:
                if not isinstance(spot, int) or not GoBoard.white <= spot <= GoBoard.black:
                    return False
        return True

    def getEmptyBoardList(self):
        return [[GoBoard.space] * self.__size for _ in range(self.__size)]

    def featureColor(self, color):
        if not isinstance(color, int) or not GoBoard.white <= color <= GoBoard.black:
            raise Exception("GoBoard: featureColor: error: invalid color")
        ret = self.getEmptyBoardList()
        for i in range(self.__size):
            for j in range(self.__size):
                if self.__boardList[i][j] == color:
                    ret[i][j] = 1
        return ret

    def featureCurrent(self):
        if self.__fourHistory[3] == None:
            return self.getEmptyBoardList()
        else:
            return self.featureColor(- self.__fourHistory[3][2])

    def featureOpponent(self):
        if self.__fourHistory[3] == None:
            return self.getEmptyBoardList()
        else:
            return self.featureColor(self.__fourHistory[3][2])

    def featureEmpty(self):
        return self.featureColor(GoBoard.space)

    def featureAllZeros(self):
        return self.getEmptyBoardList()

    def featureAllOnes(self):
        return [[1] * self.__size for _ in range(self.__size)]

    def featureFourLiberty(self):
        ret = [self.getEmptyBoardList() for _ in range(8)]
        color = GoBoard.black
        if self.__fourHistory[3] != None:
            color = - self.__fourHistory[3][2]
        liberty = self.countLiberty()
        for i in range(self.__size):
            for j in range(self.__size):
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
            mat = self.getEmptyBoardList()
            if self.__fourHistory[i] != None:
                mat[self.__fourHistory[i][0]][self.__fourHistory[i][1]] = 1
            ret.append(mat)
        return ret

    def featureIllegal(self):
        ret = self.getEmptyBoardList()
        color = GoBoard.black
        if self.__fourHistory[3] != None:
            color = - self.__fourHistory[3][2]
        for i in range(self.__size):
            for j in range(self.__size):
                if not self.isValidMove(i, j, color):
                    ret[i][j] = 1
        return ret

    def featureFourCapture(self):
        ret = [self.getEmptyBoardList() for _ in range(8)]
        color = GoBoard.black
        if self.__fourHistory[3] != None:
            color = - self.__fourHistory[3][2]
        vis = self.getEmptyBoardList()
        for i in range(self.__size):
            for j in range(self.__size):
                if vis[i][j] == 0 and self.__boardList[i][j] != GoBoard.space:
                    bfs = self.bfsFloodFill(i, j)
                    for spot in bfs[0]:
                        vis[spot[0]][spot[1]] = 1
                    if len(bfs[1]) == 1:
                        x = bfs[1][0][0]
                        y = bfs[1][0][1]
                        self.__boardList[x][y] = - self.__boardList[i][j]
                        count = len(self.captureSpot((x, y)))
                        self.__boardList[x][y] = GoBoard.space
                        if self.__boardList[i][j] == - color:
                            if not self.isValidMove(x, y, color):
                                continue
                            if count == 1:
                                ret[0][x][y] = 1
                            elif count == 2:
                                ret[1][x][y] = 1
                            elif count == 3:
                                ret[2][x][y] = 1
                            elif count >= 4:
                                ret[3][x][y] = 1
                        else:
                            if count == 1:
                                ret[4][x][y] = 1
                            elif count == 2:
                                ret[5][x][y] = 1
                            elif count == 3:
                                ret[6][x][y] = 1
                            elif count >= 4:
                                ret[7][x][y] = 1
        return ret

    def allFeatures(self):
        ret = [[[0] * GoBoard.featureCount for _ in range(self.__size)] for _ in range(self.__size)]
        tmp = []
        tmp.append(self.featureCurrent())
        tmp.append(self.featureOpponent())
        tmp.append(self.featureEmpty())
        tmp.append(self.featureAllZeros())
        tmp.append(self.featureAllOnes())
        tmp += self.featureFourLiberty()
        tmp += self.featureFourHistory()
        tmp.append(self.featureIllegal())
        tmp += self.featureFourCapture()
        for i in range(self.__size):
            for j in range(self.__size):
                for k in range(GoBoard.featureCount):
                    ret[i][j][k] = tmp[k][i][j]
        return ret

def rPrint(arg):
    if isinstance(arg, list):
        for item in arg:
            rPrint(item)
        print()
    else:
        print(arg, end = ' ')

def test():
    board = GoBoard(int(input('Board size: ')))
    color = GoBoard.black
    while True:
        board.printBoard()
        if color == GoBoard.black:
            print("Black's turn")
        else:
            print("White's turn")
        x = input('x: ')
        y = input('y: ')
        if x == '' and y == '':
            color = - color
            continue
        board.move(int(x), int(y), color)
        board.printBoard()
        while True:
            feature = input('Feature: ')
            if feature == '':
                break
            if hasattr(board, 'feature' + feature):
                rPrint(getattr(board, 'feature' + feature)())
            else:
                print("Feature not found!")
        color = - color

if __name__ == '__main__':
    test()
