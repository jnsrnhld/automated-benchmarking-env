import numpy as np
from scipy.optimize import nnls, lsq_linear

from services.ellis_port.univariate_predictor import UnivariatePredictor


class Ernest(UnivariatePredictor):
    """
    A class for fitting and predicting using the Ernest model based on nonlinear least squares.
    """

    @staticmethod
    def _fmap(x):
        """
        Internal static method to map input x to a set of features.
        """
        return np.c_[np.ones_like(x), 1. / x, np.log(x), x]

    def _fit(self, x: np.ndarray, y: np.ndarray):
        """
        Fit the model to the data.

        Parameters:
        x (np.ndarray): The input feature array.
        y (np.ndarray): The target array.

        Returns:
        self: The fitted model with updated coefficients.
        """
        x, y = x.flatten(), y.flatten()
        X = self._fmap(x)
        try:
            coeff, res = nnls(X, y, maxiter=10000)
            self.coeff = coeff
        except (RuntimeError, ValueError) as e:
            print(f"nnls failed... x: {X}, y: {y}, Exception: {e}")
            result = lsq_linear(X, y, bounds=(0, np.inf))
            self.coeff = result.x
        return self

    def _predict(self, x: np.ndarray):
        """
        Predict output using the fitted model.

        Parameters:
        x (np.ndarray): The input feature array.

        Returns:
        np.ndarray: The predicted values.
        """
        x = x.flatten()
        X = self._fmap(x)
        return np.dot(X, self.coeff)
