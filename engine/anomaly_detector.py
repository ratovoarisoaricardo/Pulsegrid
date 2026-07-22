import numpy as np
from typing import List, Dict, Any

class RealTimeAnomalyDetector:
    """Statistical Z-Score & ML Anomaly Detector for streaming metrics."""
    
    def __init__(self, window_size: int = 30, z_threshold: float = 2.5):
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.history: List[float] = []

    def detect(self, metric_value: float) -> Dict[str, Any]:
        """Evaluates incoming metric value and determines if it is an anomaly."""
        self.history.append(metric_value)
        if len(self.history) > self.window_size:
            self.history.pop(0)

        if len(self.history) < 5:
            return {"is_anomaly": False, "z_score": 0.0, "reason": "Warming up"}

        mean = np.mean(self.history[:-1])
        std = np.std(self.history[:-1])
        
        if std == 0:
            std = 0.001

        z_score = (metric_value - mean) / std
        is_anomaly = abs(z_score) > self.z_threshold

        return {
            "is_anomaly": bool(is_anomaly),
            "z_score": round(float(z_score), 2),
            "mean_baseline": round(float(mean), 2),
            "reason": f"Z-score {z_score:.2f} exceeded threshold {self.z_threshold}" if is_anomaly else "Normal"
        }
