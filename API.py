from GoBoard import GoBoard as gb
from SGFParser import SGFParser as sp
from PolicyNetwork import PolicyNetwork as pn
from copy import deepcopy

board = gb()
sgf = sp()
network = pn()
sgf.open('../a.sgf')
boards = []
moves = []
count = 0
while sgf.hasNextMove():
    move = sgf.getNextMove()
    boards.append(deepcopy(board))
    moves.append((move[0], move[1]))
    board.move(move[0], move[1], move[2])
    count += 1
for _ in range(100):
    for i in range(count // 50):
        network.train(boards[i * 50:i * 50 + 50], moves[i * 50:i * 50 + 50], 10)
        print(network.lossAndAccuracy(boards[i * 50:i * 50 + 50], moves[i * 50:i * 50 + 50]))
