from collections import deque
from typing import List, Dict, Any

class MetricsBufferCache:
    """In-memory ring buffer caching metrics & alerts for low-latency clients."""
    
    def __init__(self, maxlen: int = 50):
        self.buffer = deque(maxlen=maxlen)
        self.alerts = deque(maxlen=20)

    def add_metric(self, metric: Dict[str, Any]):
        self.buffer.append(metric)

    def add_alert(self, alert: Dict[str, Any]):
        self.alerts.append(alert)

    def get_recent_metrics(self) -> List[Dict[str, Any]]:
        return list(self.buffer)

    def get_recent_alerts(self) -> List[Dict[str, Any]]:
        return list(self.alerts)
