import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import "./style.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [events, setEvents] = useState([]);
  const [insights, setInsights] = useState(null);

  async function refresh() {
    try {
      const [a, b, c, d] = await Promise.all([
        fetch(API + "/api/latest").then(r => r.json()),
        fetch(API + "/api/history?limit=60").then(r => r.json()),
        fetch(API + "/api/events?limit=20").then(r => r.json()),
        fetch(API + "/api/insights").then(r => r.json())
        
      ]);

      setLatest(a.data);
      setHistory(b.data);
      setEvents(c.data);
      setInsights(d);
    } catch (error) {
      console.error("Backend unavailable:", error);
    }
  }

  useEffect(() => {
    refresh();

    const id = setInterval(refresh, 2000);

    return () => clearInterval(id);
  }, []);

  const t = latest?.temperature;
  const h = latest?.humidity;

  const status =
    t == null
      ? "WAITING"
      : t >= 7.5
        ? "HIGH TEMP"
        : t < 2
          ? "LOW TEMP"
          : latest.cooling
            ? "COOLING"
            : "NORMAL";

  return (
    <main>
      <header>
        <div>
          <h1>ColdTrace</h1>
          <p>Smart Cold-Chain Monitoring</p>
        </div>

        <span>CT001 • ONLINE</span>
      </header>

      <section className="cards">
        <Card
          title="Temperature"
          value={t == null ? "--" : t + "°C"}
          sub={status}
        />

        <Card
          title="Humidity"
          value={h == null ? "--" : h + "%"}
          sub="LIVE"
        />

        <Card
          title="Cooling"
          value={latest?.cooling ? "ON" : "OFF"}
          sub={latest?.cooling ? "ACTIVE" : "IDLE"}
        />
      </section>

      <section className="panel">
        <h2>Temperature History</h2>

        <div className="chart">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" hide />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="temperature"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="grid">

        <div className="panel">
  <h2>AI Insights</h2>

  {insights ? (
    <>
      <div className="insight-row">
        <span>Trend</span>
        <b>{insights.trend}</b>
      </div>

      <div className="insight-row">
        <span>Temperature Rate</span>
        <b>{insights.rate}°C/sample</b>
      </div>

      <div className="insight-row">
        <span>Anomaly</span>
        <b>{insights.anomaly ? "DETECTED" : "NONE"}</b>
      </div>

      <div className="insight-row">
        <span>Cooling Failure</span>
        <b>
          {insights.cooling_failure ? "DETECTED" : "NONE"}
        </b>
      </div>

      <div className="insight-row">
        <span>Risk Level</span>
        <b>{insights.risk}</b>
      </div>

      <div className="insight-message">
        {insights.cooling_failure
          ? "Temperature is rising while cooling is ON. Possible cooling failure detected."
          : insights.anomaly
            ? "Rapid temperature change detected. The system is monitoring the condition."
            : insights.trend === "RISING"
              ? "Temperature is gradually rising. Continue monitoring the cold-chain condition."
              : insights.trend === "FALLING"
                ? "Temperature is falling and the system is monitoring for low-temperature conditions."
                : "Temperature conditions are currently stable."}
      </div>
    </>
  ) : (
    <p>Loading AI insights...</p>
  )}
</div>
        

        <div className="panel">
          <h2>Event Log</h2>

          {events.length === 0 ? (
            <p>No events recorded.</p>
          ) : (
            events.map(e => (
              <div className="event" key={e.id}>
                <span>
                  {new Date(e.timestamp).toLocaleTimeString()}
                </span>

                <b>{e.event_type}</b>

                <span>{e.temperature}°C</span>
              </div>
            ))
          )}
        </div>

      </section>
    </main>
  );
}

function Card({ title, value, sub }) {
  return (
    <div className="card">
      <span>{title}</span>
      <strong>{value}</strong>
      <b>{sub}</b>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);