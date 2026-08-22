import React, { useEffect, useMemo, useState } from "react";
import Plot from "react-plotly.js";
import "./Insights.css";

const Insights = () => {
  const [qiniData, setQiniData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadQiniData = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch("/qini_curve_data.json");

        if (!response.ok) {
          throw new Error(
            `Unable to load Qini data. HTTP ${response.status}`
          );
        }

        const data = await response.json();

        console.log("Qini data loaded:", data);

        /*
         * Your actual JSON structure:
         *
         * fractions
         * qini_values
         * random_baseline
         * uplift_by_decile
         */

        if (
          !Array.isArray(data.fractions) ||
          !Array.isArray(data.qini_values) ||
          !Array.isArray(data.random_baseline)
        ) {
          throw new Error(
            "Invalid Qini data format. Required fields: fractions, qini_values, random_baseline."
          );
        }

        if (
          data.fractions.length !== data.qini_values.length ||
          data.fractions.length !== data.random_baseline.length
        ) {
          throw new Error(
            "Qini data arrays have different lengths."
          );
        }

        setQiniData(data);
      } catch (err) {
        console.error("Qini loading error:", err);

        setError(
          err.message ||
            "Unable to load causal analysis results."
        );
      } finally {
        setLoading(false);
      }
    };

    loadQiniData();
  }, []);

  /*
   * Calculate useful business metrics
   */
  const analysis = useMemo(() => {
    if (!qiniData) return null;

    const fractions = qiniData.fractions;
    const qiniValues = qiniData.qini_values;
    const randomBaseline = qiniData.random_baseline;

    /*
     * Maximum Qini value
     */
    const maxQini = Math.max(...qiniValues);

    /*
     * Index where Qini is maximum
     */
    const maxQiniIndex = qiniValues.indexOf(maxQini);

    /*
     * Best targeting percentage
     */
    const bestTargeting =
      fractions[maxQiniIndex] * 100;

    /*
     * Random baseline at best targeting point
     */
    const randomAtBest =
      randomBaseline[maxQiniIndex];

    /*
     * Improvement over random baseline
     */
    const improvement =
      randomAtBest !== 0
        ? ((maxQini - randomAtBest) /
            Math.abs(randomAtBest)) *
          100
        : 0;

    /*
     * Uplift by decile
     */
    const upliftByDecile =
      qiniData.uplift_by_decile || {};

    /*
     * Find highest uplift decile
     */
    const decileEntries = Object.entries(
      upliftByDecile
    );

    let bestDecile = null;

    if (decileEntries.length > 0) {
      bestDecile = decileEntries.reduce(
        (best, current) =>
          Number(current[1]) >
          Number(best[1])
            ? current
            : best
      );
    }

    return {
      fractions,
      qiniValues,
      randomBaseline,
      upliftByDecile,
      maxQini,
      bestTargeting,
      randomAtBest,
      improvement,
      bestDecile,
    };
  }, [qiniData]);

  /*
   * Loading state
   */
  if (loading) {
    return (
      <div className="insights-page">
        <div className="insights-container">

          <div className="page-header">
            <div>
              <span className="page-label">
                CAUSAL ANALYSIS
              </span>

              <h1>Causal Insights</h1>

              <p>
                Double Machine Learning based
                treatment-effect analysis.
              </p>
            </div>
          </div>

          <div className="loading-card">
            Loading causal analysis results...
          </div>

        </div>
      </div>
    );
  }

  /*
   * Error state
   */
  if (error) {
    return (
      <div className="insights-page">
        <div className="insights-container">

          <div className="page-header">
            <div>
              <span className="page-label">
                CAUSAL ANALYSIS
              </span>

              <h1>Causal Insights</h1>

              <p>
                Double Machine Learning based
                treatment-effect analysis.
              </p>
            </div>
          </div>

          <div className="error-card">

            <div className="error-icon">
              !
            </div>

            <h3>
              Unable to load results
            </h3>

            <p>
              {error}
            </p>

            <div className="error-help">
              <strong>Expected JSON structure:</strong>

              <pre>
{`{
  "fractions": [...],
  "qini_values": [...],
  "random_baseline": [...],
  "uplift_by_decile": {...}
}`}
              </pre>

              <p>
                Your file should be located at:
              </p>

              <code>
                frontend/public/qini_curve_data.json
              </code>
            </div>

          </div>

        </div>
      </div>
    );
  }

  /*
   * Safety check
   */
  if (!analysis) {
    return null;
  }

  return (
    <div className="insights-page">

      <div className="insights-container">

        {/* =========================================
            HEADER
        ========================================== */}

        <div className="page-header">

          <div>
            <span className="page-label">
              CAUSAL ANALYSIS
            </span>

            <h1>
              Causal Insights
            </h1>

            <p>
              Double Machine Learning based
              treatment-effect and uplift analysis.
            </p>
          </div>

          <div className="status-badge">
            <span>●</span>
            Model Results Loaded
          </div>

        </div>


        {/* =========================================
            SUMMARY CARDS
        ========================================== */}

        <div className="insight-grid">

          {/* Maximum Qini */}

          <div className="insight-card">

            <span className="card-label">
              Maximum Qini
            </span>

            <strong>
              {analysis.maxQini.toFixed(2)}
            </strong>

            <small>
              Highest cumulative causal uplift
            </small>

          </div>


          {/* Best Targeting */}

          <div className="insight-card">

            <span className="card-label">
              Best Targeting Point
            </span>

            <strong>
              {analysis.bestTargeting.toFixed(1)}%
            </strong>

            <small>
              Customers targeted at maximum Qini
            </small>

          </div>


          {/* Data Points */}

          <div className="insight-card">

            <span className="card-label">
              Qini Data Points
            </span>

            <strong>
              {analysis.fractions.length}
            </strong>

            <small>
              Model evaluation points
            </small>

          </div>


          {/* Random Comparison */}

          <div className="insight-card">

            <span className="card-label">
              Random Baseline
            </span>

            <strong>
              {analysis.randomAtBest.toFixed(2)}
            </strong>

            <small>
              At the best targeting point
            </small>

          </div>


          {/* Improvement */}

          <div className="insight-card">

            <span className="card-label">
              Model Advantage
            </span>

            <strong>
              {analysis.improvement.toFixed(1)}%
            </strong>

            <small>
              Improvement over random baseline
            </small>

          </div>


          {/* Best Decile */}

          <div className="insight-card">

            <span className="card-label">
              Highest Uplift Segment
            </span>

            <strong>
              {analysis.bestDecile
                ? `D${Number(analysis.bestDecile[0]) + 1}`
                : "N/A"}
            </strong>

            <small>
              {analysis.bestDecile
                ? `${(
                    Number(analysis.bestDecile[1]) *
                    100
                  ).toFixed(2)}% uplift`
                : "No decile data"}
            </small>

          </div>

        </div>


        {/* =========================================
            QINI CURVE
        ========================================== */}

        <section className="chart-card">

          <div className="chart-header">

            <div>
              <span className="chart-label">
                MODEL PERFORMANCE
              </span>

              <h2>
                Qini Curve
              </h2>

              <p>
                Compares the causal model against
                random customer targeting.
              </p>
            </div>

          </div>


          <Plot
            data={[
              {
                x: analysis.fractions.map(
                  (value) => value * 100
                ),

                y: analysis.qiniValues,

                type: "scatter",

                mode: "lines+markers",

                name: "Causal Model",

                line: {
                  width: 3,
                },

                marker: {
                  size: 5,
                },
              },

              {
                x: analysis.fractions.map(
                  (value) => value * 100
                ),

                y: analysis.randomBaseline,

                type: "scatter",

                mode: "lines",

                name: "Random Targeting",

                line: {
                  dash: "dash",
                  width: 2,
                },
              },
            ]}

            layout={{
              autosize: true,

              xaxis: {
                title:
                  "Customers Targeted (%)",

                ticksuffix: "%",
              },

              yaxis: {
                title:
                  "Cumulative Qini Value",
              },

              hovermode: "x unified",

              legend: {
                orientation: "h",
                y: 1.1,
              },

              margin: {
                l: 70,
                r: 30,
                t: 40,
                b: 70,
              },

              paper_bgcolor: "transparent",

              plot_bgcolor: "transparent",

              font: {
                family:
                  "Inter, Arial, sans-serif",
              },
            }}

            useResizeHandler

            style={{
              width: "100%",
              height: "450px",
            }}

            config={{
              responsive: true,
              displaylogo: false,
            }}
          />

        </section>


        {/* =========================================
            UPLIFT BY DECILE
        ========================================== */}

        <section className="chart-card">

          <div className="chart-header">

            <div>
              <span className="chart-label">
                CUSTOMER SEGMENTATION
              </span>

              <h2>
                Uplift by Decile
              </h2>

              <p>
                Estimated treatment uplift for each
                customer segment ranked by causal effect.
              </p>
            </div>

          </div>


          <Plot
            data={[
              {
                x: Object.keys(
                  analysis.upliftByDecile
                ).map(
                  (decile) =>
                    `D${Number(decile) + 1}`
                ),

                y: Object.values(
                  analysis.upliftByDecile
                ).map(
                  (value) =>
                    value * 100
                ),

                type: "bar",

                name: "Customer Uplift",

                hovertemplate:
                  "Segment %{x}<br>" +
                  "Uplift: %{y:.2f}%<extra></extra>",
              },
            ]}

            layout={{
              autosize: true,

              xaxis: {
                title:
                  "Customer Decile",
              },

              yaxis: {
                title:
                  "Estimated Uplift (%)",

                ticksuffix: "%",
              },

              margin: {
                l: 70,
                r: 30,
                t: 30,
                b: 70,
              },

              paper_bgcolor: "transparent",

              plot_bgcolor: "transparent",

              font: {
                family:
                  "Inter, Arial, sans-serif",
              },
            }}

            useResizeHandler

            style={{
              width: "100%",
              height: "420px",
            }}

            config={{
              responsive: true,
              displaylogo: false,
            }}
          />

        </section>


        {/* =========================================
            BUSINESS INTERPRETATION
        ========================================== */}

        <section className="interpretation-card">

          <div className="interpretation-header">

            <span>
              BUSINESS INTERPRETATION
            </span>

            <h2>
              What does this mean?
            </h2>

          </div>


          <p>
            The Double Machine Learning model
            estimates the causal effect of the
            campaign treatment on customer outcomes
            while accounting for observed customer
            characteristics.
          </p>


          <p>
            The Qini curve measures how effectively
            the model ranks customers according to
            their expected incremental treatment
            benefit.
          </p>


          <div className="recommendation-box">

            <strong>
              Targeting Recommendation
            </strong>

            <p>
              The highest Qini value in the supplied
              results occurs when approximately{" "}

              <strong>
                {analysis.bestTargeting.toFixed(1)}%
              </strong>{" "}

              of customers are targeted.
            </p>

          </div>


          <div className="recommendation-box">

            <strong>
              Highest-Uplift Segment
            </strong>

            <p>
              The strongest customer segment is{" "}

              <strong>
                {analysis.bestDecile
                  ? `Decile ${
                      Number(
                        analysis.bestDecile[0]
                      ) + 1
                    }`
                  : "not available"}
              </strong>

              {analysis.bestDecile &&
                `, with an estimated uplift of ${(
                  Number(
                    analysis.bestDecile[1]
                  ) * 100
                ).toFixed(2)}%.`}
            </p>

          </div>


          <div className="warning-box">

            <strong>
              Important
            </strong>

            <p>
              A positive estimated uplift means
              the treatment is predicted to provide
              additional benefit for that customer
              segment. Negative uplift suggests that
              targeting that segment may be less
              beneficial.
            </p>

          </div>

        </section>

      </div>

    </div>
  );
};

export default Insights;