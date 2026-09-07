import React, {
  useEffect,
  useState
} from "react";

import {
  getBudget,
  optimizeBudget
} from "../services/api";

import {
  saveBudget
} from "../services/storage";

import "./BudgetSettings.css";


const BudgetSettings = () => {

  const [budget, setBudget] =
    useState("");

  const [maxCustomers, setMaxCustomers] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(true);


  useEffect(() => {

    getBudget()

      .then((data) => {

        setBudget(
          data.total_budget ?? ""
        );

        setMaxCustomers(
          data.max_customers ?? ""
        );

      })

      .catch((err) => {

        setError(
          err.message
        );

      })

      .finally(() => {

        setLoading(false);

      });

  }, []);


  const handleSave = async () => {

    setMessage("");
    setError("");

    const totalBudget =
      Number(budget);

    const maximumCustomers =
      maxCustomers === ""
        ? null
        : Number(maxCustomers);


    if (
      !Number.isFinite(
        totalBudget
      )
      ||
      totalBudget <= 0
    ) {

      setError(
        "Total budget must be greater than zero."
      );

      return;
    }


    if (
      maximumCustomers !== null
      &&
      (
        !Number.isInteger(
          maximumCustomers
        )
        ||
        maximumCustomers <= 0
      )
    ) {

      setError(
        "Maximum customers must be a positive whole number."
      );

      return;
    }


    setLoading(true);


    try {

      const response =
        await optimizeBudget(
          totalBudget,
          maximumCustomers
        );

      const result =
        response.optimization;


      saveBudget({

        totalBudget,

        maxCustomers:
          maximumCustomers,

        updatedAt:
          new Date().toISOString()

      });


      setMessage(

        `Optimization completed. ${
          result.customers_allocated.toLocaleString()
        } of ${
          result.customers.toLocaleString()
        } customers received a positive discount. Budget remaining: ₹${
          result.budget_remaining.toFixed(2)
        }.`

      );

    } catch (err) {

      setError(
        err.message ||
          "Unable to run the optimizer."
      );

    } finally {

      setLoading(false);

    }

  };


  return (

    <div className="budget-page">

      <div className="budget-container">

        <div className="page-header">

          <span className="page-label">
            BUDGET CONTROL
          </span>

          <h1>
            Budget Settings
          </h1>

          <p>
            Changing these settings immediately
            reruns the SciPy optimizer, so the
            Prescription page always reflects
            the latest budget.
          </p>

        </div>


        <div className="budget-card">

          <div className="form-group">

            <label>
              Total Marketing Budget
            </label>

            <div className="input-wrapper">

              <span>
                ₹
              </span>

              <input
                type="number"
                min="1"
                value={budget}
                onChange={(e) =>
                  setBudget(
                    e.target.value
                  )
                }
                placeholder="5000"
              />

            </div>

            <small>
              Total amount available for
              discount allocation.
            </small>

          </div>


          <div className="form-group">

            <label>
              Maximum Customers (optional)
            </label>

            <input
              className="normal-input"
              type="number"
              min="1"
              value={maxCustomers}
              onChange={(e) =>
                setMaxCustomers(
                  e.target.value
                )
              }
              placeholder="No explicit customer cap"
            />

            <small>
              Optional cap on customers
              receiving a positive discount.
            </small>

          </div>


          <button
            className="primary-button"
            onClick={handleSave}
            disabled={loading}
          >

            {loading
              ? "Running Optimization..."
              : "Save & Re-run Optimization"}

          </button>


          {error && (

            <div className="budget-error">
              {error}
            </div>

          )}


          {message && (

            <div className="budget-message">
              ✓ {message}
            </div>

          )}

        </div>

      </div>

    </div>

  );

};


export default BudgetSettings;