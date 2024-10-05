import numpy as np
from typing import Optional, List

from univariate_predictor import UnivariatePredictor
from ernest import Ernest
from kernel_regression import KernelRegression
from interpolation_splits import InterpolationSplits
from cross_validation import CrossValidation


class Bell(UnivariatePredictor):
    def __init__(self):
        self.best_model: Optional[UnivariatePredictor] = None

    def _fit(self, x: np.ndarray, y: np.ndarray) -> 'Bell':
        if len(x) != len(y):
            raise ValueError("Vectors x and y must have the same length!")

        # Create candidate models for interpolation
        bandwidths = np.linspace(1, 100, 100)
        models: List[UnivariatePredictor] = [
            KernelRegression(bandwidth=bandwidth, tolerance=1e-12) for bandwidth in bandwidths
        ]
        models.append(Ernest())

        # Compute the CV score using interpolation splits
        splits = InterpolationSplits(x, y)
        loss_function = lambda y_pred, y_true: np.sum(np.abs(y_pred - y_true) / y_true) / len(y_true)
        scores = CrossValidation.cross_validation_score(models, splits, loss_function)

        # Compute mean score for each model and select the best
        mean_scores = np.sum(scores, axis=1) / scores.shape[1]
        idx = np.argmin(mean_scores)

        # Train the selected model
        self.best_model = models[idx]
        self.best_model.fit(x, y)

        return self

    def _predict(self, x: np.ndarray) -> np.ndarray:
        if self.best_model is None:
            raise Exception("Model has not been fitted yet!")
        return self.best_model.predict(x)
