import {
  useEffect,
  useState
} from "react";

import {
  useNavigate
} from "react-router-dom";

import {
  getBudget,
  getDatasetStatus,
  getInsights,
  getPrescription
} from "../services/api";

import {
  generateInsights
} from "../services/insightsEngine";

import InsightCard from "./InsightCard";

import "./Dashboard.css";


function summarizePrescriptions(
  prescriptions
) {

  const customers =
    prescriptions.length;

  const allocated =
    prescriptions.filter(
      (row) =>
        Number(
          row.optimal_discount
        ) > 0
    ).length;

  const revenue =
    prescriptions.reduce(
      (sum, row) =>
        sum +
        Number(
          row.predicted_revenue
          || 0
        ),
      0
    );

  const cost =
    prescriptions.reduce(
      (sum, row) =>
        sum +
        Number(
          row.marketing_cost
          || 0
        ),
      0
    );

  return {

    customers,

    customers_allocated:
      allocated,

    predicted_revenue:
      revenue,

    marketing_cost:
      cost

  };

}


function Dashboard() {

  const navigate =
    useNavigate();


  const [
    qiniData,
    setQiniData
  ] = useState(null);


  const [
    prescriptionData,
    setPrescriptionData
  ] = useState(null);


  const [
    budgetData,
    setBudgetData
  ] = useState(null);


  const [
    datasetStatus,
    setDatasetStatus
  ] = useState(null);


  const [
    loading,
    setLoading
  ] = useState(true);


  const [
    loadIssues,
    setLoadIssues
  ] = useState([]);


  const loadDashboard =
    async () => {

      setLoading(true);

      const issues = [];


      try {

        const status =
          await getDatasetStatus();

        setDatasetStatus(
          status
        );

      } catch {

        issues.push(
          "Dataset status could not be loaded."
        );

      }


      try {

        const insights =
          await getInsights();

        setQiniData(
          insights
        );

      } catch (error) {

        setQiniData(null);

        if (
          !error.message.includes(
            "No uploaded dataset"
          )
        ) {

          issues.push(
            "Live causal insights could not be loaded."
          );

        }

      }


      try {

        const prescription =
          await getPrescription();

        setPrescriptionData(
          summarizePrescriptions(
            prescription.prescriptions
            || []
          )
        );

      } catch (error) {

        setPrescriptionData(
          null
        );

        if (
          !error.message.includes(
            "Prescription file not found"
          )
        ) {

          issues.push(
            "Prescription results could not be loaded."
          );

        }

      }


      try {

        setBudgetData(
          await getBudget()
        );

      } catch {

        setBudgetData(
          null
        );

        issues.push(
          "Budget settings could not be loaded."
        );

      }


      setLoadIssues(
        issues
      );

      setLoading(false);

    };


  useEffect(() => {

    loadDashboard();

  }, []);


  const insights =
    loading

      ? []

      : generateInsights({

          qiniData,

          prescriptionData,

          budgetData

        });


  const hasAnyResults =
    Boolean(
      qiniData
      ||
      prescriptionData
    );


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
            Upload data, calculate causal effects,
            optimize the budget, and review the
            final customer-level prescription.
          </p>

          <button
            className="secondary-button"
            onClick={
              loadDashboard
            }
          >
            ↻ Refresh Dashboard
          </button>

        </div>


        {datasetStatus?.uploaded && (

          <div className="dashboard-issues">

            <p>

              ✓ Current dataset:{" "}

              <strong>
                {
                  datasetStatus
                    .dataset
                    ?.file_name
                }
              </strong>{" "}

              (
              {Number(
                datasetStatus
                  .dataset
                  ?.rows
                || 0
              ).toLocaleString()}

              {" "}rows)

            </p>

          </div>

        )}


        <div className="insights-section">

          <div className="insights-section-header">

            <h2>
              What the model recommends
            </h2>

            <p>
              These summaries use the latest
              backend causal analysis and
              optimization output.
            </p>

          </div>


          {loading ? (

            <div className="dashboard-loading-card">

              Loading live results...

            </div>

          ) : !hasAnyResults ? (

            <div className="dashboard-empty-card">

              <strong>
                No live results yet
              </strong>

              <p>
                Upload the campaign CSV first.
                The backend will calculate ITE
                and Qini results from it.
              </p>

              <button
                className="secondary-button"
                onClick={() =>
                  navigate("/upload")
                }
              >
                Upload Data →
              </button>

            </div>

          ) : (

            <div className="insight-grid">

              {insights.map(
                (insight) => (

                  <InsightCard
                    key={
                      insight.id
                    }
                    {...insight}
                  />

                )
              )}

            </div>

          )}


          {loadIssues.length > 0 && (

            <div className="dashboard-issues">

              {loadIssues.map(
                (issue) => (

                  <p
                    key={issue}
                  >
                    ⚠ {issue}
                  </p>

                )
              )}

            </div>

          )}

        </div>


        <div className="dashboard-grid">


          <button
            className="dashboard-card"
            onClick={() =>
              navigate("/upload")
            }
          >

            <span className="card-number">
              01
            </span>

            <h2>
              Upload Data
            </h2>

            <p>
              Send a campaign CSV to the backend
              and run fresh causal analysis.
            </p>

            <span className="card-link">
              Open Data Upload →
            </span>

          </button>


          <button
            className="dashboard-card"
            onClick={() =>
              navigate("/budget")
            }
          >

            <span className="card-number">
              02
            </span>

            <h2>
              Budget Settings
            </h2>

            <p>
              Change the budget and immediately
              rerun the SciPy prescription optimizer.
            </p>

            <span className="card-link">
              Configure Budget →
            </span>

          </button>


          <button
            className="dashboard-card"
            onClick={() =>
              navigate("/insights")
            }
          >

            <span className="card-number">
              03
            </span>

            <h2>
              Causal Insights
            </h2>

            <p>
              View Qini and uplift-by-decile
              results calculated from the current upload.
            </p>

            <span className="card-link">
              View Insights →
            </span>

          </button>


          <button
            className="dashboard-card"
            onClick={() =>
              navigate("/prescription")
            }
          >

            <span className="card-number">
              04
            </span>

            <h2>
              Final Prescription
            </h2>

            <p>
              View the latest customer-level
              discount allocation returned by FastAPI.
            </p>

            <span className="card-link">
              View Prescription →
            </span>

          </button>


          <button
            className="dashboard-card"
            onClick={() =>
              navigate("/monitoring")
            }
          >

            <span className="card-number">
              05
            </span>

            <h2>
              Data Monitoring
            </h2>

            <p>
              Check a new customer-data batch
              against the historical drift baseline.
            </p>

            <span className="card-link">
              Open Monitoring →
            </span>

          </button>


        </div>

      </div>

    </section>

  );

}


export default Dashboard;