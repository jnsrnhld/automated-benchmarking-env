from .univariate_predictor import UnivariatePredictor
import numpy as np


class KernelRegression(UnivariatePredictor):
    """
    Kernel Regression model implementing univariate regression with locally weighted linear regression.

    Parameters
    ----------
    degree : int, optional
        The degree of the polynomial features. Default is 1.
    bandwidth : float, optional
        The bandwidth parameter for the kernel. Default is 1.0.
    tolerance : float, optional
        Regularization parameter to avoid singular matrices. Default is machine epsilon.

    Examples
    --------
    ```python
    # Create a KernelRegression instance
    predictor = KernelRegression(degree=2, bandwidth=1.0)

    # Fit the model
    predictor.fit(x_train, y_train)

    # Predict new values
    y_pred = predictor.predict(x_test)
    ```
    """

    def __init__(self, degree=1, bandwidth=1.0, tolerance=np.finfo(float).eps):
        self.degree = degree
        self.bandwidth = bandwidth
        self.tolerance = tolerance
        self.x = None
        self.y = None

    def _fit(self, x: np.ndarray, y: np.ndarray):
        if x.shape[0] != y.shape[0]:
            raise ValueError("Vectors x and y must have the same length!")

        self.x = x
        self.y = y

        return self

    def _predict(self, x_predict: np.ndarray) -> np.ndarray:
        if self.x is None or self.y is None:
            raise ValueError("Model has not been fitted yet!")

        x_train = self.x
        y_train = self.y

        n_predict = x_predict.shape[0]
        n_train = x_train.shape[0]

        # Compute the weight matrix
        diff = x_predict[:, np.newaxis] - x_train[np.newaxis, :]
        weight_matrix = np.exp(- (diff ** 2) / (2 * self.bandwidth ** 2))

        # Map features
        X = self._feature_map(x_train)
        X_predict = self._feature_map(x_predict)

        # Predict values
        y_predict = self._predict_values(X, y_train, X_predict, weight_matrix)

        return y_predict

    def _feature_map(self, x: np.ndarray) -> np.ndarray:
        """
        Maps the input data to polynomial features up to the specified degree.

        Parameters
        ----------
        x : numpy.ndarray
            Input data array.

        Returns
        -------
        x_mapped : numpy.ndarray
            Mapped feature array.
        """
        x_mapped = np.zeros((x.shape[0], self.degree + 1))
        for i in range(self.degree + 1):
            x_mapped[:, i] = x ** i
        return x_mapped

    def _predict_values(self, X: np.ndarray, y: np.ndarray, X_predict: np.ndarray, W: np.ndarray) -> np.ndarray:
        """
        Predicts the target values for the given feature matrix and weight matrix.

        Parameters
        ----------
        X : numpy.ndarray
            Training feature matrix.
        y : numpy.ndarray
            Training target vector.
        X_predict : numpy.ndarray
            Feature matrix for prediction.
        W : numpy.ndarray
            Weight matrix.

        Returns
        -------
        y_pred : numpy.ndarray
            Predicted target values.
        """
        y_pred = np.zeros(X_predict.shape[0])
        for i in range(y_pred.shape[0]):
            y_pred[i] = self._predict_single(X, y, X_predict[i, :], W[i, :])
        return y_pred

    def _predict_single(self, X: np.ndarray, y: np.ndarray, x: np.ndarray, w: np.ndarray) -> float:
        """
        Predicts a single target value using locally weighted linear regression.

        Parameters
        ----------
        X : numpy.ndarray
            Training feature matrix.
        y : numpy.ndarray
            Training target vector.
        x : numpy.ndarray
            Single feature vector for prediction.
        w : numpy.ndarray
            Weight vector for the training samples.

        Returns
        -------
        y_pred : float
            Predicted target value.
        """
        # Compute the weighted normal equations components
        xtx = X.T @ (w[:, np.newaxis] * X) + self.tolerance * np.eye(X.shape[1])
        xty = X.T @ (w * y)

        # Solve for coefficients
        c = np.linalg.solve(xtx, xty)

        # Compute prediction
        y_pred = x @ c

        return y_pred
