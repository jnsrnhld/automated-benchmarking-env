import numpy as np
from typing import List, Iterator, Tuple, Callable
from univariate_predictor import UnivariatePredictor


class CrossValidation:
    @staticmethod
    def cross_validation_score(
            models: List[UnivariatePredictor],
            splits: Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
            loss_function: Callable[[np.ndarray, np.ndarray], float]
    ) -> np.ndarray:
        """
        Evaluates multiple models using cross-validation splits and a loss function.

        Args:
            models (List[UnivariatePredictor]): A list of models to evaluate.
            splits (Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]): An iterator over
                tuples containing training and testing splits: (x_train, y_train, x_test, y_test).
            loss_function (Callable[[np.ndarray, np.ndarray], float]): A function that computes the loss
                between predicted and actual values.

        Returns:
            np.ndarray: A 2D array of shape (num_models, num_splits) containing the loss scores.
        """
        # Initialize a list to hold scores for each model
        scores = [[] for _ in models]

        # Iterate over each cross-validation split
        for x_train, y_train, x_test, y_test in splits:
            # Evaluate each model on the current split
            for idx, model in enumerate(models):
                # Fit the model and make predictions
                model.fit(x_train, y_train)
                y_predict = model.predict(x_test)

                # Compute the loss
                score = loss_function(y_predict, y_test)
                scores[idx].append(score)

        # Convert the list of scores into a NumPy array
        scores_matrix = np.array(scores)
        return scores_matrix
