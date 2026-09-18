import numpy as np
from sklearn.ensemble import IsolationForest

def train(temperatures):
    X = np.asarray(temperatures, dtype=float).reshape(-1, 1)
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    return model

def predict(model, temperature):
    result = model.predict([[temperature]])[0]
    return {"is_anomaly": result == -1, "label": "ANOMALY" if result == -1 else "NORMAL"}
