import numpy as np


class InterpolationSplits:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xu = np.unique(x)[1:-1]
        self.n_iter = self.xu.size
        self.i_iter = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.i_iter == self.n_iter:
            raise StopIteration

        m = self.x == self.xu[self.i_iter]
        xtrain, ytrain = self.x[~m], self.y[~m]
        xtest, ytest = self.x[m], self.y[m]

        self.i_iter = self.i_iter + 1

        return (xtrain, ytrain), (xtest, ytest)

    def __len__(self):
        return self.n_iter
