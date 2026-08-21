import React, { useState } from "react";
import { saveDataset } from "../services/storage";
import "./UploadData.css";

const UploadData = () => {
  const [file, setFile] = useState(null);
  const [dataset, setDataset] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const parseCSV = (text) => {
    const lines = text
      .trim()
      .split(/\r?\n/)
      .filter(Boolean);

    if (lines.length < 2) {
      throw new Error(
        "CSV file is empty or contains no data."
      );
    }

    const headers = lines[0]
      .split(",")
      .map((header) => header.trim());

    const rows = lines.slice(1).map((line) => {
      const values = line.split(",");
      const row = {};

      headers.forEach((header, index) => {
        row[header] =
          values[index]?.trim() ?? "";
      });

      return row;
    });

    return {
      headers,
      rows,
    };
  };

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0];

    setError("");
    setDataset(null);
    setFile(null);

    if (!selectedFile) {
      return;
    }

    if (
      !selectedFile.name
        .toLowerCase()
        .endsWith(".csv")
    ) {
      setError("Please upload a CSV file.");
      return;
    }

    if (selectedFile.size === 0) {
      setError("The selected file is empty.");
      return;
    }

    setFile(selectedFile);
  };

  const handleUpload = () => {
    if (!file) {
      setError(
        "Please select a CSV file first."
      );
      return;
    }

    setLoading(true);
    setError("");

    const reader = new FileReader();

    reader.onload = (event) => {
      try {
        const text = event.target.result;

        const parsed = parseCSV(text);

        const datasetInfo = {
          fileName: file.name,
          rows: parsed.rows.length,
          columns: parsed.headers.length,
          headers: parsed.headers,
          preview: parsed.rows.slice(0, 10),
          uploadedAt:
            new Date().toISOString(),
        };

        saveDataset(datasetInfo);

        setDataset(datasetInfo);
        setLoading(false);
      } catch (err) {
        console.error(err);

        setError(
          err.message ||
            "Unable to process CSV file."
        );

        setLoading(false);
      }
    };

    reader.onerror = () => {
      setError(
        "Unable to read the selected file."
      );

      setLoading(false);
    };

    reader.readAsText(file);
  };

  return (
    <div className="upload-page">
      <div className="upload-container">

        <div className="page-header">
          <span className="page-label">
            DATA MANAGEMENT
          </span>

          <h1>
            Upload Campaign Data
          </h1>

          <p>
            Upload historical customer campaign
            data for validation and analysis.
          </p>
        </div>

        <div className="upload-card">

          <label className="upload-box">

            <div className="upload-icon">
              ↑
            </div>

            <h3>
              Select CSV Dataset
            </h3>

            <p>
              Upload your cleaned retail
              campaign dataset.
            </p>

            <span className="file-button">
              Choose CSV File
            </span>

            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
            />

          </label>

          {file && (
            <div className="selected-file">
              <span>
                Selected file
              </span>

              <strong>
                {file.name}
              </strong>
            </div>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button
            className="primary-button upload-button"
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading
              ? "Processing..."
              : "Upload & Validate"}
          </button>

        </div>

        {dataset && (
          <div className="dataset-result">

            <div className="success-message">
              ✓ Dataset uploaded and validated
              successfully.
            </div>

            <div className="dataset-stats">

              <div>
                <span>Rows</span>
                <strong>
                  {dataset.rows}
                </strong>
              </div>

              <div>
                <span>Columns</span>
                <strong>
                  {dataset.columns}
                </strong>
              </div>

              <div>
                <span>File</span>
                <strong>
                  {dataset.fileName}
                </strong>
              </div>

            </div>

            <div className="columns-section">
              <h2>Columns</h2>

              <div className="column-list">
                {dataset.headers.map(
                  (column) => (
                    <span key={column}>
                      {column}
                    </span>
                  )
                )}
              </div>
            </div>

            <div className="preview-section">
              <h2>Data Preview</h2>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      {dataset.headers.map(
                        (column) => (
                          <th key={column}>
                            {column}
                          </th>
                        )
                      )}
                    </tr>
                  </thead>

                  <tbody>
                    {dataset.preview.map(
                      (row, rowIndex) => (
                        <tr key={rowIndex}>
                          {dataset.headers.map(
                            (column) => (
                              <td key={column}>
                                {row[column]}
                              </td>
                            )
                          )}
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
};

export default UploadData;