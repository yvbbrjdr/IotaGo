#!/usr/bin/env python

from GoBoard import GoBoard as gb
from PolicyNetwork import PolicyNetwork as pn

def main():
    print('Welcome to IotaGo')
    network = pn(layerCount = int(input('layerCount: ')), filterCount = int(input('filterCount: ')), learningRate = float(input('learningRate: ')))
    while True:
        command = input('[l]oad [s]ave [t]rainFolder [i]nference [e]xit\n')
        if command == 'l':
            network.load(input('Filename: '))
        elif command == 's':
            network.save(input('Filename: '))
        elif command == 't':
            network.trainFolder(input('Path: '), times = int(input('Times: ')))
        elif command == 'i':
            board = gb()
            while True:
                color = board.getNextColor()
                board.printBoard()
                if color == gb.black:
                    print('Black\'s turn')
                else:
                    print('White\'s turn')
                command = input('[l]oad [s]ave [m]ove [sk]ip [i]nference [e]xit\n')
                if command == 'l':
                    board.load(input('Filename: '))
                elif command == 's':
                    board.save(input('Filename: '))
                elif command == 'm':
                    x = input('x: ')
                    y = input('y: ')
                    board.move(int(x), int(y), color)
                elif command == 'sk':
                    board.skip()
                elif command == 'i':
                    infer = network.inference([board])[0]
                    m = - 1.0
                    mx = 0
                    my = 0
                    for i in range(network.getSize()):
                        for j in range(network.getSize()):
                            if infer[i][j] > m and board.isValidMove(i, j, color):
                                m = infer[i][j]
                                mx = i
                                my = j
                    board.move(mx, my, color)
                elif command == 'e':
                    break
        elif command == 'e':
            break

if __name__ == '__main__':
    main()
