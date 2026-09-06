import { useEffect, useMemo, useState } from "react";
import { getPrescription } from "../services/api";
import "./Prescription.css";

function Prescription() {
  const [data, setData] = useState([]);
  const [search, setSearch] = useState("");
  const [discountFilter, setDiscountFilter] = useState("all");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadPrescription();
  }, []);

  async function loadPrescription() {
    try {
      setLoading(true);
      setError("");

      const result = await getPrescription();

      if (!result.prescriptions) {
        throw new Error("Prescription data is missing from API response.");
      }

      setData(result.prescriptions);
    } catch (err) {
      console.error("Prescription loading error:", err);

      setError(
        err.message || "Unable to connect to the EconoCausal API."
      );
    } finally {
      setLoading(false);
    }
  }

  /* -----------------------------
     FILTER DATA
  ----------------------------- */

  const filteredData = useMemo(() => {
    return data.filter((customer) => {
      const customerId = String(customer.customer_id);

      const matchesSearch = customerId.includes(search.trim());

      const discount = Number(customer.optimal_discount);

      let matchesDiscount = true;

      if (discountFilter === "discounted") {
        matchesDiscount = discount > 0;
      }

      if (discountFilter === "no-discount") {
        matchesDiscount = discount === 0;
      }

      return matchesSearch && matchesDiscount;
    });
  }, [data, search, discountFilter]);

  /* -----------------------------
     SUMMARY
  ----------------------------- */

  const summary = useMemo(() => {
    const customers = data.length;

    const allocated = data.filter(
      (customer) => Number(customer.optimal_discount) > 0
    ).length;

    const revenue = data.reduce(
      (total, customer) => total + Number(customer.predicted_revenue || 0),
      0
    );

    const cost = data.reduce(
      (total, customer) => total + Number(customer.marketing_cost || 0),
      0
    );

    const averageDiscount =
      customers > 0
        ? data.reduce(
            (total, customer) => total + Number(customer.optimal_discount || 0),
            0
          ) / customers
        : 0;

    const allocationRate = customers > 0 ? (allocated / customers) * 100 : 0;

    return {
      customers,
      allocated,
      revenue,
      cost,
      averageDiscount,
      allocationRate,
    };
  }, [data]);

  /* -----------------------------
     FORMAT CURRENCY
  ----------------------------- */

  function formatCurrency(value) {
    return `₹${Number(value).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  }

  /* -----------------------------
     LOADING
  ----------------------------- */

  if (loading) {
    return (
      <div className="prescription-page">
        <div className="prescription-loading">
          <div className="loading-spinner"></div>
          <h2>Loading optimized prescription...</h2>
          <p>Fetching the final discount allocation from the EconoCausal API.</p>
        </div>
      </div>
    );
  }

  /* -----------------------------
     ERROR
  ----------------------------- */

  if (error) {
    return (
      <div className="prescription-page">
        <div className="prescription-error">
          <div className="error-icon">⚠️</div>
          <h2>Unable to load prescription</h2>
          <p>{error}</p>
          <button onClick={loadPrescription}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="prescription-page">
      {/* HEADER */}
      <div className="prescription-header">
        <div>
          <span className="prescription-eyebrow">
            PRESCRIPTIVE OPTIMIZATION
          </span>
          <h1>Customer Discount Prescription</h1>
          <p>
            Personalized discount recommendations generated under the
            available marketing budget.
          </p>
        </div>

        <div className="live-badge">
          <span></span>
          Live API Data
        </div>
      </div>

      {/* BUSINESS RECOMMENDATION */}
      <div className="strategy-card">
        <div className="strategy-label">RECOMMENDED STRATEGY</div>
        <h2>Target customers selectively using optimized discount levels.</h2>
        <p>
          The optimization engine evaluated{" "}
          <strong>{summary.customers.toLocaleString()}</strong> customers and
          selected discounts for{" "}
          <strong>{summary.allocated.toLocaleString()}</strong> customers
          while respecting the marketing budget.
        </p>
      </div>

      {/* SUMMARY CARDS */}
      <div className="prescription-summary">
        <div className="prescription-card">
          <span>Customers</span>
          <strong>{summary.customers.toLocaleString()}</strong>
          <small>Customers evaluated</small>
        </div>

        <div className="prescription-card">
          <span>Customers Targeted</span>
          <strong>{summary.allocated.toLocaleString()}</strong>
          <small>{summary.allocationRate.toFixed(2)}% of customers</small>
        </div>

        <div className="prescription-card">
          <span>Predicted Revenue</span>
          <strong>{formatCurrency(summary.revenue)}</strong>
          <small>Optimization output</small>
        </div>

        <div className="prescription-card">
          <span>Marketing Cost</span>
          <strong>{formatCurrency(summary.cost)}</strong>
          <small>Optimized spend</small>
        </div>
      </div>

      {/* NATURAL LANGUAGE SUMMARY */}
      <div className="business-summary">
        <div className="business-summary-header">
          <span>BUSINESS INTERPRETATION</span>
          <h2>What does the optimizer recommend?</h2>
        </div>

        <div className="business-summary-grid">
          <div className="business-summary-item">
            <div className="summary-icon">🎯</div>
            <div>
              <h3>Selective targeting</h3>
              <p>
                Discounts are recommended for{" "}
                <strong>{summary.allocationRate.toFixed(2)}%</strong> of the
                evaluated customer base instead of automatically discounting
                everyone.
              </p>
            </div>
          </div>

          <div className="business-summary-item">
            <div className="summary-icon">💰</div>
            <div>
              <h3>Budget-aware allocation</h3>
              <p>
                The optimizer determines discount assignments while enforcing
                the available marketing budget constraint.
              </p>
            </div>
          </div>

          <div className="business-summary-item">
            <div className="summary-icon">📊</div>
            <div>
              <h3>Personalized discounts</h3>
              <p>
                Customers do not automatically receive the same discount. The
                prescription assigns the optimized discount level customer by
                customer.
              </p>
            </div>
          </div>

          <div className="business-summary-item">
            <div className="summary-icon">🧠</div>
            <div>
              <h3>Causal + prescriptive decision</h3>
              <p>
                Causal treatment-effect estimates are used upstream of the
                optimization process to support targeted marketing decisions.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* FILTER BAR */}
      <div className="prescription-controls">
        <div className="search-box">
          <span>🔎</span>
          <input
            type="text"
            placeholder="Search customer ID..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <select
          value={discountFilter}
          onChange={(event) => setDiscountFilter(event.target.value)}
        >
          <option value="all">All Customers</option>
          <option value="discounted">Discounted Customers</option>
          <option value="no-discount">No Discount</option>
        </select>

        <button className="refresh-button" onClick={loadPrescription}>
          ↻ Refresh
        </button>
      </div>

      {/* TABLE */}
      <div className="prescription-table-card">
        <div className="table-header">
          <div>
            <span>ALLOCATION MATRIX</span>
            <h2>Customer-level prescription</h2>
          </div>

          <div className="result-count">
            Showing <strong>{filteredData.length.toLocaleString()}</strong>{" "}
            customers
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Optimal Discount</th>
                <th>Discount Fraction</th>
                <th>Predicted Revenue</th>
                <th>Marketing Cost</th>
              </tr>
            </thead>

            <tbody>
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan="5" className="empty-table">
                    No customers match your filter.
                  </td>
                </tr>
              ) : (
                filteredData.map((customer, index) => (
                  <tr key={customer.customer_id ?? index}>
                    <td>
                      <strong>{customer.customer_id}</strong>
                    </td>

                    <td>
                      <span
                        className={
                          Number(customer.optimal_discount) > 0
                            ? "discount-badge"
                            : "no-discount-badge"
                        }
                      >
                        {Number(customer.optimal_discount)}%
                      </span>
                    </td>

                    <td>
                      {Number(customer.discount_fraction || 0).toFixed(2)}
                    </td>

                    <td>{formatCurrency(customer.predicted_revenue)}</td>

                    <td>{formatCurrency(customer.marketing_cost)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* FOOTER NOTE */}
      <div className="prescription-footer">
        <span>✓</span>
        <p>
          Prescription generated by the EconoCausal prescriptive optimization
          engine. Each customer receives exactly one allowed discount level
          subject to the marketing budget constraint.
        </p>
      </div>
    </div>
  );
}

export default Prescription;
