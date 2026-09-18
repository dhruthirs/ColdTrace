# ColdTrace
Smart cold-chain monitoring and active temperature-control prototype.

Modules:
- firmware/ : ESP32 + SHT20 + OLED + motor driver/Peltier
- backend/  : FastAPI + SQLite
- ml/       : anomaly detection / prediction
- frontend/ : React dashboard
- simulator/: software-only telemetry for development without hardware
- integration/: end-to-end tests
- docs/     : architecture, API contract, team ownership

Development flow:
Simulator -> FastAPI -> SQLite -> ML -> React Dashboard

Hardware flow later:
ESP32/SHT20 -> FastAPI -> SQLite -> ML -> React Dashboard

Prototype thresholds only:
Cooling ON >= 7.5 C
Cooling OFF <= 5.8 C
Low warning < 2.0 C

This is a hackathon engineering prototype, not a validated/certified vaccine carrier.
