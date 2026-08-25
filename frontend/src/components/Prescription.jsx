import React, { useEffect, useMemo, useState } from "react";
import "./Prescription.css";

const Prescription = () => {
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/data/optimized_discount_assignments.csv")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load optimization results.");
        }

        return response.text();
      })
      .then((csvText) => {
        const rows = csvText
          .trim()
          .split("\n")
          .map((row) => row.split(","));

        if (rows.length < 2) {
          throw new Error("Optimization file is empty.");
        }

        const headers = rows[0].map((header) =>
          header.trim().toLowerCase()
        );

        const data = rows.slice(1).map((row) => {
          const record = {};

          headers.forEach((header, index) => {
            record[header] = row[index]?.trim() || "";
          });

          return record;
        });

        setAllocations(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const getValue = (row, possibleNames) => {
    for (const name of possibleNames) {
      if (row[name] !== undefined && row[name] !== "") {
        return row[name];
      }
    }

    return 0;
  };

  const totalRevenue = useMemo(() => {
    return allocations.reduce((total, row) => {
      return (
        total +
        Number(
          getValue(row, [
            "predicted_revenue",
            "revenue",
          ])
        )
      );
    }, 0);
  }, [allocations]);

  const totalCost = useMemo(() => {
    return allocations.reduce((total, row) => {
      return (
        total +
        Number(
          getValue(row, [
            "marketing_cost",
            "cost",
            "discount_cost",
          ])
        )
      );
    }, 0);
  }, [allocations]);

  const customersWithDiscount = useMemo(() => {
    return allocations.filter((row) => {
      const discount = Number(
        getValue(row, [
          "optimal_discount",
          "discount",
        ])
      );

      return discount > 0;
    }).length;
  }, [allocations]);

  if (loading) {
    return (
      <div className="prescription-page">
        <div className="prescription-container">
          <div className="loading-card">
            Loading optimization results...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="prescription-page">
        <div className="prescription-container">
          <div className="error-card">
            <h2>Unable to load prescription</h2>
            <p>{error}</p>

            <p>
              Make sure the optimization output is available at:
            </p>

            <code>
              frontend/public/data/optimized_discount_assignments.csv
            </code>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="prescription-page">
      <div className="prescription-container">

        {/* Header */}

        <div className="prescription-header">
          <div>
            <span className="page-label">
              PRESCRIPTIVE OPTIMIZATION
            </span>

            <h1>Optimal Discount Prescription</h1>

            <p>
              Customer-level discount allocation generated
              by the optimization model.
            </p>
          </div>
        </div>

        {/* Summary Cards */}

        <div className="prescription-summary">

          <div className="summary-card">
            <span>Total Customers</span>

            <strong>
              {allocations.length.toLocaleString()}
            </strong>
          </div>

          <div className="summary-card">
            <span>Customers with Discount</span>

            <strong>
              {customersWithDiscount.toLocaleString()}
            </strong>
          </div>

          <div className="summary-card">
            <span>Total Predicted Revenue</span>

            <strong>
              ₹{totalRevenue.toFixed(2)}
            </strong>
          </div>

          <div className="summary-card">
            <span>Total Marketing Cost</span>

            <strong>
              ₹{totalCost.toFixed(2)}
            </strong>
          </div>

        </div>

        {/* Allocation Matrix */}

        <div className="matrix-card">

          <div className="matrix-header">
            <div>
              <h2>Allocation Matrix</h2>

              <p>
                Mathematically optimal discount assigned
                to each customer.
              </p>
            </div>

            <span className="result-badge">
              Optimization Complete
            </span>
          </div>

          <div className="table-wrapper">

            <table className="prescription-table">

              <thead>
                <tr>
                  <th>#</th>
                  <th>Customer ID</th>
                  <th>Optimal Discount</th>
                  <th>Predicted Revenue</th>
                  <th>Marketing Cost</th>
                </tr>
              </thead>

              <tbody>

                {allocations.map((row, index) => {

                  const customerId = getValue(
                    row,
                    ["customer_id", "customerid", "id"]
                  );

                  const discount = getValue(
                    row,
                    [
                      "optimal_discount",
                      "discount",
                    ]
                  );

                  const revenue = getValue(
                    row,
                    [
                      "predicted_revenue",
                      "revenue",
                    ]
                  );

                  const cost = getValue(
                    row,
                    [
                      "marketing_cost",
                      "cost",
                      "discount_cost",
                    ]
                  );

                  return (
                    <tr key={index}>

                      <td>
                        {index + 1}
                      </td>

                      <td className="customer-id">
                        {customerId}
                      </td>

                      <td>
                        <span className="discount-badge">
                          {Number(discount).toFixed(0)}%
                        </span>
                      </td>

                      <td>
                        ₹{Number(revenue).toFixed(2)}
                      </td>

                      <td>
                        ₹{Number(cost).toFixed(2)}
                      </td>

                    </tr>
                  );
                })}

              </tbody>

            </table>

          </div>

        </div>

      </div>
    </div>
  );
};

export default Prescription;