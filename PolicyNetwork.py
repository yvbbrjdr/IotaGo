#!/usr/bin/env python

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
from GoBoard import GoBoard as gb
from time import time

class PolicyNetwork(object):

    filterCount = 256
    filterSize = 3
    layerCount = 13

    def __init__(self, size = 19):
        if not isinstance(size, int) or size <= 0:
            raise Exception('PolicyNetwork: __init__: error: invalid size')
        self.__size = size
        self.__x = tf.placeholder(tf.float32, shape = [None, size, size, gb.featureCount])
        self.__y_ = tf.placeholder(tf.float32, shape = [None, size ** 2])
        self.__y = PolicyNetwork.conv2d(self.__x, PolicyNetwork.filterCount, 5)
        for _ in range(PolicyNetwork.layerCount - 2):
            self.__y = PolicyNetwork.conv2d(self.__y, PolicyNetwork.filterCount, PolicyNetwork.filterSize)
        self.__y = PolicyNetwork.conv2d(self.__y, 1, PolicyNetwork.filterSize)
        self.__rawY = tf.reshape(self.__y, [-1, size ** 2])
        self.__y = tf.nn.softmax(self.__rawY)
        self.__loss = tf.losses.softmax_cross_entropy(onehot_labels = self.__y_, logits = self.__rawY)
        self.__train = tf.contrib.layers.optimize_loss(loss = self.__loss, global_step = tf.contrib.framework.get_global_step(), learning_rate = 0.001, optimizer = "SGD")
        correct_prediction = tf.equal(tf.argmax(self.__y, 1), tf.argmax(self.__y_, 1))
        self.__accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
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

    def train(self, boards, moves, times = 1):
        if not isinstance(times, int) or times <= 0:
            raise Exception('PolicyNetwork: train: error: invalid times')
        inputs = self.getInput(boards, moves)
        for _ in range(times):
            self.__sess.run(self.__train, {self.__x : inputs[0], self.__y_ : inputs[1]})

    def lossAndAccuracy(self, boards, moves):
        inputs = self.getInput(boards, moves)
        return (self.__sess.run([self.__loss, self.__accuracy], {self.__x : inputs[0], self.__y_ : inputs[1]}))

    @staticmethod
    def conv2d(inputs, filters, kernel_size):
        return tf.layers.conv2d(inputs = inputs, filters = filters, kernel_size = [kernel_size, kernel_size], padding = 'same', activation = tf.nn.elu)

def test():
    board1 = gb()
    board2 = gb()
    board2.move(3, 3, gb.black)
    network = PolicyNetwork()
    t0 = time()
    print('Initial Loss and Accuracy:', network.lossAndAccuracy([board1, board2], [(3, 3), (15, 15)]), 'Time:', time() - t0)
    for i in range(100):
        network.train([board1, board2], [(3, 3), (15, 15)], 10)
        print('Step:', i * 10 + 10, 'Loss and Accuracy:', network.lossAndAccuracy([board1, board2], [(3, 3), (15, 15)]), 'Time:', time() - t0)

if __name__ == '__main__':
    test()
