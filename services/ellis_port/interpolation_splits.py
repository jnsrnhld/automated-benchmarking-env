import numpy as np


class InterpolationSplits:
    def __init__(self, x: np.ndarray, y: np.ndarray):
        self.x = x
        self.y = y

        # Unique x values
        self.x_unique = np.unique(x)

        # Interpolation values: exclude the first and last unique x values
        self.x_interpolation = self.x_unique[1:-1]

        # Number of interpolation points
        self.n = len(self.x_interpolation)

        # Iterator index
        self.i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.n:
            raise StopIteration

        # Create mask for current interpolation point
        mask = self.x == self.x_interpolation[self.i]

        # Training data: all points not matching the current interpolation point
        x_train = self.x[~mask]
        y_train = self.y[~mask]

        # Test data: points matching the current interpolation point
        x_test = self.x[mask]
        y_test = self.y[mask]

        # Move to the next interpolation point
        self.i += 1

        # Return the training and test data as tuples
        return x_train, y_train, x_test, y_test
