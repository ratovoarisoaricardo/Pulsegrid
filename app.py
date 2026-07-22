import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List

from engine.stream_simulator import MetricsStreamSimulator
from engine.anomaly_detector import RealTimeAnomalyDetector
from engine.redis_cache import MetricsBufferCache

app = FastAPI(title="PulseGrid AI", description="Real-time Streaming Analytics & Anomaly Detection Engine")

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Core Engine Components
simulator = MetricsStreamSimulator()
detector = RealTimeAnomalyDetector(window_size=20, z_threshold=2.2)
cache = MetricsBufferCache(maxlen=50)

class ConnectionManager:
    """Manages active WebSocket client connections."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.get("/")
async def get_dashboard():
    """Serves the main real-time dashboard HTML."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws/metrics")
async def websocket_metrics_endpoint(websocket: WebSocket):
    """WebSocket endpoint streaming high-frequency metrics & instant anomaly alerts."""
    await manager.connect(websocket)
    try:
        while True:
            # Generate metric point
            metric = simulator.generate_metric()
            
            # Run anomaly detection on latency
            anomaly_res = detector.detect(metric["latency"])
            
            packet = {
                "metric": metric,
                "anomaly": anomaly_res
            }
            
            cache.add_metric(packet)
            if anomaly_res["is_anomaly"]:
                cache.add_alert(packet)

            await websocket.send_text(json.dumps(packet))
            await asyncio.sleep(1.0)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
