from datetime import datetime, timezone
import sqlite3
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ml.trend import calculate_trend, calculate_rate
from ml.anomaly import detect_anomaly, detect_cooling_failure

DB = Path(__file__).parent / "coldtrace.db"
app = FastAPI(title="ColdTrace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Telemetry(BaseModel):
    device_id: str = "CT001"
    timestamp: str | None = None
    temperature: float
    humidity: float
    cooling: bool

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.execute("CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT, timestamp TEXT, temperature REAL, humidity REAL, cooling INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT, timestamp TEXT, event_type TEXT, temperature REAL)")
    c.commit()
    c.close()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/telemetry")
def telemetry(data: Telemetry):
    ts = data.timestamp or datetime.now(timezone.utc).isoformat()

    c = conn()

    previous = c.execute(
        "SELECT * FROM telemetry WHERE device_id=? ORDER BY id DESC LIMIT 1",
        (data.device_id,)
    ).fetchone()

    # Get recent temperatures for anomaly detection
    recent_rows = c.execute(
        """
        SELECT temperature
        FROM telemetry
        WHERE device_id=?
        ORDER BY id DESC
        LIMIT 10
        """,
        (data.device_id,)
    ).fetchall()

    temperatures = [row["temperature"] for row in reversed(recent_rows)]

    # Include the new temperature
    temperatures.append(data.temperature)

    # Store telemetry
    c.execute(
        """
        INSERT INTO telemetry(
            device_id,
            timestamp,
            temperature,
            humidity,
            cooling
        )
        VALUES(?,?,?,?,?)
        """,
        (
            data.device_id,
            ts,
            data.temperature,
            data.humidity,
            int(data.cooling)
        )
    )

      

    event = None

# New anomaly detection
    anomaly = detect_anomaly(temperatures)

# New cooling-failure detection
    cooling_failure = detect_cooling_failure(
       temperatures,
       data.cooling
)

# Check the most recent event
    last_event = c.execute(
    """
       SELECT event_type
       FROM events
       WHERE device_id=?
       ORDER BY id DESC
       LIMIT 1
    """,
    (data.device_id,)
).fetchone()

    last_event_type = last_event["event_type"] if last_event else None


# -------------------------
# ABNORMAL EVENTS
# -------------------------

    if cooling_failure:

    # Avoid duplicate COOLING_FAILURE events
        if last_event_type != "COOLING_FAILURE":
           event = "COOLING_FAILURE"

    elif anomaly:

    # Avoid duplicate ANOMALY_DETECTED events
        if last_event_type != "ANOMALY_DETECTED":
           event = "ANOMALY_DETECTED"


# -------------------------
# NORMAL / EXISTING EVENTS
# -------------------------

    elif previous is not None and bool(previous["cooling"]) != data.cooling:

        event = "COOLING_ON" if data.cooling else "COOLING_OFF"

    elif data.temperature < 2.0:

        event = "LOW_TEMP"

    elif data.temperature >= 7.5:

        event = "HIGH_TEMP"


# -------------------------
# RECOVERY
# -------------------------

    elif last_event_type in [
    "COOLING_FAILURE",
    "ANOMALY_DETECTED",
    "HIGH_TEMP",
    "LOW_TEMP"
]:

      if data.temperature >= 2.0 and data.temperature < 7.5:
        event = "RECOVERY"
    if event:
        c.execute(
            """
            INSERT INTO events(
                device_id,
                timestamp,
                event_type,
                temperature
            )
            VALUES(?,?,?,?)
            """,
            (
                data.device_id,
                ts,
                event,
                data.temperature
            )
        )

    c.commit()
    c.close()

    return {
        "accepted": True,
        "event": event,
        "anomaly": anomaly,
        "cooling_failure": cooling_failure
    }

@app.get("/api/latest")
def latest(device_id="CT001"):
    c = conn()
    r = c.execute("SELECT * FROM telemetry WHERE device_id=? ORDER BY id DESC LIMIT 1", (device_id,)).fetchone()
    c.close()
    return {"data": dict(r) if r else None}

@app.get("/api/history")
def history(device_id="CT001", limit: int = 100):
    c = conn()
    rows = c.execute("SELECT * FROM telemetry WHERE device_id=? ORDER BY id DESC LIMIT ?", (device_id, min(limit,1000))).fetchall()
    c.close()
    return {"data": [dict(r) for r in reversed(rows)]}

@app.get("/api/events")
def events(device_id="CT001", limit: int = 100):
    c = conn()
    rows = c.execute("SELECT * FROM events WHERE device_id=? ORDER BY id DESC LIMIT ?", (device_id, min(limit,500))).fetchall()
    c.close()
    return {"data": [dict(r) for r in rows]}

@app.get("/api/insights")
def insights(device_id="CT001"):
    c = conn()

    rows = c.execute(
        """
        SELECT temperature, humidity, cooling
        FROM telemetry
        WHERE device_id=?
        ORDER BY id DESC
        LIMIT 10
        """,
        (device_id,)
    ).fetchall()

    c.close()

    if not rows:
        return {
            "temperature": None,
            "humidity": None,
            "cooling": False,
            "trend": "INSUFFICIENT_DATA",
            "rate": 0.0,
            "anomaly": False,
            "risk": "UNKNOWN"
        }

    # Reverse so oldest reading comes first
    rows = list(reversed(rows))

    temperatures = [row["temperature"] for row in rows]

    current_temperature = temperatures[-1]
    current_humidity = rows[-1]["humidity"]
    current_cooling = bool(rows[-1]["cooling"])

       # Calculate temperature trend and rate
    trend = calculate_trend(temperatures)
    rate = calculate_rate(temperatures)

    anomaly = detect_anomaly(temperatures)
    cooling_failure = detect_cooling_failure(
        temperatures,
        current_cooling
)

    # Basic risk assessment
    if current_temperature >= 7.5:
        risk = "HIGH"
    elif current_temperature < 2.0:
        risk = "LOW_TEMP"
    elif trend == "RISING" and current_cooling:
        risk = "WATCH"
    else:
        risk = "NORMAL"

    return {
    "temperature": current_temperature,
    "humidity": current_humidity,
    "cooling": current_cooling,
    "trend": trend,
    "rate": rate,
    "anomaly": anomaly,
    "cooling_failure": cooling_failure,
    "risk": risk
}
