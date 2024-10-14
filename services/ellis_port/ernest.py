import numpy as np
from scipy.optimize import nnls

from services.ellis_port.univariate_predictor import UnivariatePredictor


def feature_map(x: np.ndarray) -> np.ndarray:
    epsilon = 1e-10  # Small value to avoid division by zero and log(0)

    ones = np.ones_like(x)

    # Replace 0 values in x with epsilon to avoid division by zero and log(0)
    x_safe = np.where(x == 0, epsilon, x)

    # Feature mapping
    x_mapped = np.vstack([
        ones,  # Constant term
        ones / x_safe,  # 1/x
        np.log(x_safe),  # log(x)
        x  # x itself
    ]).T

    return x_mapped


class Ernest(UnivariatePredictor):
    def __init__(self):
        self.coefficients = None

    def _fit(self, x: np.ndarray, y: np.ndarray) -> 'Ernest':
        if len(x) != len(y):
            raise ValueError("Vectors x and y must have the same length!")
        X = feature_map(x)
        A = X.T @ X
        b = X.T @ y
        (result, _) = nnls(A, b, maxiter=max(400, len(b)), atol=Ernest.compute_atol(A))
        self.coefficients = result
        return self

    def _predict(self, x: np.ndarray) -> np.ndarray:
        if self.coefficients is None:
            raise Exception("Model has not been fitted yet!")
        _x = feature_map(x)
        return _x @ self.coefficients

    @staticmethod
    def compute_atol(A: np.ndarray) -> float:
        m, n = A.shape
        norm_A_1 = np.linalg.norm(A, 1)
        atol = max(m, n) * norm_A_1 * np.spacing(1.) * 1e4
        return atol
