#!/usr/bin/env python

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
from GoBoard import GoBoard as gb
from GoBoard import rPrint

class PolicyNetwork(object):

    filterCount = 256
    filterSize = 3

    def __init__(self, size = 19):
        if not isinstance(size, int) or size <= 0:
            raise Exception("PolicyNetwork: __init__: error: invalid size")
        self.__size = size
        self.__x = tf.placeholder(tf.float32, shape = [None, size, size, gb.featureCount])
        self.__y_ = tf.placeholder(tf.float32, shape = [None, size ** 2])
        self.__y = PolicyNetwork.conv2d(self.__x, PolicyNetwork.weight_variable([5, 5, gb.featureCount, PolicyNetwork.filterCount]))
        self.__y += PolicyNetwork.bias_variable([PolicyNetwork.filterCount])
        self.__y = tf.nn.relu(self.__y)
        for _ in range(11):
            self.__y = PolicyNetwork.conv2d(self.__y, PolicyNetwork.weight_variable([PolicyNetwork.filterSize, PolicyNetwork.filterSize, PolicyNetwork.filterCount, PolicyNetwork.filterCount]))
            self.__y += PolicyNetwork.bias_variable([PolicyNetwork.filterCount])
            self.__y = tf.nn.relu(self.__y)
        self.__y = PolicyNetwork.conv2d(self.__y, PolicyNetwork.weight_variable([PolicyNetwork.filterSize, PolicyNetwork.filterSize, PolicyNetwork.filterCount, 1]))
        self.__y += PolicyNetwork.bias_variable([1])
        self.__y = tf.nn.relu(self.__y)
        self.__logy = tf.reshape(self.__y, [-1, size ** 2])
        self.__y = tf.nn.softmax(self.__logy)
        self.__cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels = self.__y_, logits = self.__logy))
        self.__train_step = tf.train.MomentumOptimizer(0.01, 0.01).minimize(self.__cross_entropy)
        self.__sess = tf.Session()
        self.__sess.run(tf.global_variables_initializer())

    def getSize(self):
        return self.__size

    def save(self, filename):
        if not isinstance(filename, str):
            raise Exception("PolicyNetwork: save: error: invalid filename")
        tf.train.Saver().save(self.__sess, filename)
        return True

    def load(self, filename):
        if not isinstance(filename, str):
            raise Exception("PolicyNetwork: load: error: invalid filename")
        tf.train.Saver().restore(self.__sess, filename)
        return True

    def inference(self, board):
        if not isinstance(board, gb) or board.getSize() != self.__size:
            raise Exception("PolicyNetwork: inference: error: invalid board")
        return self.__sess.run(self.__y, {self.__x : [board.allFeatures()]}).reshape([self.__size, self.__size]).tolist()

    def train(self, boards, moves, times = 1):
        if not isinstance(boards, list):
            raise Exception("PolicyNetwork: train: error: invalid boards")
        if not isinstance(moves, list):
            raise Exception("PolicyNetwork: train: error: invalid moves")
        if not isinstance(times, int) or times <= 0:
            raise Exception("PolicyNetwork: train: error: invalid times")
        x = []
        y = []
        for board in boards:
            if not isinstance(board, gb):
                raise Exception("PolicyNetwork: train: error: invalid board")
            x.append(board.allFeatures())
        for move in moves:
            if not isinstance(move, tuple) or len(move) != 2 or not isinstance(move[0], int) or not isinstance(move[1], int):
                raise Exception("PolicyNetwork: train: error: invalid move")
            tmp = [0] * (self.__size ** 2)
            tmp[move[0] * self.__size + move[1]] = 1
            y.append(tmp)
        for _ in range(times):
            self.__sess.run(self.__train_step, {self.__x : x, self.__y_ : y})
        return True

    def loss(self, boards, moves):
        if not isinstance(boards, list):
            raise Exception("PolicyNetwork: loss: error: invalid boards")
        if not isinstance(moves, list):
            raise Exception("PolicyNetwork: loss: error: invalid moves")
        x = []
        y = []
        for board in boards:
            if not isinstance(board, gb):
                raise Exception("PolicyNetwork: loss: error: invalid board")
            x.append(board.allFeatures())
        for move in moves:
            if not isinstance(move, tuple) or len(move) != 2 or not isinstance(move[0], int) or not isinstance(move[1], int):
                raise Exception("PolicyNetwork: loss: error: invalid move")
            tmp = [0] * (self.__size ** 2)
            tmp[move[0] * self.__size + move[1]] = 1
            y.append(tmp)
        return self.__sess.run(self.__cross_entropy, {self.__x : x, self.__y_ : y})

    @staticmethod
    def weight_variable(shape):
        return tf.Variable(tf.truncated_normal(shape, stddev = 0))

    @staticmethod
    def bias_variable(shape):
        return tf.Variable(tf.constant(0.1, shape = shape))

    @staticmethod
    def conv2d(x, W):
        return tf.nn.conv2d(x, W, strides = [1, 1, 1, 1], padding = 'SAME')

def test():
    board1 = gb()
    board2 = gb()
    board2.move(3, 3, gb.black)
    network = PolicyNetwork(board1.getSize())
    filename = input('Filename: ')
    if os.path.isfile(filename + '.meta'):
        network.load(filename)
    print("Initial Loss:", network.loss([board1, board2], [(3, 3), (15, 15)]))
    for i in range(100):
        network.train([board1, board2], [(3, 3), (15, 15)], 10)
        network.save(filename)
        print("Step:", i * 10 + 10, "Loss:", network.loss([board1, board2], [(3, 3), (15, 15)]))
    rPrint([network.inference(board1), network.inference(board2)])

if __name__ == '__main__':
    test()