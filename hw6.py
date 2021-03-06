# -*- coding: utf-8 -*-
"""Hw6

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tGruT-pZd0u83l4MYTVkBYgsq5zn9yUd
"""



import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import scipy.optimize

import math as math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def loadData (which):
    images = np.load("mnist_{}_images.npy".format(which))
    labels = np.load("mnist_{}_labels.npy".format(which))
    return images, labels

def fPC (y, yhat):
    yhat = np.argmax(yhat, axis=0)
    y = np.argmax(y, axis=0)
    n = float(y.size)
    diff = y - yhat
    diff[diff!=0] = 1 
    num_correct = n - np.sum(diff)
    return num_correct/n

NUM_INPUT = 784  # Number of input neurons
NUM_HIDDEN = 50  # Number of hidden neurons
NUM_OUTPUT = 10  # Number of output neurons
NUM_CHECK = 5  # Number of examples on which to check the gradient

# Given a vector w containing all the weights and biased vectors, extract
# and return the individual weights and biases W1, b1, W2, b2.
# This is useful for performing a gradient check with check_grad.
def unpack (w):
  #(50, 784) (50, 1) (10, 50) (10, 1)
  W1 = w[0:39200]
  W1 = W1.reshape(50,784)
  b1 = w[39200:39250]
  b1 = b1.reshape(50,1)
  W2 = w[39250:39750]
  W2 = W2.reshape(10,50)
  b2 = w[39750:39760]
  b2 = b2.reshape(10,1)
#   W1 = w[0]
#   b1 = w[1]
#   W2 = w[2]
#   b2 = w[3]
  return W1, b1, W2, b2

# Given individual weights and biases W1, b1, W2, b2, concatenate them and
# return a vector w containing all of them.
# This is useful for performing a gradient check with check_grad.
def pack (W1, b1, W2, b2):
  W1 = W1.flatten()
  W2 = W2.flatten()
  b1 = b1.flatten()
  b2 = b2.flatten()
  w = np.concatenate((W1, b1, W2, b2))
#   w = []
#   w.append(W1)
#   w.append(b1)
#   w.append(W2)
#   w.append(b2)
  return w

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / np.sum(e_x, axis=0) 

def relu(x):
    X= np.copy(x)
    X[X <= 0] = 0
    return X

def relu_prime(x):
  x = x.T
  x[x <= 0] = 0
  x[x > 0]  = 1
  return x
  
def fCE(y, yhat, w2, w1):
    size = y.shape[1]
    return -(1./size) * np.sum(y*np.log(yhat)) 

def forwardProp(X, w):
    w1new, b1new, w2new, b2new = unpack(w)
    z1 = w1new.dot(X) + b1new
    h1 = relu(z1)
    z2 = w2new.dot(h1) + b2new
    yhat = softmax(z2)
    return yhat, z1, h1

def backProp(X, yhat, y, w1, w2, z1, h1, batch_size):
    diff = (yhat-y).T
    diff = diff.dot(w2)
    z1t = relu_prime(z1)
    gt = diff * z1t
    gb1 = np.mean(gt.T, axis=1)
    gb2 = np.mean(yhat - y, axis=1)
    gb1 = gb1.reshape((len(gb1), 1))
    gb2 = gb2.reshape((len(gb2), 1))
    gw1 = gt.T.dot(X.T)* (1./batch_size)
    gw2 = (yhat - y).dot(h1.T)*(1./batch_size)
    return gb1, gb2, gw1, gw2
    
# Given training images X, associated labels Y, and a vector of combined weights
# and bias terms w, compute and return the gradient of fCE. You might
# want to extend this function to return multiple arguments (in which case you
# will also need to modify slightly the gradient check code below).
def gradCE (X, Y, w):
  yhat, z1, h1 = forward_prop(X,w)
  gW1, gb1, gW2, gb2 = back_prop(X, Y, yhat, w, z1, h1)
  wgrad = pack(gW1, gb1, gW2, gb2)
#   print(fCE(Y, yhat))
#   print(fpc(Y, yhat), 'pc')
  return wgrad, yhat

def updateWeights(X, y, w, hidden_nodes, learning_rate, batch_size, epochs, bl=False):
    n = y.shape[1]
    num_batches = int(n/batch_size)
    weights, biases, weights2, biases2 = unpack(w)
    w1old = np.copy(weights)
    w1new = np.copy(weights)
    w2old = np.copy(weights2)
    w2new = np.copy(weights2)
    b1old = np.copy(biases)
    b1new = np.copy(biases)
    b2new = np.copy(biases2)
    b2old = np.copy(biases2)
    pc = 0

    for e in range(epochs):
        idx = 0
        for batch in range(num_batches):
            B_X = X[:,idx:idx + batch_size]
            B_y = y[:,idx:idx+batch_size]
            w = pack(w1new, b1new, w2new, b2new)
            B_yhat, z1, h1 = forwardProp(B_X, w)
            gb1, gb2, gw1, gw2 = backProp(B_X, B_yhat, B_y, w1new, w2new, z1, h1, batch_size)
            w1old = np.copy(w1new)
            w2old = np.copy(w2new)
            b1old = np.copy(b1new)
            b2old = np.copy(b2new)
            w1new = w1old - (learning_rate * gw1)
            w2new = w2old - (learning_rate * gw2)
            b1new = b1old - (learning_rate * gb1)
            b2new = b2old - (learning_rate * gb2)
            idx += batch_size
            w = pack(w1new, b1new, w2new, b2new)
        yhat, z1, h1 = forwardProp(X, w)
        pc = fPC(y, yhat)
        cross = fCE(y,yhat, w1new, w2new)
        if e >= epochs - 20 and not bl:
            print("Epoch " + str(e+1) + "")
            print("fPC = " + str(pc))
            print("fCE = " + str(cross))
            print()

    return w1new, w2new, b1new, b2new, pc


def train (trainX, trainY, hidden_nodes=50, learning_rate=.2, batch_size=16, epochs=30, bl=False):
    X = trainX
    y = trainY
    
    W1 = 2 * np.random.randn(NUM_HIDDEN, X.shape[0]) *  1./ NUM_INPUT** 0.5
    b1  = .01 * np.ones(NUM_HIDDEN).reshape((NUM_HIDDEN,1)) * .01
    W2 = np.random.randn(10, NUM_HIDDEN) *  1./ NUM_INPUT**0.5
    b2 = .01 * np.ones(NUM_OUTPUT).reshape((10,1))  
    w = pack(W1, b1, W2, b2)
    # Check that the gradient is correct on just a few examples (randomly drawn).
#   idxs = np.random.permutation(trainX.shape[0])[0:NUM_CHECK]
#   print(scipy.optimize.check_grad(lambda w_: fCE(np.atleast_2d(trainX[idxs,:]), np.atleast_2d(trainY[idxs,:]), w_), \
#                                 lambda w_: gradCE(np.atleast_2d(trainX[idxs,:]), np.atleast_2d(trainY[idxs,:]), w_), \
#                                 w))
#   Train the network and obtain the sequence of w's obtained using SGD
    return updateWeights(X, y, w,  hidden_nodes, learning_rate, batch_size, epochs, bl)



def findBestHyperParameters(X, y, w1, w2, b1, b2, val_faces, val_labels):
    w1v = np.copy(w1)
    w2v = np.copy(w2)
    b2v = np.copy(b2)
    b1v = np.copy(b1)

    hidden_layers =  [30, 40, 50]
    learning_rates = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
    minibatches = [16, 32, 64, 128, 256]
    epochs = [20, 30, 40, 50]

    best_fpc = 0.0
    best_hidden = 0
    best_learning = 0
    best_minibatches = 0
    best_epochs = 0

    for i in range(10):
        print("Validation {}".format(i))
        curr_hiddens = hidden_layers[int(np.random.rand()*3)]
        curr_learning = learning_rates[int(np.random.rand()*6)]
        curr_minibatches = minibatches[int(np.random.rand()*5)]
        curr_epochs = epochs[int(np.random.rand()*4)]

        print("hidden_layers = ", curr_hiddens)
        print("Learning Rate = ", curr_learning)
        print("Batches = ", curr_minibatches)
        print("Epochs = ", curr_epochs)

        w1 = np.copy(w1v)
        w2 = np.copy(w2v)
        b2 = np.copy(b2v)
        b1 = np.copy(b1v)

        w1v, w2v, b1v, b2v, pc = train(X, y, curr_hiddens, curr_learning, curr_minibatches, curr_epochs, bl=True)
        valid = pack(w1, b1, w2, b2)
        yhat, z1, h1 = forwardProp(val_faces, valid)
        pc = fPC(val_labels, yhat)
        cross = fCE(val_labels, yhat, w1, w2)

        print("fpc = " + str(pc))
        print("fce = " + str(cross))
        print()

        w1 = np.copy(w1v)
        w2 = np.copy(w2v)
        b2 = np.copy(b2v)
        b1 = np.copy(b1v)

        if pc > best_fpc:
            best_fpc = pc
            best_hidden_layers = curr_hiddens
            best_learning = curr_learning
            best_minibatches = curr_minibatches
            best_epochs = curr_epochs
            print(" Validation Update")
            print("Improved FPC = ", best_fpc);
            print("hidden_layers = ", best_hidden_layers)
            print("Learning Rate = ", best_learning)
            print("Batches = ", best_minibatches)
            print("Epochs = ", best_epochs)
            print()

    print("Hyperparameters Validation")
    print("fPC = ", best_fpc);
    print("hidden_layers = ", best_hidden_layers)
    print("Learning Rate = ", best_learning)
    print("Batches = ", best_minibatches)
    print("Epochs = ", best_epochs)
    print()
    print("Optimized hyperparameters...")
    print()
    w1, w2, b1, b2, pc = train(X, y, best_hidden_layers, best_learning, best_minibatches, best_epochs, bl=False)
    return w1, w2, b1, b2

def test(testingFaces, testingLabels, w1, w2, b1, b2):
    print("Beginning testing...")
    tests = pack(w1, b1, w2, b2)
    yhat_test, z1, h1 = forwardProp(testingFaces, tests)
    pc_test = fPC(testingLabels, yhat_test)
    cross_test = fCE(testingLabels, yhat_test, w1, w2)
    print()
    print ("*** Testing Set Results ***")
    print("fPC = " + str(pc_test))
    print("fCE = " + str(cross_test))

if __name__ == "__main__":
    trainX, trainY = loadData("train")
    testX, testY = loadData("test")
    validation_faces,validation_labels  = loadData("validation")
    rng_state = np.random.get_state()
    np.random.shuffle(trainX)
    np.random.set_state(rng_state)
    np.random.shuffle(trainY)

    np.random.set_state(rng_state)
    np.random.shuffle(validation_faces)
    np.random.set_state(rng_state)
    np.random.shuffle(validation_labels) 

    w1, w2, b1, b2, pc = train(trainX.T, trainY.T)
    w1, w2, b1, b2 = findBestHyperParameters(trainX.T, trainY.T, w1, w2, b1, b2, validation_faces.T, validation_labels.T)
    test(testX.T, testY.T, w1, w2, b1, b2)