import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier


def test_numpy_and_pandas_are_available() -> None:
    values = np.array([100.0, 101.5, 102.0])
    frame = pd.DataFrame({"close": values})

    assert frame["close"].tolist() == [100.0, 101.5, 102.0]
    assert np.isclose(frame["close"].mean(), 101.1666666667)


def test_scikit_learn_environment_is_available() -> None:
    model = DummyClassifier(strategy="most_frequent")
    model.fit(np.array([[0], [1]]), np.array([0, 1]))

    assert model.predict(np.array([[2]])).tolist() == [0]
