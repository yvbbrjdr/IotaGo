#!/usr/bin/env python3

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
from GoBoard import GoBoard as gb
from time import time
from SGFParser import SGFParser as sp
from copy import deepcopy

class PolicyNetwork(object):

    def __init__(self, size = 19, layerCount = 13, filterCount = 256, filterSize = 3, learningRate = 0.001):
        if not isinstance(size, int) or size <= 0:
            raise Exception('PolicyNetwork: __init__: error: invalid size')
        if not isinstance(layerCount, int) or layerCount < 2:
            raise Exception('PolicyNetwork: __init__: error: invalid layerCount')
        if not isinstance(filterCount, int) or filterCount <= 0:
            raise Exception('PolicyNetwork: __init__: error: invalid filterCount')
        if not isinstance(filterSize, int) or not 0 < filterSize <= size:
            raise Exception('PolicyNetwork: __init__: error: invalid filterSize')
        if not isinstance(learningRate, float) or learningRate <= 0:
            raise Exception('PolicyNetwork: __init__: error: invalid learningRate')
        self.__size = size
        self.__x = tf.placeholder(tf.float32, shape = [None, size, size, gb.featureCount])
        self.__y_ = tf.placeholder(tf.float32, shape = [None, size ** 2])
        self.__y = PolicyNetwork.conv2d(self.__x, filterCount, 5)
        for _ in range(layerCount - 2):
            self.__y = PolicyNetwork.conv2d(self.__y, filterCount, filterSize)
        self.__y = PolicyNetwork.conv2d(self.__y, 1, filterSize)
        self.__rawY = tf.reshape(self.__y, [-1, size ** 2])
        self.__y = tf.nn.softmax(self.__rawY)
        self.__loss = tf.losses.softmax_cross_entropy(onehot_labels = self.__y_, logits = self.__rawY)
        self.__train = tf.contrib.layers.optimize_loss(loss = self.__loss, global_step = tf.contrib.framework.get_global_step(), learning_rate = learningRate, optimizer = "SGD")
        correctPrediction = tf.equal(tf.argmax(self.__y, 1), tf.argmax(self.__y_, 1))
        self.__accuracy = tf.reduce_mean(tf.cast(correctPrediction, tf.float32))
        self.__sess = tf.Session()
        self.__sess.run(tf.global_variables_initializer())

    def getSize(self):
        return self.__size

    def save(self, filename):
        if not isinstance(filename, str):
            raise Exception('PolicyNetwork: save: error: invalid filename')
        tf.train.Saver().save(self.__sess, filename)

    def load(self, filename):
        if not isinstance(filename, str):
            raise Exception('PolicyNetwork: load: error: invalid filename')
        tf.train.Saver().restore(self.__sess, filename)

    def getInput(self, boards, moves):
        if not isinstance(boards, list):
            raise Exception('PolicyNetwork: getInput: error: invalid boards')
        if not isinstance(moves, list):
            raise Exception('PolicyNetwork: getInput: error: invalid moves')
        x = []
        y = []
        for board in boards:
            if not isinstance(board, gb) or board.getSize() != self.__size:
                raise Exception('PolicyNetwork: getInput: error: invalid board')
            x.append(board.allFeatures())
        for move in moves:
            if not isinstance(move, tuple) or len(move) != 2 or not isinstance(move[0], int) or not 0 <= move[0] < self.__size or not isinstance(move[1], int) or not 0 <= move[1] < self.__size:
                raise Exception('PolicyNetwork: getInput: error: invalid move')
            tmp = [0] * (self.__size ** 2)
            tmp[move[0] * self.__size + move[1]] = 1
            y.append(tmp)
        return (x, y)

    def inference(self, boards):
        return self.__sess.run(self.__y, {self.__x : self.getInput(boards, [])[0]}).reshape([-1, self.__size, self.__size]).tolist()

    def train(self, boards, moves, batchSize = 50, times = 1):
        if not isinstance(batchSize, int) or batchSize <= 0:
            raise Exception('PolicyNetwork: train: error: invalid batchSize')
        if not isinstance(times, int) or times <= 0:
            raise Exception('PolicyNetwork: train: error: invalid times')
        moveCount = min(len(boards), len(moves))
        batchCount = moveCount // batchSize
        if moveCount % batchSize > 0:
            batchCount += 1
        print('Start to train %d move(s) %d time(s) with batch size %d and batch count %d\nExtracting features. . . ' % (moveCount, times, batchSize, batchCount), end = '', flush = True)
        t0 = time()
        inputs = self.getInput(boards, moves)
        print('done in %f second(s)' % (time() - t0))
        if moveCount == 0:
            return
        laa = self.__sess.run([self.__loss, self.__accuracy], {self.__x : inputs[0], self.__y_ : inputs[1]})
        print('Training started with loss %f and accuracy %f' % (laa[0], laa[1]))
        for i in range(times):
            print('    Training #%d. . . ' % (i + 1))
            t00 = time()
            for j in range(batchCount):
                print('        Training batch #%d. . . ' % (j + 1), end = '', flush = True)
                t000 = time()
                self.__sess.run(self.__train, {self.__x : inputs[0][j * batchSize : j * batchSize + batchSize], self.__y_ : inputs[1][j * batchSize : j * batchSize + batchSize]})
                print('done in %f second(s)' % (time() - t000))
            print('    #%d trained in %f second(s)' % (i + 1, time() - t00))
        laa = self.__sess.run([self.__loss, self.__accuracy], {self.__x : inputs[0], self.__y_ : inputs[1]})
        print('Training ended in %f second(s) with loss %f and accuracy %f' % (time() - t0, laa[0], laa[1]))

    def lossAndAccuracy(self, boards, moves):
        inputs = self.getInput(boards, moves)
        return self.__sess.run([self.__loss, self.__accuracy], {self.__x : inputs[0], self.__y_ : inputs[1]})

    def trainSGF(self, filename, batchSize = 50, times = 10):
        if not isinstance(filename, str):
            raise Exception('PolicyNetwork: trainSGF: error: invalid filename')
        if not isinstance(batchSize, int) or batchSize <= 0:
            raise Exception('PolicyNetwork: trainSGF: error: invalid batchSize')
        if not isinstance(times, int) or times <= 0:
            raise Exception('PolicyNetwork: trainSGF: error: invalid times')
        board = gb(self.getSize())
        sgf = sp(filename)
        boards = []
        moves = []
        while sgf.hasNextMove():
            move = sgf.getNextMove()
            boards.append(deepcopy(board))
            moves.append((move[0], move[1]))
            try:
                board.move(move[0], move[1], move[2])
            except:
                print('Reaching invalid move')
                return
        self.train(boards, moves, batchSize, times)

    def trainFolder(self, path, batchSize = 50, times = 10):
        if not isinstance(path, str):
            raise Exception('PolicyNetwork: trainFolder: error: invalid path')
        if not isinstance(batchSize, int) or batchSize <= 0:
            raise Exception('PolicyNetwork: trainFolder: error: invalid batchSize')
        if not isinstance(times, int) or times <= 0:
            raise Exception('PolicyNetwork: trainFolder: error: invalid times')
        try:
            for parent, _, filenames in os.walk(path):
                for filename in filenames:
                    if filename[-4:] == '.sgf':
                        join = os.path.join(parent,filename)
                        print('Start to train %s' % (join))
                        self.trainSGF(join, batchSize, times)
                        print('Training ended')
        except KeyboardInterrupt:
            print('Training ended by keyboard')
            return

    @staticmethod
    def conv2d(inputs, filters, kernel_size):
        return tf.layers.conv2d(inputs = inputs, filters = filters, kernel_size = [kernel_size, kernel_size], padding = 'same', activation = tf.nn.elu)

if __name__ == '__main__':
    PolicyNetwork(layerCount = int(input('layerCount: ')), filterCount = int(input('filterCount: ')), learningRate = float(input('learningRate: '))).trainFolder(input('Train Folder: '), times = int(input('Times: ')))
