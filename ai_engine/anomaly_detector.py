from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)

    def train(self, data):
        self.model.fit(data)

    def predict(self, point):
        return self.model.predict([point])[0]  # -1 anomaly, 1 normal
