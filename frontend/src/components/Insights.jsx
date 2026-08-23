import React, { useEffect, useMemo, useState } from "react";
import Plot from "react-plotly.js";
import "./Insights.css";

const Insights = () => {
  const [qiniData, setQiniData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // -----------------------------
  // FILTERS
  // -----------------------------

  const [targetingFilter, setTargetingFilter] = useState("100");

  const [decileFilter, setDecileFilter] = useState("all");

  // -----------------------------
  // LOAD QINI DATA
  // -----------------------------

  useEffect(() => {
    const loadQiniData = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch("./data/qini_curve_data.json");

        if (!response.ok) {
          throw new Error(
            `Unable to load Qini data. HTTP ${response.status}`
          );
        }

        const data = await response.json();

        console.log("Qini data loaded:", data);

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

  // -----------------------------
  // FILTERED ANALYSIS
  // -----------------------------

  const analysis = useMemo(() => {
    if (!qiniData) return null;

    const fractions = qiniData.fractions;
    const qiniValues = qiniData.qini_values;
    const randomBaseline = qiniData.random_baseline;

    // -----------------------------
    // TARGETING FILTER
    // -----------------------------

    const maxTargeting = Number(targetingFilter) / 100;

    const filteredIndexes = fractions
      .map((fraction, index) => ({
        fraction,
        index,
      }))
      .filter(
        ({ fraction }) =>
          fraction <= maxTargeting
      );

    const filteredFractions = filteredIndexes.map(
      ({ fraction }) => fraction
    );

    const filteredQiniValues = filteredIndexes.map(
      ({ index }) => qiniValues[index]
    );

    const filteredRandomBaseline =
      filteredIndexes.map(
        ({ index }) => randomBaseline[index]
      );

    // -----------------------------
    // MAXIMUM QINI
    // -----------------------------

    const maxQini = Math.max(
      ...filteredQiniValues
    );

    const maxQiniIndex =
      filteredQiniValues.indexOf(maxQini);

    const bestTargeting =
      filteredFractions[maxQiniIndex] * 100;

    const randomAtBest =
      filteredRandomBaseline[maxQiniIndex];

    const improvement =
      randomAtBest !== 0
        ? ((maxQini - randomAtBest) /
            Math.abs(randomAtBest)) *
          100
        : 0;

    // -----------------------------
    // UPLIFT DATA
    // -----------------------------

    const upliftByDecile =
      qiniData.uplift_by_decile || {};

    let decileEntries =
      Object.entries(upliftByDecile);

    // Apply decile filter
    if (decileFilter !== "all") {
      decileEntries =
        decileEntries.filter(
          ([decile]) =>
            Number(decile) + 1 ===
            Number(decileFilter)
        );
    }

    // -----------------------------
    // BEST DECILE
    // -----------------------------

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
      fractions: filteredFractions,
      qiniValues: filteredQiniValues,
      randomBaseline: filteredRandomBaseline,

      upliftEntries: decileEntries,

      maxQini,
      bestTargeting,
      randomAtBest,
      improvement,
      bestDecile,
    };
  }, [
    qiniData,
    targetingFilter,
    decileFilter,
  ]);

  // -----------------------------
  // LOADING STATE
  // -----------------------------

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

  // -----------------------------
  // ERROR STATE
  // -----------------------------

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

              <strong>
                Expected JSON structure:
              </strong>

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

  // -----------------------------
  // SAFETY CHECK
  // -----------------------------

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
            FILTERS
        ========================================== */}

        <section className="insights-filter-card">

          <div className="filter-heading">

            <div>

              <span className="chart-label">
                ANALYSIS FILTERS
              </span>

              <h2>
                Filter Causal Results
              </h2>

              <p>
                Adjust the targeting range and
                customer uplift segment.
              </p>

            </div>

            <button
              className="reset-filter-button"
              onClick={() => {
                setTargetingFilter("100");
                setDecileFilter("all");
              }}
            >
              Reset Filters
            </button>

          </div>


          <div className="filter-grid">

            {/* Targeting Filter */}

            <div className="filter-group">

              <label htmlFor="targeting-filter">
                Maximum Targeting Range
              </label>

              <select
                id="targeting-filter"
                value={targetingFilter}
                onChange={(e) =>
                  setTargetingFilter(e.target.value)
                }
              >

                <option value="100">
                  All Customers
                </option>

                <option value="10">
                  Top 10%
                </option>

                <option value="20">
                  Top 20%
                </option>

                <option value="30">
                  Top 30%
                </option>

                <option value="40">
                  Top 40%
                </option>

                <option value="50">
                  Top 50%
                </option>

                <option value="60">
                  Top 60%
                </option>

                <option value="70">
                  Top 70%
                </option>

                <option value="80">
                  Top 80%
                </option>

                <option value="90">
                  Top 90%
                </option>

              </select>

            </div>


            {/* Decile Filter */}

            <div className="filter-group">

              <label htmlFor="decile-filter">
                Customer Uplift Segment
              </label>

              <select
                id="decile-filter"
                value={decileFilter}
                onChange={(e) =>
                  setDecileFilter(e.target.value)
                }
              >

                <option value="all">
                  All Deciles
                </option>

                {Array.from(
                  { length: 10 },
                  (_, index) => (
                    <option
                      key={index + 1}
                      value={index + 1}
                    >
                      Decile {index + 1}
                    </option>
                  )
                )}

              </select>

            </div>

          </div>

        </section>


        {/* =========================================
            SUMMARY CARDS
        ========================================== */}

        <div className="insight-grid">

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


          <div className="insight-card">

            <span className="card-label">
              Highest Uplift Segment
            </span>

            <strong>

              {analysis.bestDecile
                ? `D${Number(
                    analysis.bestDecile[0]
                  ) + 1}`
                : "N/A"}

            </strong>

            <small>

              {analysis.bestDecile
                ? `${(
                    Number(
                      analysis.bestDecile[1]
                    ) * 100
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

                x: analysis.upliftEntries.map(
                  ([decile]) =>
                    `D${Number(decile) + 1}`
                ),

                y: analysis.upliftEntries.map(
                  ([, value]) =>
                    Number(value) * 100
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

              The highest Qini value in the selected
              range occurs when approximately{" "}

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