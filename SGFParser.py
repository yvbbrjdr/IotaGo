#!/usr/bin/env python

from GoBoard import GoBoard as gb

class SGFParser(object):

    spotDic = {
    'a' : 0, 'b' : 1, 'c' : 2, 'd' : 3, 'e' : 4,
    'f' : 5, 'g' : 6, 'h' : 7, 'i' : 8, 'j' : 9,
    'k' : 10, 'l' : 11, 'm' : 12, 'n' : 13, 'o' : 14,
    'p' : 15, 'q' : 16, 'r' : 17, 's' : 18
    }

    def __init__(self, filename = None):
        self.__moves = []
        self.__index = 0
        if filename != None:
            self.open(filename)

    def open(self, filename):
        self.__moves = []
        self.__index = 0
        if not isinstance(filename, str):
            raise Exception('SGFParser: open: error: invalid filename')
        with open(filename, 'r') as f:
            self.__moves = [s for s in f.read().split(';') if s[0] == 'B' or s[0] == 'W']

    def getNextMove(self):
        while True:
            if not self.hasNextMove():
                raise Exception('SGFParser: getNextMove: error: out of moves')
            move = self.__moves[self.__index]
            self.__index += 1
            color = gb.black
            if move[0] == 'W':
                color = gb.white
            if move[2] not in SGFParser.spotDic or move[3] not in SGFParser.spotDic:
                continue
            return (SGFParser.spotDic[move[3]], SGFParser.spotDic[move[2]], color)

    def hasNextMove(self):
        return self.__index < len(self.__moves)

def test():
    sgf = SGFParser(input('Filename: '))
    board = gb()
    while sgf.hasNextMove():
        move = sgf.getNextMove()
        board.move(move[0], move[1], move[2])
    board.printBoard()

if __name__ == '__main__':
    test()
