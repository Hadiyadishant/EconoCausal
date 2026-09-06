import { useState } from "react";
import { checkDrift } from "../services/api";
import "./DataMonitoring.css";

const REQUIRED_COLUMNS = [
  "age",
  "income",
  "previous_purchases",
  "customer_tenure_days",
  "avg_basket_size",
  "discount",
  "campaign_response",
  "channel",
  "purchase",
];

const NUMERIC_COLUMNS = [
  "age",
  "income",
  "previous_purchases",
  "customer_tenure_days",
  "avg_basket_size",
  "discount",
  "campaign_response",
  "purchase",
];

const VARIABLE_LABELS = {
  age: "Customer Age",
  income: "Income",
  previous_purchases: "Previous Purchases",
  customer_tenure_days: "Customer Tenure (days)",
  avg_basket_size: "Average Basket Size",
  discount: "Discount Applied",
  campaign_response: "Campaign Response",
  channel: "Purchase Channel",
  purchase: "Purchase Outcome",
};

function parseCSV(text) {
  const lines = text
    .trim()
    .split(/\r?\n/)
    .filter(Boolean);

  if (lines.length < 2) {
    throw new Error("CSV file is empty or contains no data rows.");
  }

  const headers = lines[0].split(",").map((h) => h.trim());

  const missing = REQUIRED_COLUMNS.filter((col) => !headers.includes(col));
  if (missing.length > 0) {
    throw new Error(
      `This file is missing required columns: ${missing.join(", ")}.`
    );
  }

  return lines.slice(1).map((line) => {
    const values = line.split(",");
    const row = {};

    headers.forEach((header, index) => {
      const raw = values[index]?.trim() ?? "";
      row[header] = NUMERIC_COLUMNS.includes(header) ? Number(raw) : raw;
    });

    return row;
  });
}

function DataMonitoring() {
  const [file, setFile] = useState(null);
  const [fileError, setFileError] = useState("");
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleFileChange = (event) => {
    const selected = event.target.files?.[0];

    setFileError("");
    setError("");
    setResult(null);
    setFile(null);

    if (!selected) return;

    if (!selected.name.toLowerCase().endsWith(".csv")) {
      setFileError("Please upload a CSV file.");
      return;
    }

    setFile(selected);
  };

  const handleCheck = () => {
    if (!file) {
      setFileError("Please select a CSV file first.");
      return;
    }

    setChecking(true);
    setError("");
    setResult(null);

    const reader = new FileReader();

    reader.onload = async (event) => {
      try {
        const rows = parseCSV(event.target.result);

        if (rows.length === 0) {
          throw new Error("No data rows found in this file.");
        }

        const response = await checkDrift(rows);
        setResult(response.drift);
      } catch (err) {
        console.error("Drift check error:", err);
        setError(
          err.message || "Unable to check this data for drift."
        );
      } finally {
        setChecking(false);
      }
    };

    reader.onerror = () => {
      setError("Unable to read the selected file.");
      setChecking(false);
    };

    reader.readAsText(file);
  };

  const perVariable = result?.per_variable
    ? Object.entries(result.per_variable)
    : [];

  return (
    <div className="monitoring-page">
      <div className="monitoring-container">

        <div className="page-header">
          <span className="page-label">DATA MONITORING</span>
          <h1>Customer Data Drift Check</h1>
          <p>
            Compare a new batch of customer data against the historical
            baseline to catch changes before they affect campaign results.
          </p>
        </div>

        <div className="monitoring-card">

          <label className="upload-box">
            <div className="upload-icon">↑</div>
            <h3>Select New Customer Data (CSV)</h3>
            <p>
              Needs the columns: {REQUIRED_COLUMNS.join(", ")}.
            </p>
            <span className="file-button">Choose CSV File</span>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
            />
          </label>

          {file && (
            <div className="selected-file">
              <span>Selected file</span>
              <strong>{file.name}</strong>
            </div>
          )}

          {fileError && <div className="monitoring-error-inline">{fileError}</div>}

          <button
            className="primary-button"
            onClick={handleCheck}
            disabled={!file || checking}
          >
            {checking ? "Checking..." : "Check for Drift"}
          </button>

        </div>

        {error && (
          <div className="monitoring-card monitoring-error-card">
            <strong>Unable to complete the drift check</strong>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <>
            <div
              className={`status-banner ${
                result.overall_status === "DRIFT DETECTED"
                  ? "status-warning"
                  : "status-ok"
              }`}
            >
              <strong>
                {result.overall_status === "DRIFT DETECTED"
                  ? "Drift detected"
                  : "No drift detected"}
              </strong>
              <p>
                {result.overall_status === "DRIFT DETECTED"
                  ? "One or more customer attributes in this batch look meaningfully different from the historical baseline. Review the flagged variables below before trusting model predictions on this data."
                  : "This batch of customer data looks statistically consistent with the historical baseline the model was trained on."}
              </p>
            </div>

            <div className="monitoring-table-card">
              <div className="table-header">
                <div>
                  <span>PER-VARIABLE RESULTS</span>
                  <h2>Where does it stand?</h2>
                </div>
                <div className="result-count">
                  Threshold: p &lt; {result.threshold}
                </div>
              </div>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Variable</th>
                      <th>Status</th>
                      <th>p-value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {perVariable.map(([key, value]) => (
                      <tr key={key}>
                        <td>{VARIABLE_LABELS[key] || key}</td>
                        <td>
                          <span
                            className={
                              value.status === "DRIFT WARNING"
                                ? "drift-badge warning"
                                : value.status === "INSUFFICIENT_DATA"
                                ? "drift-badge neutral"
                                : "drift-badge ok"
                            }
                          >
                            {value.status === "DRIFT WARNING"
                              ? "Changed"
                              : value.status === "INSUFFICIENT_DATA"
                              ? "Not enough data"
                              : "Stable"}
                          </span>
                        </td>
                        <td>
                          {value.p_value === null || value.p_value === undefined
                            ? "—"
                            : Number(value.p_value).toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

      </div>
    </div>
  );
}

export default DataMonitoring;
