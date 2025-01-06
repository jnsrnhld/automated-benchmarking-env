import numpy as np


class MeanRelativeError(object):
    def __call__(self, y_pred, y):
        return np.mean(np.abs((y_pred - y) / y))


def cv_score(models, splits):
    scores = np.zeros((len(models), len(splits)))
    loss_func = MeanRelativeError()

    for i, ((xtrain, ytrain), (xtest, ytest)) in enumerate(splits):
        for j, model in enumerate(models):
            model.fit((xtrain, ytrain))
            ypred = model.predict((xtest, ytest))
            scores[j, i] = loss_func(ypred, ytest)

    return scores
