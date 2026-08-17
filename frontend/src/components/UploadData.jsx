import { useState } from "react";
import "./UploadData.css";

export default function UploadData() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith(".csv")) {
      setFile(null);
      setMessage("Please select a CSV file.");
      return;
    }

    setFile(selectedFile);
    setMessage("CSV file selected successfully.");
  };

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <span className="eyebrow">DATA MANAGEMENT</span>
          <h1>Upload Campaign Data</h1>
          <p>Upload historical customer campaign data for causal analysis.</p>
        </div>
      </div>

      <div className="upload-card">
        <label className="upload-zone" htmlFor="csv-file">
          <div className="upload-icon">↑</div>
          <h2>Upload your CSV dataset</h2>
          <p>Choose a historical campaign dataset to continue.</p>
          <span className="primary-button">Browse CSV</span>
          <input
            id="csv-file"
            type="file"
            accept=".csv,text/csv"
            onChange={handleChange}
            hidden
          />
        </label>

        {file && (
          <div className="selected-file">
            <div>
              <strong>{file.name}</strong>
              <span>{(file.size / 1024).toFixed(1)} KB</span>
            </div>
            <span className="status-badge">Ready</span>
          </div>
        )}

        {message && (
          <p className={`upload-message ${message.includes("successfully") ? "success" : "error"}`}>
            {message}
          </p>
        )}
      </div>
    </section>
  );
}
