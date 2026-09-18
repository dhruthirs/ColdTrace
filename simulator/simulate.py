import time, random, requests
from datetime import datetime, timezone

URL = "http://127.0.0.1:8000/api/telemetry"
temperature = 5.5
cooling = False

while True:
    if cooling:
        temperature -= 0.18
        if temperature <= 5.8:
            cooling = False
    else:
        temperature += 0.08
        if temperature >= 7.5:
            cooling = True

    temperature += random.uniform(-0.03, 0.03)
    payload = {
        "device_id": "CT001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": round(temperature, 2),
        "humidity": round(58 + random.uniform(-1.5, 1.5), 1),
        "cooling": cooling
    }

    try:
        r = requests.post(URL, json=payload, timeout=3)
        print(payload, "->", r.json())
    except requests.RequestException as e:
        print("Backend unavailable:", e)
    time.sleep(2)
