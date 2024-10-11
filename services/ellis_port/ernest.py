import numpy as np
from scipy.optimize import nnls
from .univariate_predictor import UnivariatePredictor


def feature_map(x: np.ndarray) -> np.ndarray:
    ones = np.ones_like(x)
    x = np.vstack([ones, ones / x, np.log(x), x]).T
    return x


class Ernest(UnivariatePredictor):
    def __init__(self):
        self.coefficients = None

    def _fit(self, x: np.ndarray, y: np.ndarray) -> 'Ernest':
        if len(x) != len(y):
            raise ValueError("Vectors x and y must have the same length!")
        x = feature_map(x)

        # When x is entirely ones, the resulting feature matrix has only one unique row, meaning it has rank 1 (despite
        # having more rows), leading to a singular matrix when attempting least squares or NNLS.
        # In this case, we directly compute the mean of y and set the coefficients accordingly.
        if np.all(x == x[0]):
            print(f"Ernest#fit: x is entirely ones. Using mean y value.")
            self.coefficients = np.mean(y)
            return self
        else:
            xtx = np.dot(x.T, x)
            xty = np.dot(x.T, y)
            self.coefficients, _ = nnls(xtx, xty)
            return self

    def _predict(self, x: np.ndarray) -> np.ndarray:
        if self.coefficients is None:
            raise Exception("Model has not been fitted yet!")
        x = feature_map(x)
        return x @ self.coefficients
