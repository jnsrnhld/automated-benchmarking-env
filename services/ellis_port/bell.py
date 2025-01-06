import numpy as np
from typing import Optional, List

from .cross_validation import cv_score
from .univariate_predictor import UnivariatePredictor
from .ernest import Ernest
from .kernel_regression import KernelRegression
from .interpolation_splits import InterpolationSplits

class Bell(UnivariatePredictor):
    """
    A class that implements a model selection mechanism using different univariate predictors.
    """
    def __init__(self):
        self.best_model: Optional[UnivariatePredictor] = None

    def _fit(self, x: np.ndarray, y: np.ndarray) -> 'Bell':
        """
        Fits the best model from a pool of candidate models.

        Parameters:
        x (np.ndarray): Input feature array.
        y (np.ndarray): Target array.

        Returns:
        self: The fitted Bell model with the best predictor.
        """
        if len(x) != len(y):
            raise ValueError("Input and target arrays must have the same length.")

        splits = InterpolationSplits(x, y)

        models = [
            Ernest(),
            KernelRegression(),
        ]

        scores = cv_score(models, splits)
        best_idx = np.argmin(scores)
        self.best_model = models[best_idx].fit(x, y)
        return self

    def _predict(self, x: np.ndarray) -> np.ndarray:
        """
        Predicts the output using the best fitted model.

        Parameters:
        x (np.ndarray): Input feature array.

        Returns:
        np.ndarray: Predicted values.
        """
        if self.best_model is None:
            raise RuntimeError("No model has been fitted yet.")
        return self.best_model.predict(x)
