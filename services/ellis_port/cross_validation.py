import numpy as np
from typing import List, Iterator, Tuple, Callable
from .univariate_predictor import UnivariatePredictor


def loss_func(ypred, ytest):
    """
    Computes the loss between the predicted and test values.

    Parameters:
    ypred (np.ndarray): Predicted values.
    ytest (np.ndarray): True test values.

    Returns:
    float: The computed loss value.
    """
    return np.mean(np.abs((ypred - ytest) / ytest))


def cross_validation_score(
        models: List[UnivariatePredictor],
        splits: Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]
) -> np.ndarray:
    """
    Evaluates multiple models using cross-validation splits and a loss function.

    Parameters:
    models (List[UnivariatePredictor]): A list of models to evaluate.
    splits (Iterator[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]):
        An iterator that provides train-test splits for cross-validation.

    Returns:
    np.ndarray: An array containing the loss for each model.
    """
    results = []
    for model in models:
        losses = []
        for xtrain, xtest, ytrain, ytest in splits:
            model.fit(xtrain, ytrain)
            ypred = model.predict(xtest)
            losses.append(loss_func(ypred, ytest))
        results.append(np.mean(losses))
    return np.array(results)
