import React, {
  useEffect,
  useMemo,
  useState
} from "react";

import Plot from "react-plotly.js";

import {
  getInsights
} from "../services/api";

import "./Insights.css";


const Insights = () => {

  const [qiniData, setQiniData] =
    useState(null);

  const [targetingFilter, setTargetingFilter] =
    useState("100");

  const [decileFilter, setDecileFilter] =
    useState("all");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  const loadInsights = async () => {

    try {

      setLoading(true);
      setError("");

      const result =
        await getInsights();

      setQiniData(
        result
      );

    } catch (err) {

      setError(
        err.message ||
          "Unable to load live causal insights."
      );

      setQiniData(null);

    } finally {

      setLoading(false);

    }

  };


  useEffect(() => {

    loadInsights();

  }, []);


  const analysis = useMemo(() => {

    if (!qiniData) {
      return null;
    }


    const maxTargeting =
      Number(
        targetingFilter
      ) / 100;


    const indexes =
      qiniData.fractions

        .map(
          (
            fraction,
            index
          ) => ({
            fraction,
            index
          })
        )

        .filter(
          ({ fraction }) =>
            fraction <=
            maxTargeting
        );


    const fractions =
      indexes.map(
        (item) =>
          item.fraction
      );


    const qiniValues =
      indexes.map(
        (item) =>
          qiniData.qini_values[
            item.index
          ]
      );


    const randomBaseline =
      indexes.map(
        (item) =>
          qiniData.random_baseline[
            item.index
          ]
      );


    const maxQini =
      Math.max(
        ...qiniValues
      );


    const bestIndex =
      qiniValues.indexOf(
        maxQini
      );


    const bestTargeting =
      fractions[
        bestIndex
      ] * 100;


    const randomAtBest =
      randomBaseline[
        bestIndex
      ];


    const improvement =
      randomAtBest !== 0

        ? (
            (
              maxQini
              -
              randomAtBest
            )
            /
            Math.abs(
              randomAtBest
            )
          ) * 100

        : 0;


    let upliftEntries =
      Object.entries(
        qiniData.uplift_by_decile
        || {}
      );


    if (
      decileFilter !== "all"
    ) {

      upliftEntries =
        upliftEntries.filter(
          ([decile]) =>
            Number(decile)
            + 1
            ===
            Number(
              decileFilter
            )
        );

    }


    const allDeciles =
      Object.entries(
        qiniData.uplift_by_decile
        || {}
      );


    const bestDecile =
      allDeciles.length

        ? allDeciles.reduce(
            (
              best,
              current
            ) =>
              Number(
                current[1]
              )
              >
              Number(
                best[1]
              )
                ? current
                : best
          )

        : null;


    return {

      fractions,

      qiniValues,

      randomBaseline,

      maxQini,

      bestTargeting,

      randomAtBest,

      improvement,

      upliftEntries,

      bestDecile

    };

  }, [
    qiniData,
    targetingFilter,
    decileFilter
  ]);


  if (loading) {

    return (

      <div className="insights-page">

        <div className="insights-container">

          <div className="chart-card">

            <h2>
              Loading live causal insights...
            </h2>

          </div>

        </div>

      </div>

    );

  }


  if (error) {

    return (

      <div className="insights-page">

        <div className="insights-container">

          <div className="chart-card">

            <h2>
              No live analysis available
            </h2>

            <p>
              {error}
            </p>

            <button
              className="primary-button"
              onClick={
                loadInsights
              }
            >
              Retry
            </button>

          </div>

        </div>

      </div>

    );

  }


  return (

    <div className="insights-page">

      <div className="insights-container">

        <div className="page-header">

          <span className="page-label">
            CAUSAL ANALYSIS
          </span>

          <h1>
            Live Causal Insights
          </h1>

          <p>
            Qini and uplift results are
            calculated by the backend
            from the latest uploaded dataset.
          </p>

        </div>


        <section className="filters-card">

          <div>

            <label>
              Maximum Targeting Range
            </label>

            <select
              value={
                targetingFilter
              }
              onChange={(e) =>
                setTargetingFilter(
                  e.target.value
                )
              }
            >

              {[25, 50, 75, 100].map(
                (value) => (

                  <option
                    key={value}
                    value={value}
                  >
                    {value}%
                  </option>

                )
              )}

            </select>

          </div>


          <div>

            <label>
              Decile
            </label>

            <select
              value={
                decileFilter
              }
              onChange={(e) =>
                setDecileFilter(
                  e.target.value
                )
              }
            >

              <option value="all">
                All Deciles
              </option>

              {Object.keys(
                qiniData.uplift_by_decile
                || {}
              ).map(
                (key) => (

                  <option
                    key={key}
                    value={
                      Number(key) + 1
                    }
                  >
                    Decile{" "}
                    {Number(key) + 1}
                  </option>

                )
              )}

            </select>

          </div>


          <button
            className="primary-button"
            onClick={
              loadInsights
            }
          >
            ↻ Refresh
          </button>

        </section>


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
              At maximum Qini
            </small>

          </div>


          <div className="insight-card">

            <span className="card-label">
              Customers Analyzed
            </span>

            <strong>
              {Number(
                qiniData.customers
              ).toLocaleString()}
            </strong>

            <small>
              Rows in current upload
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
              At best targeting point
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
              Versus random baseline
            </small>

          </div>


          <div className="insight-card">

            <span className="card-label">
              Highest Uplift Segment
            </span>

            <strong>

              {analysis.bestDecile
                ? `D${
                    Number(
                      analysis.bestDecile[0]
                    ) + 1
                  }`
                : "N/A"}

            </strong>

            <small>

              {analysis.bestDecile
                ? `${
                    (
                      Number(
                        analysis.bestDecile[1]
                      )
                      * 100
                    ).toFixed(2)
                  }% uplift`
                : "No decile data"}

            </small>

          </div>

        </div>


        <section className="chart-card">

          <div className="chart-header">

            <span className="chart-label">
              MODEL PERFORMANCE
            </span>

            <h2>
              Qini Curve
            </h2>

            <p>
              Live comparison of the causal
              ranking against the random
              targeting baseline.
            </p>

          </div>


          <Plot

            data={[

              {

                x:
                  analysis.fractions.map(
                    (value) =>
                      value * 100
                  ),

                y:
                  analysis.qiniValues,

                type:
                  "scatter",

                mode:
                  "lines+markers",

                name:
                  "Causal Model",

                line: {
                  width: 3
                },

                marker: {
                  size: 5
                }

              },

              {

                x:
                  analysis.fractions.map(
                    (value) =>
                      value * 100
                  ),

                y:
                  analysis.randomBaseline,

                type:
                  "scatter",

                mode:
                  "lines",

                name:
                  "Random Targeting",

                line: {
                  dash:
                    "dash",

                  width: 2
                }

              }

            ]}

            layout={{

              autosize: true,

              xaxis: {

                title:
                  "Customers Targeted (%)",

                ticksuffix:
                  "%"

              },

              yaxis: {

                title:
                  "Cumulative Qini Value"

              },

              hovermode:
                "x unified",

              legend: {

                orientation:
                  "h",

                y:
                  1.1

              },

              margin: {

                l: 70,

                r: 30,

                t: 40,

                b: 70

              },

              paper_bgcolor:
                "transparent",

              plot_bgcolor:
                "transparent"

            }}

            useResizeHandler

            style={{
              width: "100%",
              height: "450px"
            }}

            config={{
              responsive: true,
              displaylogo: false
            }}

          />

        </section>


        <section className="chart-card">

          <div className="chart-header">

            <span className="chart-label">
              CUSTOMER SEGMENTATION
            </span>

            <h2>
              Uplift by Decile
            </h2>

            <p>
              Estimated treatment uplift for
              customers ranked by the current
              causal model.
            </p>

          </div>


          <Plot

            data={[

              {

                x:
                  analysis.upliftEntries.map(
                    ([decile]) =>
                      `D${
                        Number(decile) + 1
                      }`
                  ),

                y:
                  analysis.upliftEntries.map(
                    ([, value]) =>
                      Number(value)
                      * 100
                  ),

                type:
                  "bar",

                name:
                  "Customer Uplift",

                hovertemplate:
                  "Segment %{x}<br>" +
                  "Uplift: %{y:.2f}%" +
                  "<extra></extra>"

              }

            ]}

            layout={{

              autosize: true,

              xaxis: {
                title:
                  "Customer Decile"
              },

              yaxis: {

                title:
                  "Estimated Uplift (%)",

                ticksuffix:
                  "%"

              },

              margin: {

                l: 70,

                r: 30,

                t: 30,

                b: 70

              },

              paper_bgcolor:
                "transparent",

              plot_bgcolor:
                "transparent"

            }}

            useResizeHandler

            style={{
              width: "100%",
              height: "420px"
            }}

            config={{
              responsive: true,
              displaylogo: false
            }}

          />

        </section>


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
            estimates the causal effect of discount
            treatment on purchase probability while
            accounting for the observed customer
            characteristics used by the project.

          </p>


          <p>

            The Qini curve evaluates whether the
            model ranks customers so that
            higher-uplift customers are concentrated
            earlier in the targeting list.

          </p>


          <div className="recommendation-box">

            <strong>
              Targeting Recommendation
            </strong>

            <p>

              The highest Qini value in the
              selected range occurs at approximately{" "}

              <strong>
                {analysis.bestTargeting.toFixed(1)}%
              </strong>{" "}

              of customers targeted.

            </p>

          </div>


          <div className="recommendation-box">

            <strong>
              Highest-Uplift Segment
            </strong>

            <p>

              The strongest segment is{" "}

              <strong>

                {analysis.bestDecile
                  ? `Decile ${
                      Number(
                        analysis.bestDecile[0]
                      ) + 1
                    }`
                  : "not available"}

              </strong>

              {analysis.bestDecile
                ? `, with estimated uplift of ${
                    (
                      Number(
                        analysis.bestDecile[1]
                      ) * 100
                    ).toFixed(2)
                  }%.`
                : "."}

            </p>

          </div>


          <div className="warning-box">

            <strong>
              Important
            </strong>

            <p>

              These are causal estimates from
              the uploaded dataset. A positive
              ITE indicates predicted benefit
              from treatment; it is not a guarantee
              of an individual customer's outcome.

            </p>

          </div>

        </section>

      </div>

    </div>

  );

};


export default Insights;