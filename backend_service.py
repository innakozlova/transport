from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import random

app = FastAPI(title="Транспортный Бэкенд & Дашборд")

def get_mock_buses():
    bus_ids = ["132430", "133300", "122048", "122613", "131672"]
    stops = ["399.0", "266.0", "66.0", "72.0", "440.0"]
    buses_data = []
    
    for b, s in zip(bus_ids, stops):
        try:
            # Делаем HTTP-запрос к контейнеру ml_core по его внутреннему имени в Docker
            res = requests.post("http://ml_core:8001/predict", json={
                "tr_id": b,
                "target_stop_id": s,
                "cur_dev_s": float(random.randint(15, 140)),
                "T": "2026-01-06 18:30:00"
            }, timeout=2).json()
        except Exception as e:
            # Режим Graceful Degradation (Мягкая деградация при сбое связи)
            res = {
                "predicted_delay_seconds": float(random.randint(15, 140)), 
                "status_color": "yellow", 
                "pattern_reason": "Автономный режим (деградация связи)"
            }
            
        buses_data.append({
            "id": b,
            "stop": s,
            "delay": res["predicted_delay_seconds"],
            "color": res["status_color"],
            "reason": res["pattern_reason"]
        })
    return buses_data

@app.get("/", response_class=HTMLResponse)
def dashboard():
    buses = get_mock_buses()
    
    html_content = """
    <html>
        <head>
            <title>Дашборд Диспетчера МосТранс</title>
            <meta http-equiv="refresh" content="3">
            <style>
                body { font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px; color: #333; }
                h1 { color: #1a3a5f; }
                .card { background: white; padding: 15px; margin: 12px 0; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;}
                .red { border-left: 8px solid #ff4d4d; }
                .yellow { border-left: 8px solid #ffcc00; }
                .green { border-left: 8px solid #2ecc71; }
                .badge { padding: 6px 12px; border-radius: 4px; color: white; font-weight: bold; }
                .bg-red { background: #ff4d4d; } .bg-yellow { background: #ffcc00; color: black; } .bg-green { background: #2ecc71; }
            </style>
        </head>
        <body>
            <h1>🚏 Мониторинг задержек наземного транспорта (Горизонт 10-15 мин)</h1>
            <p><i>Статус: Интеграция с ML-ядром активна. Обновление каждые 3 секунды...</i></p>
    """
    for bus in buses:
        html_content += f"""
        <div class="card {bus['color']}">
            <div>
                <h3 style="margin: 0 0 5px 0;">Транспортное средство ID: {bus['id']}</h3>
                <p style="margin: 0;">Целевая остановка: {bus['stop']} | <b>Анализ паттерна:</b> {bus['reason']}</p>
            </div>
            <div class="badge bg-{bus['color']}">Прогноз: +{bus['delay']} сек</div>
        </div>
        """
    html_content += "</body></html>"
    return html_content

