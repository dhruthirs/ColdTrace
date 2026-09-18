import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import {LineChart,Line,XAxis,YAxis,CartesianGrid,Tooltip,ResponsiveContainer} from "recharts";
import "./style.css";

const API="http://127.0.0.1:8000";

function App(){
 const [latest,setLatest]=useState(null),[history,setHistory]=useState([]),[events,setEvents]=useState([]);
 async function refresh(){
  const [a,b,c]=await Promise.all([
   fetch(API+"/api/latest").then(r=>r.json()),
   fetch(API+"/api/history?limit=60").then(r=>r.json()),
   fetch(API+"/api/events?limit=20").then(r=>r.json())
  ]);
  setLatest(a.data);setHistory(b.data);setEvents(c.data);
 }
 useEffect(()=>{refresh();const id=setInterval(refresh,2000);return()=>clearInterval(id)},[]);
 const t=latest?.temperature, h=latest?.humidity;
 const status=t==null?"WAITING":t>=7.5?"HIGH TEMP":t<2?"LOW TEMP":latest.cooling?"COOLING":"NORMAL";
 return <main>
  <header><div><h1>ColdTrace</h1><p>Smart Cold-Chain Monitoring</p></div><span>CT001 • ONLINE</span></header>
  <section className="cards">
   <Card title="Temperature" value={t==null?"--":t+"°C"} sub={status}/>
   <Card title="Humidity" value={h==null?"--":h+"%"} sub="LIVE"/>
   <Card title="Cooling" value={latest?.cooling?"ON":"OFF"} sub={latest?.cooling?"ACTIVE":"IDLE"}/>
  </section>
  <section className="panel"><h2>Temperature History</h2><div className="chart">
   <ResponsiveContainer width="100%" height="100%"><LineChart data={history}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="timestamp" hide/><YAxis/><Tooltip/><Line type="monotone" dataKey="temperature" dot={false}/></LineChart></ResponsiveContainer>
  </div></section>
  <section className="grid">
   <div className="panel"><h2>AI Insights</h2><p>ML integration: <b>in progress</b></p><p>Prototype threshold: 7.5°C</p></div>
   <div className="panel"><h2>Event Log</h2>{events.map(e=><div className="event" key={e.id}><span>{new Date(e.timestamp).toLocaleTimeString()}</span><b>{e.event_type}</b><span>{e.temperature}°C</span></div>)}</div>
  </section>
 </main>
}
function Card({title,value,sub}){return <div className="card"><span>{title}</span><strong>{value}</strong><b>{sub}</b></div>}
createRoot(document.getElementById("root")).render(<App/>);
