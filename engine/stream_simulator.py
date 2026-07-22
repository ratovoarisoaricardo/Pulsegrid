import random
import time

class MetricsStreamSimulator:
    """Simulates a high-frequency real-time stream of IoT/System metrics with periodic anomaly spikes."""
    
    def __init__(self):
        self.base_latency = 45.0  # ms
        self.base_throughput = 1200  # req/sec
        self.base_cpu = 35.0  # %
        self.step = 0

    def generate_metric(self) -> dict:
        """Generates a single metric data point with timestamp and potential synthetic anomaly."""
        self.step += 1
        
        # Introduce periodic synthetic anomaly spike every 15 steps
        is_anomaly_spike = (self.step % 15 == 0)
        
        if is_anomaly_spike:
            latency = self.base_latency + random.uniform(150.0, 350.0)
            cpu = min(100.0, self.base_cpu + random.uniform(45.0, 60.0))
            throughput = self.base_throughput + random.uniform(2000.0, 4000.0)
        else:
            latency = max(10.0, self.base_latency + random.gauss(0, 5.0))
            cpu = max(5.0, min(100.0, self.base_cpu + random.gauss(0, 3.0)))
            throughput = max(100.0, self.base_throughput + random.gauss(0, 100.0))

        return {
            "timestamp": time.strftime("%H:%M:%S"),
            "step": self.step,
            "latency": round(latency, 2),
            "cpu_usage": round(cpu, 2),
            "throughput": int(throughput),
            "synthetic_spike": is_anomaly_spike
        }
