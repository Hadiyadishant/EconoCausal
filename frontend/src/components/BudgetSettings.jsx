import React, { useState } from "react";
import {
  getBudget,
  saveBudget,
} from "../services/storage";

import "./BudgetSettings.css";

const BudgetSettings = () => {
  const existingBudget = getBudget();

  const [budget, setBudget] = useState(
    existingBudget?.totalBudget ?? ""
  );

  const [cost, setCost] = useState(
    existingBudget?.costPerCustomer ?? ""
  );

  const [maxCustomers, setMaxCustomers] =
    useState(
      existingBudget?.maxCustomers ?? ""
    );

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  const handleSave = () => {
    setMessage("");
    setError("");

    const totalBudget = Number(budget);
    const costPerCustomer = Number(cost);
    const maximumCustomers =
      Number(maxCustomers);

    if (
      !Number.isFinite(totalBudget) ||
      !Number.isFinite(costPerCustomer) ||
      !Number.isFinite(maximumCustomers)
    ) {
      setError(
        "Please enter valid numbers."
      );
      return;
    }

    if (
      totalBudget <= 0 ||
      costPerCustomer <= 0 ||
      maximumCustomers <= 0
    ) {
      setError(
        "All values must be greater than zero."
      );
      return;
    }

    const affordableCustomers =
      Math.floor(
        totalBudget / costPerCustomer
      );

    const allowedCustomers =
      Math.min(
        affordableCustomers,
        maximumCustomers
      );

    saveBudget({
      totalBudget,
      costPerCustomer,
      maxCustomers: maximumCustomers,
      affordableCustomers,
      allowedCustomers,
      updatedAt:
        new Date().toISOString(),
    });

    setMessage(
      `Budget saved successfully. Maximum targetable customers: ${allowedCustomers}.`
    );
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
            Define campaign budget constraints
            used by the causal targeting workflow.
          </p>
        </div>

        <div className="budget-card">

          <div className="form-group">
            <label>
              Total Marketing Budget
            </label>

            <div className="input-wrapper">
              <span>₹</span>

              <input
                type="number"
                min="0"
                placeholder="50000"
                value={budget}
                onChange={(e) =>
                  setBudget(e.target.value)
                }
              />
            </div>

            <small>
              Example: ₹50,000
            </small>
          </div>


          <div className="form-group">
            <label>
              Cost per Customer
            </label>

            <div className="input-wrapper">
              <span>₹</span>

              <input
                type="number"
                min="0"
                placeholder="100"
                value={cost}
                onChange={(e) =>
                  setCost(e.target.value)
                }
              />
            </div>

            <small>
              Estimated campaign cost per customer
            </small>
          </div>


          <div className="form-group">
            <label>
              Maximum Customers
            </label>

            <input
              className="normal-input"
              type="number"
              min="1"
              placeholder="500"
              value={maxCustomers}
              onChange={(e) =>
                setMaxCustomers(
                  e.target.value
                )
              }
            />

            <small>
              Maximum number of customers
              to target
            </small>
          </div>


          <button
            className="primary-button"
            onClick={handleSave}
          >
            Save Budget Settings
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