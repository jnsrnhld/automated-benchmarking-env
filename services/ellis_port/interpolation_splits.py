import numpy as np


class InterpolationSplits:
    """
    An iterable class that generates training and testing splits for interpolation tasks.
    """

    def __init__(self, x, y):
        """
        Initializes the class with input feature array x and target array y.

        Parameters:
        x (np.ndarray): Input feature array.
        y (np.ndarray): Target array.
        """
        self.x = x
        self.y = y
        self.xu = np.unique(x)[1:-1]  # Unique values of x, excluding the first and last
        self.n_iter = self.xu.size    # Number of iterations (splits)
        self.i_iter = 0               # Iteration counter

    def __iter__(self):
        """
        Returns the iterator object.

        Returns:
        self: The iterator instance.
        """
        return self

    def __next__(self):
        """
        Generates the next train-test split in the iteration.

        Returns:
        Tuple: Training and testing splits (xtrain, ytrain, xtest, ytest).
        """
        if self.i_iter == self.n_iter:
            raise StopIteration

        m = self.x == self.xu[self.i_iter]
        xtrain, ytrain = self.x[~m], self.y[~m]
        xtest, ytest = self.x[m], self.y[m]

        self.i_iter = self.i_iter + 1

        return xtrain, ytrain, xtest, ytest
