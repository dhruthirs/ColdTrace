# Architecture

ESP32 + SHT20
    -> telemetry JSON
FastAPI backend
    -> SQLite telemetry/events
    -> ML inference
React dashboard

Before hardware is available:
Telemetry Simulator -> FastAPI -> SQLite -> ML -> React

Telemetry contract:
{
  "device_id": "CT001",
  "timestamp": "2026-09-19T00:00:00",
  "temperature": 6.4,
  "humidity": 58.2,
  "cooling": false
}
