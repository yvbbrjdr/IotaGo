#!/usr/bin/env python

from GoBoard import GoBoard as gb
from SGFParser import SGFParser as sp
from PolicyNetwork import PolicyNetwork as pn
from copy import deepcopy

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

if __name__ == '__main__':
    trainSGF()
