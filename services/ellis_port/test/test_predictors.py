import unittest
import numpy as np

from services.ellis_port.kernel_regression import KernelRegression
from services.ellis_port.ernest import Ernest
from services.ellis_port.bell import Bell


class TestUnivariatePredictors(unittest.TestCase):
    def test_bell_predict_without_fit(self):
        """Bell should raise Exception when predict is called without fit."""
        with self.assertRaises(Exception):
            bell = Bell()
            x = np.arange(1, 6, dtype=float)  # x = [1.0, 2.0, 3.0, 4.0, 5.0]
            bell._predict(x)

    def test_bell_fit_vectors_different_length(self):
        """Bell should raise ValueError when fit is called with vectors of different lengths."""
        with self.assertRaises(ValueError):
            bell = Bell()
            x = np.arange(1, 6, dtype=float)  # x = [1.0, 2.0, 3.0, 4.0, 5.0]
            y = np.arange(1, 5, dtype=float)  # y = [1.0, 2.0, 3.0, 4.0]
            bell._fit(x, y)

    def test_ernest_predict_without_fit(self):
        """Ernest should raise Exception when predict is called without fit."""
        with self.assertRaises(Exception):
            ernest = Ernest()
            x = np.arange(1, 6, dtype=float)
            ernest._predict(x)

    def test_ernest_fit_vectors_different_length(self):
        """Ernest should raise ValueError when fit is called with vectors of different lengths."""
        with self.assertRaises(ValueError):
            ernest = Ernest()
            x = np.arange(1, 6, dtype=float)
            y = np.arange(1, 5, dtype=float)
            ernest._fit(x, y)

    def test_ernest_correct_prediction(self):
        """Ernest should calculate the correct predictions."""
        # First assertion: y follows the Ernest model
        ernest = Ernest()
        x = np.arange(1, 11, dtype=float)  # x = [1.0, 2.0, ..., 10.0]
        y = 5 + 4 * np.log(x) + 3 / x + 2 * x  # Generate y based on the Ernest model

        ernest._fit(x, y)
        y_predict = ernest._predict(x)

        # Check that the predictions are very close to the true values
        self.assertTrue(np.allclose(y, y_predict, atol=1e-8))

        # Second assertion: check non-negativity constraint
        ernest = Ernest()
        x = np.arange(1, 11, dtype=float)
        y = 5 - 2 * x  # This should result in negative values

        ernest._fit(x, y)
        y_predict = ernest._predict(x)

        # Since Ernest enforces non-negative coefficients, predictions should be approximately zero
        self.assertTrue(np.all(np.abs(y_predict) < 1e-8))

    def test_fit_method(self):
        # Provided input data
        test_data = [
            # (x, y) pairs
            (np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0])),
            # Edge case: x and y are zero vectors
            (np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0])),
            # Large vector inputs (randomly filled with values between 0 and 1)
            (np.random.rand(1000), np.random.rand(1000)),
            # real data
            (np.array([2.0, 2.0, 2.0]), np.array([6892.0, 7908.0, 7097.0])),
            (np.array([2.0, 2.0, 2.0]), np.array([475.0, 552.0, 567.0])),
            (np.array([3.0, 3.0, 3.0]), np.array([8679.0, 7334.0, 8018.0])),
            (np.array([3.0, 3.0, 3.0, 3.0]), np.array([7062.0, 7320.0, 7389.0, 12216.0]))
        ]

        for scale_outs, runtimes in test_data:
            model = Ernest()
            try:
                model._fit(scale_outs, runtimes)
                print(f"prediction: {model.predict(np.array([1.0, 2.0, 3.0]))}")
            except Exception as e:
                self.fail(f"fit method raised an exception with input {scale_outs}, {runtimes}: {e}")

    def test_kernel_regression_predict_without_fit(self):
        """KernelRegression should raise Exception when predict is called without fit."""
        with self.assertRaises(Exception):
            kernel_regression = KernelRegression()
            x = np.arange(1, 6, dtype=float)
            kernel_regression._predict(x)

    def test_kernel_regression_fit_vectors_different_length(self):
        """KernelRegression should raise ValueError when fit is called with vectors of different lengths."""
        with self.assertRaises(ValueError):
            kernel_regression = KernelRegression()
            x = np.arange(1, 6, dtype=float)
            y = np.arange(1, 5, dtype=float)
            kernel_regression._fit(x, y)

    def test_kernel_regression_correct_prediction(self):
        """KernelRegression should calculate the correct predictions."""
        kernel_regression = KernelRegression(bandwidth=1.8)
        x = np.array([1, 2, 3, 4, 5], dtype=float)
        y = np.array([1, 4, 6, 4, 1], dtype=float)
        kernel_regression._fit(x, y)

        x_predict = np.array([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5], dtype=float)
        y_true = np.array([2.0008, 2.7264, 3.2511, 3.5680, 3.6740, 3.5680, 3.2511, 2.7264, 2.0008], dtype=float)
        y_predict = kernel_regression._predict(x_predict)

        # Check that the predictions are close to the expected true values
        self.assertTrue(np.allclose(y_true, y_predict, atol=1e-4))


if __name__ == '__main__':
    unittest.main()
