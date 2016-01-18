# Michal Badura
# Neural network algorithm with backpropagation

import numpy as np
import pickle, gzip

class NN():
    def __init__(self, nlayers, sizes, g=None, dg=None):
        self.nlayers = nlayers #first one is the input, last one is the output
        self.sizes = sizes #array of int sizes
        self.thetas = []
        self.biases = []
        for i in range(nlayers-1):
            shape = (sizes[i+1], sizes[i])            
            self.thetas.append(np.random.uniform(-0.5, 0.5, size=shape))
            self.biases.append(np.random.uniform(-0.5,0.5, size=(sizes[i+1], 1)))
        #g is the nonlinear activation function; dg its derivative
        if g==None:
            self.g = lambda x: 1 / (1.0 + np.exp(-x))
            self.dg = lambda x: self.g(x) * (1 - self.g(x))
        else:
            self.g = g
            self.dg=dg
            
    
    def forward(self, X):
        a = X        
        for i in range(self.nlayers-1):
            a = self.g(np.dot(self.thetas[i], a) + self.biases[i])
        return a
    
    def train(self, Xtrain, ytrain, alpha, niter):
        print("Learning with alpha = {0}".format(alpha))        
        self.biases = list(map(lambda x: x*0, self.biases)) #TOCHANGE
        print(self.biases)
        for t in range(niter):        
            #pick one datapoint        
            i = np.random.randint(0, len(Xtrain))
            X = Xtrain[i]
            y = ytrain[i]
            #compute ypred saving outputs for all hidden layers
            results = [X] #"outputs" in the input layer, for nicer indexing
            a = X        
            for i in range(self.nlayers-1):
                a = self.g(np.dot(self.thetas[i], a) + self.biases[i])
                results.append(a)
            ypred = a[-1]
            deltas = [None for _ in range(self.nlayers)]
            #we compute deltas, which are errors propagated backwards        
            #deltas[0] should stay None, because we don't compute errors for inputs
            deltas[self.nlayers-1] = (y-ypred) * self.dg(ypred)
            #deltas[self.nlayers-1] = (y-ypred)
            for i in range(self.nlayers-2, 0, -1):
                deltas[i] = np.dot(self.thetas[i].T, deltas[i+1]) \
                    * self.dg(results[i])
            #now we compute changes in weights, theta is exterior product
            #of outputs from source layer and deltas of target layer
            delta_thetas = []
#            numerical = self.numerical_gradient(X,y)
            for i in range(self.nlayers-1):
                delta_thetas.append(np.dot(deltas[i+1], results[i].T))
                #update weights by deltas * learning rate            
                self.thetas[i] += alpha * delta_thetas[i]
                self.biases[i] += alpha * deltas[i+1]
                #self.thetas[i] -= alpha * numerical[i]
#                print(delta_thetas)
#                print(self.numerical_gradient(X,y))
#                print("---")
                
            if t%10==0:
                error = 0                
                for i in range(len(Xtrain)):
                    error += np.linalg.norm(self.forward(Xtrain[i]) - ytrain[i])
                error /= len(Xtrain)
                print("Iteration {0}: L2 error {1}".format(t, error))
        print("Iteration {0}: L2 error {1}".format(t, error))
        
    def single_error(self, X, y):
        error = np.linalg.norm(self.forward(X) - y)
        return error
    
    def numerical_gradient(self, X, y, eps=0.000001):
        gradients = []
        saved_thetas = self.thetas[:] #copy
        for l in range(self.nlayers-1):
            theta = self.thetas[l]
            grad = np.zeros(theta.shape)
            for i in range(theta.shape[0]):
                for j in range(theta.shape[1]):
                    self.thetas[l][i][j] += eps
                    high = self.single_error(X,y)
                    self.thetas[l][i][j] -= 2*eps
                    low = self.single_error(X,y)
                    dWij = (high - low) / (2*eps)
                    grad[i][j] = dWij
                    self.thetas = saved_thetas #restore the values
            gradients.append(grad)
        return gradients
                
                
                

global model
def testLogic():
    net = NN(3,[2,2,1])
    Xtrain = list(map(lambda x: np.array(x).reshape(2,1),
                      [[1,1],[1,0],[0,1],[0,0]]))
    ytrain = list(map(lambda x: np.array(x).reshape(1,1),
                      [[0],[0],[0],[0]]))
    net.train(Xtrain, ytrain, niter=5000, alpha=0.01)
    global model
    model = net

def testLinear():
    net = NN(2,[5,1], g=lambda x:x, dg=lambda x:1)
    Xtrain = [np.random.random(size=(5,1)) for i in range(1000)]
    ytrain = [np.array([np.sum(X)/5]).reshape((1,1)) for X in Xtrain]
    net.train(Xtrain, ytrain, niter=10000, alpha=0.5)
    global model
    model = net

def testMnist(to_test):
    #pickled MNIST dataset from deeplearning.net    
    global train_set, valid_set
    global model
    f = gzip.open('mnist.pkl.gz', 'rb')
    train_set, valid_set, test_set = pickle.load(f, encoding='latin1')
    f.close()    
    Xs = list(map(lambda arr: np.array(arr).reshape(784,1), train_set[0]))
    ys = list(map(lambda n: np.array([1 if i==n else 0 for i in range(10)]).reshape(10,1), train_set[1]))
    model = NN(3,[784, 50, 10])
    model.train(Xs, ys, 0.1, 300)
    correct = 0
    for i in range(to_test):
        pred = np.argmax(model.forward(test_set[0][i].reshape(784,1)))
        actual = test_set[1][i]
        msg = "INCORRECT"        
        if actual == pred:        
            msg = "CORRECT"
            correct += 1
        #print("Number: {0}. Predicted: {1}. {2}".format(actual, pred, msg))
    print("Accuracy: {0}".format(correct*1.0/to_test))

np.random.seed(1)
#testLogic()
#testLinear()
testMnist(1000)



