#Michal Badura
#simple Logistic Regression class with gradient checking
import numpy as np
from numpy.linalg import norm
import pickle, gzip

class LogisticRegression():
    """
    Logistic regression, trained by gradient descent
    """    
    def __init__(self, nin, nout):
        #adding one row for bias        
        self.theta = np.random.uniform(-1, 1, (nout, nin+1))
        #activation function        
        self.activ = lambda x: 1 / (1.0 + np.exp(-x))
        self.activprime = lambda x: self.activ(x) * (1 - self.activ(x))
        
    
    def single_gradient(self, X, y):
        """Calculates gradient of theta for a single datapoint"""
        ypred = self.predict(X)
        Xbias = np.vstack((X, np.array([1.0])))
        delta = (ypred - y)                
        return np.dot(delta, Xbias.T)
        
    
    def train(self, Xtrain, ytrain, niter, alpha, batchsize=100):
        for t in range(niter):        
            total_gradient = 0        
            batchidx = np.random.choice(range(len(Xtrain)), batchsize)
            Xbatch = [Xtrain[i] for i in batchidx]
            ybatch = [ytrain[i] for i in batchidx] 
            for i in range(len(Xbatch)):
                X,y = Xbatch[i],ybatch[i]
                total_gradient -= self.single_gradient(X,y)
                #total_gradient += self.numerical_gradient(X, y)
            total_gradient /= len(Xbatch)           
            self.theta += alpha * total_gradient
            if t%10==0:            
                print("Iteration {0}, error: {1}".format(
                    t, self.error(Xtrain, ytrain)))
            
    
    def predict(self, X):
        X = np.vstack((X, np.array([1.0]))) #add bias input
        return self.activ(np.dot(self.theta, X))
    
    def error(self, Xs, ys):
        """Computes preditction error for a dataset.
            Uses a convex cost function."""        
        m = len(Xs)        
        ypreds = list(map(self.predict, Xs))
        errs = [ys[i]*np.log(ypreds[i]) + (1-ys[i])*np.log(1-ypreds[i]) for i in range(len(ys))]         
        total = sum(map(norm, errs))
        #diffs = sum([np.dot((ys[i]-ypreds[i]).T, (ys[i]-ypreds[i])) for i in range(len(ys))])
        return -1.0/(m) * total
    
    def numerical_gradient(self, X, y, eps=0.000001):
        """
            Gradient computed by numerical approximation.
            For gradient checking.
        """
        saved_theta = self.theta[:] #copy
        theta = self.theta
        grad = np.zeros(theta.shape)
        for i in range(theta.shape[0]):
            for j in range(theta.shape[1]):
                self.theta[i][j] += eps
                high = self.error([X],[y])
                self.theta[i][j] -= 2*eps
                low = self.error([X],[y])
                dWij = (high - low) / (2*eps)
                grad[i][j] = dWij
                self.theta = saved_theta #restore the values
        return grad
    

def test():
    Xs = [np.random.uniform(-10,10,(5,1)) for _ in range(100)]
    ys = [np.array([np.sum(X)/3, np.sum(X)/5]).reshape(2,1) for X in Xs]
    global model    
    model = LogisticRegression(2,1)
    print(model.error(Xs, ys))
    model.train(Xs, ys, 1000, 0.02)

def testSingle():
    Xs = [np.array([1,1,1,1,1]).reshape(5,1)] + [np.random.uniform(-10,10,(5,1)) for _ in range(100)]
    ys = [np.array([1 if np.sum(X)/5 > 1 else 0]).reshape(1,1) for X in Xs]
    global model    
    model = LogisticRegression(5,1)
    print(model.error(Xs, ys))
    print(Xs[0], ys[0])
    model.train(Xs, ys, 100, 0.2)    

def testMnist(to_test):
    #pickled MNIST dataset from deeplearning.net    
    global train_set, valid_set
    global model
    f = gzip.open('mnist.pkl.gz', 'rb')
    train_set, valid_set, test_set = pickle.load(f, encoding='latin1')
    f.close()    
    Xs = list(map(lambda arr: np.array(arr).reshape(784,1), train_set[0]))
    ys = list(map(lambda n: np.array([1 if i==n else 0 for i in range(10)]).reshape(10,1), train_set[1]))
    model = LogisticRegression(784, 10)
    model.train(Xs, ys, 1000, 0.15)
    correct = 0
    for i in range(to_test):
        pred = np.argmax(model.predict(test_set[0][i].reshape(784,1)))
        actual = test_set[1][i]
        msg = "INCORRECT"        
        if actual == pred:        
            msg = "CORRECT"
            correct += 1
        #print("Number: {0}. Predicted: {1}. {2}".format(actual, pred, msg))
    print("Accuracy: {0}".format(correct*1.0/to_test))
        
        
np.random.seed(1)
testMnist(10000)