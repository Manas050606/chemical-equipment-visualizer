import React, { useState } from "react";
import axios from "axios";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { Bar, Pie } from "react-chartjs-2";
import "./App.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
);

function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState(""); // For explorer

  const handleUpload = async () => {
    if (!file) {
      alert("Select file");
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/upload/",
        formData,
      );
      setAnalysis(res.data.current_analysis);
      setActiveTab("dashboard");
    } catch (err) {
      alert("Error connecting to backend");
    } finally {
      setLoading(false);
    }
  };

  const renderDashboard = () => (
    <div className="fade-in">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Units</div>
          <div className="stat-value">{analysis.total_count}</div>
        </div>
        {Object.entries(analysis.averages).map(([k, v]) => (
          <div className="stat-card" key={k}>
            <div className="stat-label">Avg {k}</div>
            <div className="stat-value">{v.toFixed(1)}</div>
          </div>
        ))}
      </div>
      <div className="charts-wrapper">
        <div className="chart-card">
          <h3>Equipment Distribution</h3>
          <div style={{ flex: 1, position: "relative" }}>
            <Bar
              data={{
                labels: Object.keys(analysis.distribution),
                datasets: [
                  {
                    label: "Count",
                    data: Object.values(analysis.distribution),
                    backgroundColor: "#3b82f6",
                    borderRadius: 4,
                  },
                ],
              }}
              options={{ maintainAspectRatio: false }}
            />
          </div>
        </div>
        <div className="chart-card">
          <h3>Composition</h3>
          <div style={{ flex: 1, position: "relative" }}>
            <Pie
              data={{
                labels: Object.keys(analysis.distribution),
                datasets: [
                  {
                    data: Object.values(analysis.distribution),
                    backgroundColor: ["#3b82f6", "#10b981", "#f59e0b"],
                  },
                ],
              }}
              options={{ maintainAspectRatio: false }}
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderExplorer = () => {
    // Filter logic
    const data = analysis.full_data || [];
    const filtered = data.filter(
      (item) =>
        item["Equipment Name"]
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        item.Type.toLowerCase().includes(searchTerm.toLowerCase()),
    );

    return (
      <div className="fade-in">
        <div style={{ marginBottom: "20px", display: "flex", gap: "10px" }}>
          <input
            type="text"
            placeholder="Search Equipment (e.g., Pump A)..."
            style={{
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid #e2e8f0",
              width: "300px",
            }}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="stat-card" style={{ padding: 0, overflow: "hidden" }}>
          <table style={{ margin: 0 }}>
            <thead>
              <tr style={{ background: "#f8fafc" }}>
                <th>Name</th>
                <th>Type</th>
                <th>Health</th>
                <th>Action Required</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: "bold" }}>
                    {row["Equipment Name"]}
                  </td>
                  <td>{row.Type}</td>
                  <td>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                      }}
                    >
                      <div
                        style={{
                          width: "50px",
                          height: "6px",
                          background: "#e2e8f0",
                          borderRadius: "3px",
                        }}
                      >
                        <div
                          style={{
                            width: `${row.Health}%`,
                            height: "100%",
                            background: row.Health < 50 ? "#ef4444" : "#10b981",
                            borderRadius: "3px",
                          }}
                        ></div>
                      </div>
                      {row.Health}%
                    </div>
                  </td>
                  <td>{row.Action}</td>
                  <td>
                    <span
                      style={{
                        padding: "4px 8px",
                        borderRadius: "12px",
                        fontSize: "12px",
                        fontWeight: "bold",
                        background: row.Health < 50 ? "#fee2e2" : "#dcfce7",
                        color: row.Health < 50 ? "#991b1b" : "#166534",
                      }}
                    >
                      {row.Priority}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <div
              style={{ padding: "20px", textAlign: "center", color: "#94a3b8" }}
            >
              No matching equipment found.
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <span>⚗️</span> ChemViz Pro
        </div>
        <div className="upload-zone">
          <div style={{ fontSize: "24px", marginBottom: "5px" }}>📂</div>
          <div style={{ fontSize: "12px", color: "#94a3b8" }}>
            {file ? file.name : "Drag CSV"}
          </div>
          <input
            type="file"
            className="file-input"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>
        <button
          className="analyze-btn"
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? "Processing..." : "Analyze"}
        </button>
      </aside>

      <main className="main-content">
        <div className="header-row">
          <h1 className="page-title">Plant Dashboard</h1>
          {analysis && (
            <button
              className="download-btn"
              onClick={() => window.open("http://127.0.0.1:8000/api/report/")}
            >
              📥 Report
            </button>
          )}
        </div>

        {!analysis ? (
          <div
            style={{ textAlign: "center", marginTop: "15vh", color: "#94a3b8" }}
          >
            <h2>Upload Data to Begin</h2>
          </div>
        ) : (
          <>
            <div className="tabs-nav">
              <button
                className={`tab-btn ${activeTab === "dashboard" ? "active" : ""}`}
                onClick={() => setActiveTab("dashboard")}
              >
                Overview
              </button>
              <button
                className={`tab-btn ${activeTab === "explorer" ? "active" : ""}`}
                onClick={() => setActiveTab("explorer")}
              >
                Equipment Explorer
              </button>
            </div>
            {activeTab === "dashboard" && renderDashboard()}
            {activeTab === "explorer" && renderExplorer()}
          </>
        )}
      </main>
    </div>
  );
}
export default App;
