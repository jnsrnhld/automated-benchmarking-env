import numpy as np
from scipy.optimize import nnls

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
        X = self._fmap(x)
        try:
            (coeff, _) = nnls(X, y)
            self.coeff = coeff
        except:
            # prevents matrix is singular error
            self.coeff = np.mean(y)
        return self

    def _predict(self, x: np.ndarray):
        """
        Predict output using the fitted model.

        Parameters:
        x (np.ndarray): The input feature array.

        Returns:
        np.ndarray: The predicted values.
        """
        X = self._fmap(x)
        return np.dot(X, self.coeff)
