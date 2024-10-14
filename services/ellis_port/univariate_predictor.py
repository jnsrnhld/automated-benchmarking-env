from abc import ABC, abstractmethod
import numpy as np

class UnivariatePredictor(ABC):
    """
    This class provides a basic abstract interface for univariate predictors.
    """

    @abstractmethod
    def _fit(self, x: np.ndarray, y: np.ndarray):
        """
        Abstract method to fit the model to the data.

        Parameters:
        x (np.ndarray): Input feature array.
        y (np.ndarray): Target array.
        """
        pass

    def fit(self, x: np.ndarray, y: np.ndarray):
        """
        Public method to fit the model, calling the underlying abstract _fit method.

        Parameters:
        x (np.ndarray): Input feature array.
        y (np.ndarray): Target array.

        Returns:
        self: The fitted model instance.
        """
        return self._fit(x, y)

    @abstractmethod
    def _predict(self, x: np.ndarray) -> np.ndarray:
        """
        Abstract method to predict the target values based on the input data.

        Parameters:
        x (np.ndarray): Input feature array.

        Returns:
        np.ndarray: Predicted values.
        """
        pass

    def predict(self, x: np.ndarray) -> np.ndarray:
        """
        Public method to predict the target values, calling the underlying abstract _predict method.

        Parameters:
        x (np.ndarray): Input feature array.

        Returns:
        np.ndarray: Predicted values.
        """
        return self._predict(x)
