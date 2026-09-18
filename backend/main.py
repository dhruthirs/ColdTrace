from datetime import datetime, timezone
import sqlite3
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    previous = c.execute("SELECT cooling FROM telemetry WHERE device_id=? ORDER BY id DESC LIMIT 1", (data.device_id,)).fetchone()
    c.execute("INSERT INTO telemetry(device_id,timestamp,temperature,humidity,cooling) VALUES(?,?,?,?,?)",
              (data.device_id, ts, data.temperature, data.humidity, int(data.cooling)))

    event = None
    if previous is not None and bool(previous["cooling"]) != data.cooling:
        event = "COOLING_ON" if data.cooling else "COOLING_OFF"
    elif data.temperature < 2.0:
        event = "LOW_TEMP"
    elif data.temperature >= 7.5:
        event = "HIGH_TEMP"

    if event:
        c.execute("INSERT INTO events(device_id,timestamp,event_type,temperature) VALUES(?,?,?,?)",
                  (data.device_id, ts, event, data.temperature))
    c.commit()
    c.close()
    return {"accepted": True, "event": event}

@app.get("/api/latest")
def latest(device_id="CT001"):
    c = conn()
    r = c.execute("SELECT * FROM telemetry WHERE device_id=? ORDER BY id DESC LIMIT 1", (device_id,)).fetchone()
    c.close()
    return {"data": dict(r) if r else None}

@app.get("/api/history")
def history(device_id="CT001", limit=100):
    c = conn()
    rows = c.execute("SELECT * FROM telemetry WHERE device_id=? ORDER BY id DESC LIMIT ?", (device_id, min(limit,1000))).fetchall()
    c.close()
    return {"data": [dict(r) for r in reversed(rows)]}

@app.get("/api/events")
def events(device_id="CT001", limit=100):
    c = conn()
    rows = c.execute("SELECT * FROM events WHERE device_id=? ORDER BY id DESC LIMIT ?", (device_id, min(limit,500))).fetchall()
    c.close()
    return {"data": [dict(r) for r in rows]}
