#!/usr/bin/env python3

from GoBoard import GoBoard as gb
from PolicyNetwork import PolicyNetwork as pn
from copy import deepcopy

def inputType(prompt, typename):
    while True:
        try:
            x = typename(input(prompt))
            return x
        except:
            print('inputType: error: invalid input')

def main():
    print('Welcome to IotaGo')
    while True:
        try:
            network = pn(layerCount = inputType('layerCount: ', int), filterCount = inputType('filterCount: ', int), learningRate = inputType('learningRate: ', float))
            break
        except:
            print('main: error: invalid network parameters')
    while True:
        command = input('[l]oad [s]ave [t]rainFolder [i]nference [e]xit\n')
        if command == 'l':
            try:
                network.load(input('Filename: '))
            except:
                print('main: error: load failed')
        elif command == 's':
            try:
                network.save(input('Filename: '))
            except:
                print('main: error: save failed')
        elif command == 't':
            try:
                network.trainFolder(input('Path: '), times = inputType('Times: ', int))
            except:
                print('main: error: train failed')
        elif command == 'i':
            boards = [gb()]
            while True:
                board = deepcopy(boards[-1])
                color = board.getNextColor()
                board.printBoard()
                if color == gb.black:
                    print('Black\'s turn')
                else:
                    print('White\'s turn')
                command = input('[l]oad [s]ave [b]ack [m]ove [sk]ip [i]nference [e]xit\n')
                if command == 'l':
                    try:
                        board.load(input('Filename: '))
                        boards.append(board)
                    except:
                        print('main: error: load failed')
                elif command == 's':
                    try:
                        board.save(input('Filename: '))
                    except:
                        print('main: error: save failed')
                elif command == 'b':
                    if len(boards) > 1:
                        del boards[-1]
                    else:
                        print('main: error: unable to go back anymore')
                elif command == 'm':
                    try:
                        board.move(int(input('x: ')), int(input('y: ')), color)
                        boards.append(board)
                    except:
                        print('main: error: invalid move')
                elif command == 'sk':
                    board.skip()
                    boards.append(board)
                elif command == 'i':
                    infer = network.inference([board])[0]
                    m = - 1.0
                    mx = 0
                    my = 0
                    ok = False
                    for i in range(network.getSize()):
                        for j in range(network.getSize()):
                            if infer[i][j] > m and board.isValidMove(i, j, color):
                                m = infer[i][j]
                                mx = i
                                my = j
                                ok = True
                    if ok:
                        board.move(mx, my, color)
                        boards.append(board)
                    else:
                        print('pass')
                elif command == 'e':
                    break
        elif command == 'e':
            break

if __name__ == '__main__':
    main()
