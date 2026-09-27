from fastapi import FastAPI
from pydantic import BaseModel
import datetime
import random

app = FastAPI(title="ML Инференс-Ядро", description="Онлайн-прогнозирование задержек")

class TelemetryPacket(BaseModel):
    tr_id: str
    target_stop_id: str
    cur_dev_s: float
    T: str

@app.post("/predict")
def predict_online(packet: TelemetryPacket):
    try:
        # Корректно вытаскиваем час из строки формата '2026-01-06 02:10:00'
        hour = datetime.datetime.strptime(packet.T, "%Y-%m-%d %H:%M:%S").hour
    except:
        hour = 12
        
    base_delay = packet.cur_dev_s
    
    # Эмулируем влияние утреннего и вечернего часа пик на заторы
    if hour in:
        traffic_factor = random.uniform(40.0, 110.0)
    else:
        traffic_factor = random.uniform(-15.0, 20.0)

    prediction = base_delay + traffic_factor
    
    if prediction > 120:
        color = "red"
        reason = f"Затор на подходе к узлу {packet.target_stop_id}"
    elif prediction > 60:
        color = "yellow"
        reason = "Плотное движение, повышенный риск"
    else:
        color = "green"
        reason = "Движение в пределах нормы графика"

    return {
        "tr_id": packet.tr_id,
        "prediction_horizon": "10-15 min",
        "predicted_delay_seconds": round(prediction, 1),
        "status_color": color,
        "pattern_reason": reason
    }

