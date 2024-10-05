import numpy as np
from scipy.optimize import nnls
from univariate_predictor import UnivariatePredictor


class Ernest(UnivariatePredictor):
    def __init__(self):
        self.coefficients = None

    def _fit(self, x: np.ndarray, y: np.ndarray) -> 'Ernest':
        if len(x) != len(y):
            raise ValueError("Vectors x and y must have the same length!")

        x = self.feature_map(x)

        # Use SciPy's nnls to solve x @ coefficients = y, with coefficients >= 0
        self.coefficients, _ = nnls(x, y)
        return self

    def _predict(self, x: np.ndarray) -> np.ndarray:
        if self.coefficients is None:
            raise Exception("Model has not been fitted yet!")
        X = self.feature_map(x)
        return X @ self.coefficients

    def feature_map(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x)
        ones = np.ones_like(x)

        # Construct the feature matrix
        X = np.vstack([
            ones,  # Bias term
            ones / x,  # 1 / x
            np.log(x),  # log(x)
            x  # x
        ]).T  # Transpose to get shape (n_samples, n_features)
        return X
