import React, { useState } from "react";
import Papa from "papaparse";

import {
  uploadDataset
} from "../services/api";

import {
  saveDataset
} from "../services/storage";

import "./UploadData.css";


const REQUIRED_COLUMNS = [

  "customer_id",
  "age",
  "income",
  "previous_purchases",
  "campaign_response",
  "customer_tenure_days",
  "channel",
  "avg_basket_size",
  "discount",
  "purchase"

];


const UploadData = () => {

  const [file, setFile] =
    useState(null);

  const [dataset, setDataset] =
    useState(null);

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);


  const handleFileChange = (
    event
  ) => {

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

      setError(
        "Please upload a CSV file."
      );

      return;
    }

    if (
      selectedFile.size === 0
    ) {

      setError(
        "The selected file is empty."
      );

      return;
    }

    setFile(
      selectedFile
    );
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

    Papa.parse(
      file,
      {

        header: true,

        skipEmptyLines: true,

        dynamicTyping: true,

        complete:
          async (result) => {

            try {

              if (
                result.errors.length
                > 0
              ) {

                throw new Error(
                  result.errors[0].message
                );

              }

              const rows =
                result.data;

              if (!rows.length) {

                throw new Error(
                  "CSV contains no data rows."
                );

              }

              const headers =
                result.meta.fields || [];

              const missing =
                REQUIRED_COLUMNS.filter(
                  (column) =>
                    !headers.includes(
                      column
                    )
                );

              if (missing.length) {

                throw new Error(
                  `Missing required columns: ${missing.join(
                    ", "
                  )}`
                );

              }

              const response =
                await uploadDataset(
                  file.name,
                  rows
                );

              const datasetInfo = {

                fileName:
                  file.name,

                rows:
                  response.rows,

                columns:
                  headers.length,

                headers,

                preview:
                  rows.slice(0, 10),

                uploadedAt:
                  new Date().toISOString(),

                positiveITE:
                  response.positive_ite,

                negativeITE:
                  response.negative_ite,

                meanITE:
                  response.mean_ite

              };

              saveDataset(
                datasetInfo
              );

              setDataset(
                datasetInfo
              );

            } catch (err) {

              console.error(
                "Dataset upload error:",
                err
              );

              setError(
                err.message ||
                  "Unable to upload and analyze the dataset."
              );

            } finally {

              setLoading(false);

            }

          },

        error:
          (err) => {

            setError(
              err.message ||
                "Unable to read the CSV file."
            );

            setLoading(false);

          }

      }
    );

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
            data. The backend will store the
            dataset and run fresh causal analysis.
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
              Required columns:
              {" "}
              {REQUIRED_COLUMNS.join(
                ", "
              )}
            </p>

            <span className="file-button">
              Choose CSV File
            </span>

            <input
              type="file"
              accept=".csv,text/csv"
              onChange={
                handleFileChange
              }
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
            disabled={
              !file || loading
            }
          >

            {loading
              ? "Uploading & Running Causal Analysis..."
              : "Upload & Analyze"}

          </button>

        </div>


        {dataset && (

          <div className="dataset-result">

            <div className="success-message">

              ✓ Dataset uploaded and
              causal analysis completed
              successfully.

            </div>


            <div className="dataset-stats">

              <div>

                <span>
                  Rows
                </span>

                <strong>
                  {dataset.rows.toLocaleString()}
                </strong>

              </div>


              <div>

                <span>
                  Columns
                </span>

                <strong>
                  {dataset.columns}
                </strong>

              </div>


              <div>

                <span>
                  Positive ITE
                </span>

                <strong>
                  {dataset.positiveITE.toLocaleString()}
                </strong>

              </div>


              <div>

                <span>
                  Negative ITE
                </span>

                <strong>
                  {dataset.negativeITE.toLocaleString()}
                </strong>

              </div>

            </div>


            <div className="columns-section">

              <h2>
                Columns
              </h2>

              <div className="column-list">

                {dataset.headers.map(
                  (column) => (

                    <span
                      key={column}
                    >
                      {column}
                    </span>

                  )
                )}

              </div>

            </div>


            <div className="preview-section">

              <h2>
                Data Preview
              </h2>

              <div className="table-wrapper">

                <table>

                  <thead>

                    <tr>

                      {dataset.headers.map(
                        (column) => (

                          <th
                            key={column}
                          >
                            {column}
                          </th>

                        )
                      )}

                    </tr>

                  </thead>


                  <tbody>

                    {dataset.preview.map(
                      (
                        row,
                        index
                      ) => (

                        <tr
                          key={index}
                        >

                          {dataset.headers.map(
                            (column) => (

                              <td
                                key={column}
                              >
                                {String(
                                  row[column]
                                  ?? ""
                                )}
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