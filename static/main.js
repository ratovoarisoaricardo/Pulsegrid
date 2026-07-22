let chart;
const maxPoints = 25;
const labels = [];
const latencyData = [];

function initChart() {
  const ctx = document.getElementById('liveChart').getContext('2d');
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'API Latency (ms)',
        data: latencyData,
        borderColor: '#00d2ff',
        backgroundColor: 'rgba(0, 210, 255, 0.1)',
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      scales: {
        x: { ticks: { color: '#a0a0b0' } },
        y: { ticks: { color: '#a0a0b0' }, beginAtZero: true }
      },
      plugins: {
        legend: { labels: { color: '#ffffff' } }
      }
    }
  });
}

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/metrics`;
  const ws = new WebSocket(wsUrl);

  const statusBadge = document.getElementById('connection-status');

  ws.onopen = () => {
    statusBadge.innerText = 'WebSocket: Connected ⚡';
    statusBadge.className = 'status-badge status-connected';
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const m = data.metric;
    const a = data.anomaly;

    // Update Top Metric Cards
    document.getElementById('val-latency').innerText = `${m.latency} ms`;
    document.getElementById('val-cpu').innerText = `${m.cpu_usage} %`;
    document.getElementById('val-throughput').innerText = `${m.throughput} req/s`;
    
    const anomalyVal = document.getElementById('val-anomaly');
    if (a.is_anomaly) {
      anomalyVal.innerText = '🚨 ANOMALY';
      anomalyVal.style.color = '#ff4b4b';
    } else {
      anomalyVal.innerText = 'Normal';
      anomalyVal.style.color = '#00e676';
    }

    // Push data to Live Chart
    labels.push(m.timestamp);
    latencyData.push(m.latency);

    if (labels.length > maxPoints) {
      labels.shift();
      latencyData.shift();
    }

    chart.update();

    // Trigger Alert Item if Anomaly
    if (a.is_anomaly) {
      const alertsList = document.getElementById('alerts-list');
      const emptyMsg = alertsList.querySelector('.empty-msg');
      if (emptyMsg) emptyMsg.remove();

      const alertItem = document.createElement('div');
      alertItem.className = 'alert-item';
      alertItem.innerHTML = `
        <strong>🚨 Anomaly Spike Detected at ${m.timestamp}</strong><br/>
        <small>Latency: <strong>${m.latency} ms</strong> | ${a.reason}</small>
      `;
      alertsList.prepend(alertItem);
    }
  };

  ws.onclose = () => {
    statusBadge.innerText = 'WebSocket: Disconnected (Retrying...)';
    statusBadge.className = 'status-badge status-connecting';
    setTimeout(connectWebSocket, 3000);
  };
}

document.addEventListener('DOMContentLoaded', () => {
  initChart();
  connectWebSocket();
});
