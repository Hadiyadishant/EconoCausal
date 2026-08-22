import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

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

        </div>

        <div className="dashboard-info">

          <div>
            <span>MODEL</span>
            <strong>Double Machine Learning</strong>
          </div>

          <div>
            <span>ANALYSIS</span>
            <strong>Causal Treatment Effects</strong>
          </div>

          <div>
            <span>OPTIMIZATION</span>
            <strong>Budget Allocation</strong>
          </div>

        </div>

      </div>
    </section>
  );
}

export default Dashboard;