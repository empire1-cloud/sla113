/**
 * App.sla113.js — Standalone SLA113 Operator OS Build
 * EVOLVED from App.js — removes Empire 1 routes, shows ONLY SLA113 admin
 * This build deploys to sla113.southernlifestyle.org
 * NO LOGIN GATE — Sovereign operator mode, domain-locked security only
 */
import "@/App.css";
import { BrowserRouter } from "react-router-dom";
import SLA113App from "./sla113/SLA113App.standalone.jsx";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <SLA113App />
      </BrowserRouter>
    </div>
  );
}

export default App;
