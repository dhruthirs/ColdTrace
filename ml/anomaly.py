import numpy as np
from sklearn.ensemble import IsolationForest


def train(temperatures):
    X = np.asarray(temperatures, dtype=float).reshape(-1, 1)
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    return model


def predict(model, temperature):
    result = model.predict([[temperature]])[0]
    return {
        "is_anomaly": result == -1,
        "label": "ANOMALY" if result == -1 else "NORMAL"
    }


def detect_anomaly(temperatures):
    if len(temperatures) < 2:
        return False

    # Temperature rising too quickly
    rate = temperatures[-1] - temperatures[-2]

    if rate >= 0.4:
        return True

    return False


def detect_cooling_failure(temperatures, cooling):
    if not cooling or len(temperatures) < 3:
        return False

    recent = temperatures[-3:]

    # Cooling is ON but temperature keeps rising
    if recent[0] < recent[1] < recent[2]:
        return True

    return False
