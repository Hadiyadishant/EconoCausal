import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getBudget } from "../services/storage";
import { getPrescription } from "../services/api";
import { generateInsights } from "../services/insightsEngine";
import InsightCard from "./InsightCard";
import "./Dashboard.css";

// Turns the raw list of per-customer prescriptions returned by
// GET /prescription into the small set of aggregate numbers the
// insight engine and the stats strip need.
function summarizePrescriptions(prescriptions) {
  const customers = prescriptions.length;

  const allocated = prescriptions.filter(
    (row) => Number(row.optimal_discount) > 0
  ).length;

  const revenue = prescriptions.reduce(
    (sum, row) => sum + Number(row.predicted_revenue || 0),
    0
  );

  const cost = prescriptions.reduce(
    (sum, row) => sum + Number(row.marketing_cost || 0),
    0
  );

  return {
    customers,
    customers_allocated: allocated,
    predicted_revenue: revenue,
    marketing_cost: cost,
  };
}

function Dashboard() {
  const navigate = useNavigate();

  const [qiniData, setQiniData] = useState(null);
  const [prescriptionData, setPrescriptionData] = useState(null);
  const [budgetData, setBudgetData] = useState(null);

  const [loading, setLoading] = useState(true);
  const [loadIssues, setLoadIssues] = useState([]);

  // --------------------------------------------------
  // Connect to real ML outputs (Day 3)
  // Qini/uplift results still come from the static file
  // frontend/public/data/qini_curve_data.json (same source
  // Insights.jsx reads). Prescription results now come from
  // the live FastAPI backend via services/api.js.
  // --------------------------------------------------
  useEffect(() => {
    let cancelled = false;

    const loadAll = async () => {
      const issues = [];

      // Qini / uplift results
      let qini = null;
      try {
        const res = await fetch("./data/qini_curve_data.json");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        qini = await res.json();
      } catch (err) {
        issues.push("Causal analysis results (Qini curve) could not be loaded.");
      }

      // Prescriptive optimization results — live from the API
      let prescription = null;
      try {
        const result = await getPrescription();
        if (!result.prescriptions || !Array.isArray(result.prescriptions)) {
          throw new Error("Invalid prescription response");
        }
        prescription = summarizePrescriptions(result.prescriptions);
      } catch (err) {
        issues.push(
          err.message?.includes("Unable to reach")
            ? "Prescription results could not be loaded — make sure the FastAPI server is running."
            : "Prescription (discount allocation) results could not be loaded."
        );
      }

      // Budget settings (local, always safe to read)
      let budget = null;
      try {
        budget = getBudget();
      } catch (err) {
        budget = null;
      }

      if (!cancelled) {
        setQiniData(qini);
        setPrescriptionData(prescription);
        setBudgetData(budget);
        setLoadIssues(issues);
        setLoading(false);
      }
    };

    loadAll();

    return () => {
      cancelled = true;
    };
  }, []);

  // --------------------------------------------------
  // Interpret (Day 4) — natural-language insights
  // --------------------------------------------------
  const insights = loading
    ? []
    : generateInsights({ qiniData, prescriptionData, budgetData });

  const hasAnyResults = Boolean(qiniData || prescriptionData);

  const budgetRemaining =
    budgetData && prescriptionData
      ? Number(budgetData.totalBudget) - Number(prescriptionData.marketing_cost)
      : null;

  return (
    <section className="dashboard-page">
      <div className="dashboard-container">

        <div className="dashboard-header">
          <span className="dashboard-eyebrow">
            ECONOCAUSAL
          </span>

          <h1>
            Causal Campaign Dashboard
          </h1>

          <p>
            Manage campaign data, causal insights,
            and budget constraints from one place.
          </p>
        </div>

        {/* =========================================
            NATURAL-LANGUAGE INSIGHTS (Day 4 & 5)
        ========================================== */}

        <div className="insights-section">

          <div className="insights-section-header">
            <h2>What the model recommends</h2>
            <p>
              Plain-language takeaways from your latest causal
              analysis and prescriptive optimization results.
            </p>
          </div>

          {loading ? (
            <div className="dashboard-loading-card">
              Loading your latest results...
            </div>
          ) : (
            <>
              {!hasAnyResults && (
                <div className="dashboard-empty-card">
                  <strong>No results yet</strong>
                  <p>
                    Upload campaign data and run the causal analysis
                    and prescription steps to see recommendations here.
                  </p>
                  <button
                    className="secondary-button"
                    onClick={() => navigate("/upload")}
                  >
                    Upload Data →
                  </button>
                </div>
              )}

              <div className="insight-grid">
                {insights.map((insight) => (
                  <InsightCard key={insight.id} {...insight} />
                ))}
              </div>

              {loadIssues.length > 0 && (
                <div className="dashboard-issues">
                  {loadIssues.map((issue) => (
                    <p key={issue}>⚠ {issue}</p>
                  ))}
                </div>
              )}
            </>
          )}

        </div>

        {/* =========================================
            NAVIGATION CARDS (existing, polished)
        ========================================== */}

        <div className="dashboard-grid">

          <button
            className="dashboard-card"
            onClick={() => navigate("/upload")}
          >
            <span className="card-number">01</span>

            <h2>
              Upload Data
            </h2>

            <p>
              Load historical campaign data for
              the causal analysis pipeline.
            </p>

            <span className="card-link">
              Open Data Upload →
            </span>
          </button>


          <button
            className="dashboard-card"
            onClick={() => navigate("/budget")}
          >
            <span className="card-number">02</span>

            <h2>
              Budget Settings
            </h2>

            <p>
              Configure campaign budget and
              maximum targeting constraints.
            </p>

            <span className="card-link">
              Configure Budget →
            </span>
          </button>


          <button
            className="dashboard-card"
            onClick={() => navigate("/insights")}
          >
            <span className="card-number">03</span>

            <h2>
              Causal Insights
            </h2>

            <p>
              View Qini curves and uplift analysis
              from the Double Machine Learning model.
            </p>

            <span className="card-link">
              View Insights →
            </span>
          </button>

          <button
            className="dashboard-card"
            onClick={() => navigate("/prescription")}
          >
            <span className="card-number">
              04
            </span>

            <h2>
              Final Prescription
            </h2>

            <p>
              View the mathematically optimal discount
              assigned to each customer, live from the API.
            </p>

            <span className="card-link">
              View Prescription →
            </span>
          </button>

          <button
            className="dashboard-card"
            onClick={() => navigate("/monitoring")}
          >
            <span className="card-number">
              05
            </span>

            <h2>
              Data Monitoring
            </h2>

            <p>
              Check new customer data for drift
              against the historical baseline.
            </p>

            <span className="card-link">
              Check for Drift →
            </span>
          </button>

        </div>

        {/* =========================================
            LIVE MODEL SNAPSHOT (Day 3 — real values,
            falls back to static labels if unavailable)
        ========================================== */}

        <div className="dashboard-info">

          <div>
            <span>MODEL</span>
            <strong>Double Machine Learning</strong>
          </div>

          <div>
            <span>CUSTOMERS ALLOCATED</span>
            <strong>
              {prescriptionData
                ? Number(prescriptionData.customers_allocated).toLocaleString()
                : "—"}
            </strong>
          </div>

          <div>
            <span>PREDICTED REVENUE</span>
            <strong>
              {prescriptionData
                ? `₹${Number(prescriptionData.predicted_revenue).toLocaleString(
                    "en-IN",
                    { maximumFractionDigits: 0 }
                  )}`
                : "—"}
            </strong>
          </div>

          <div>
            <span>BUDGET REMAINING</span>
            <strong>
              {budgetRemaining !== null
                ? `₹${budgetRemaining.toLocaleString("en-IN", {
                    maximumFractionDigits: 0,
                  })}`
                : "—"}
            </strong>
          </div>

        </div>

      </div>
    </section>
  );
}

export default Dashboard;
