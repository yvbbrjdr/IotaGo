#!/usr/bin/env python

from GoBoard import GoBoard as gb
from SGFParser import SGFParser as sp
from PolicyNetwork import PolicyNetwork as pn
from copy import deepcopy
import time

def trainSGF():
    board = gb()
    sgf = sp()
    network = pn()
    sgf.open(input('SGF filename: '))
    boards = []
    moves = []
    count = 0
    while sgf.hasNextMove():
        move = sgf.getNextMove()
        boards.append(deepcopy(board))
        moves.append((move[0], move[1]))
        board.move(move[0], move[1], move[2])
        count += 1
    loadfilename = input('Load filename: ')
    if loadfilename != '':
        network.load(loadfilename)
    for _ in range(int(input('Times to train: '))):
        for i in range(count // 50):
            network.train(boards[i * 50:i * 50 + 50], moves[i * 50:i * 50 + 50], 10)
            print(network.lossAndAccuracy(boards[i * 50:i * 50 + 50], moves[i * 50:i * 50 + 50]))
    network.save(input('Save filename: '))

def test():
    board = gb()
    network = pn()
    network.load(input('Load filename: '))
    while True:
        color = board.getNextColor()
        if 1 == 2:
            board.printBoard()
            x = input('x: ')
            y = input('y: ')
            board.move(int(x), int(y), color)
        else:
            y = network.inference(board)
            maxp = y[0][0]
            maxx = 0
            maxy = 0
            for i in range(network.getSize()):
                for j in range(network.getSize()):
                    if y[i][j] > maxp and board.isValidMove(i, j, color):
                        maxp = y[i][j]
                        maxx = i
                        maxy = j
            board.move(maxx, maxy, color)
            board.printBoard()
            time.sleep(1)

if __name__ == '__main__':
    test()
