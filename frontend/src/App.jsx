import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import UploadData from "./components/UploadData";
import BudgetSettings from "./components/BudgetSettings";
import "./App.css";

function Dashboard() {
  return (
    <section className="page-section">
      <div className="page-header">
        <span className="eyebrow">ECONOCAUSAL</span>
        <h1>Causal Campaign Dashboard</h1>
        <p>Manage campaign data and budget constraints from one place.</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <span>01</span>
          <h2>Upload Data</h2>
          <p>Load historical campaign data for the causal analysis pipeline.</p>
        </div>
        <div className="dashboard-card">
          <span>02</span>
          <h2>Budget Settings</h2>
          <p>Configure campaign budget and maximum discount constraints.</p>
        </div>
      </div>
    </section>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<UploadData />} />
        <Route path="/budget" element={<BudgetSettings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
