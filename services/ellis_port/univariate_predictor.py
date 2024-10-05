from abc import ABC, abstractmethod
import numpy as np

class UnivariatePredictor(ABC):
    """
    This class provides a basic interface for univariate predictors.
    The following example shows general usage of such predictors:

    ```python
    # create a concrete predictor
    predictor = ConcretePredictor()

    # train the model using training data
    x_train, y_train = get_training_data()
    predictor.fit(x_train, y_train)

    # now the model can be used for prediction
    x_test, y_test = get_test_data()
    y_predict = predictor.predict(x_test)
    ```
    """

    def fit(self, x, y):
        """
        Fits the model to the training data.

        Parameters
        ----------
        x : array-like
            An array-like object containing the one-dimensional (univariate) data samples.
        y : array-like
            An array-like object containing the target values.

        Returns
        -------
        self : UnivariatePredictor
            A reference to itself.
        """
        x = np.asarray(x)
        y = np.asarray(y)
        return self._fit(x, y)

    @abstractmethod
    def _fit(self, x: np.ndarray, y: np.ndarray):
        """
        Internal method to be implemented by subclasses.

        Parameters
        ----------
        x : numpy.ndarray
            A numpy array containing the one-dimensional (univariate) data samples.
        y : numpy.ndarray
            A numpy array containing the target values.

        Returns
        -------
        self : UnivariatePredictor
            A reference to itself.
        """
        pass

    def predict(self, x):
        """
        Predicts the values for the given set of values.

        Parameters
        ----------
        x : array-like
            An array-like object containing the one-dimensional (univariate) data samples for which the target values are predicted.

        Returns
        -------
        y_pred : numpy.ndarray
            A numpy array containing the predicted values.
        """
        x = np.asarray(x)
        return self._predict(x)

    @abstractmethod
    def _predict(self, x: np.ndarray) -> np.ndarray:
        """
        Internal method to be implemented by subclasses.

        Parameters
        ----------
        x : numpy.ndarray
            A numpy array containing the one-dimensional (univariate) data samples.

        Returns
        -------
        y_pred : numpy.ndarray
            A numpy array containing the predicted values.
        """
        pass
