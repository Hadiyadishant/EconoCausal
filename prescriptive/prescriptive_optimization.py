"""
Week 3 - Prescriptive Optimization

Owner: Dishant

Purpose:
Use Princy's prepared customer-level prediction matrices and
find the mathematically optimal discount allocation.

Input:
    data/customer_optimizer_matrices_final.npz

The NPZ contains:
    customer_ids
    discount_levels
    revenue_matrix
    cost_matrix

Optimization:
    Maximize total predicted revenue

Constraints:
    1. Exactly one discount per customer
    2. Total marketing cost <= budget
    3. Discount levels are limited to Princy's supplied levels

Output:
    data/optimized_discount_assignments.csv
"""

import os
import numpy as np
import pandas as pd

from scipy.optimize import milp, LinearConstraint, Bounds


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "customer_optimizer_matrices_final.npz"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "optimized_discount_assignments.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

BUDGET = 5000.0


# ============================================================
# LOAD PRINCY'S DATA
# ============================================================

print("=" * 60)
print("PRESCRIPTIVE OPTIMIZATION")
print("=" * 60)

print("\nLoading Princy's optimization input...")

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(
        f"Princy's optimization input was not found:\n"
        f"{INPUT_PATH}"
    )


data = np.load(
    INPUT_PATH,
    allow_pickle=True
)


customer_ids = data["customer_ids"]

discount_levels = data["discount_levels"]

revenue_matrix = data["revenue_matrix"]

cost_matrix = data["cost_matrix"]


# ============================================================
# VALIDATION
# ============================================================

print("\nInput validation")

n_customers = len(customer_ids)

n_discounts = len(discount_levels)


if revenue_matrix.shape != (
    n_customers,
    n_discounts
):
    raise ValueError(
        "Revenue matrix shape does not match "
        "customer IDs and discount levels."
    )


if cost_matrix.shape != (
    n_customers,
    n_discounts
):
    raise ValueError(
        "Cost matrix shape does not match "
        "customer IDs and discount levels."
    )


if np.isnan(revenue_matrix).any():
    raise ValueError(
        "Revenue matrix contains NaN values."
    )


if np.isnan(cost_matrix).any():
    raise ValueError(
        "Cost matrix contains NaN values."
    )


if (revenue_matrix < 0).any():
    raise ValueError(
        "Revenue matrix contains negative values."
    )


if (cost_matrix < 0).any():
    raise ValueError(
        "Cost matrix contains negative values."
    )


if len(set(customer_ids)) != n_customers:
    raise ValueError(
        "Duplicate customer IDs found."
    )


print(
    f"Customers: {n_customers}"
)

print(
    f"Discount levels: {discount_levels.tolist()}"
)

print(
    f"Revenue matrix shape: {revenue_matrix.shape}"
)

print(
    f"Cost matrix shape: {cost_matrix.shape}"
)


# ============================================================
# DECISION VARIABLES
# ============================================================

"""
x[i,j] = 1

if customer i receives discount j.

x[i,j] = 0 otherwise.

There are:

    customers × discount_levels

binary variables.
"""

number_of_variables = (
    n_customers * n_discounts
)


print(
    "\nDecision variables:",
    number_of_variables
)


# ============================================================
# OBJECTIVE
# ============================================================

"""
SciPy milp minimizes by default.

Therefore:

    maximize revenue

is converted into:

    minimize -revenue
"""

objective = -revenue_matrix.flatten()


# ============================================================
# BINARY BOUNDS
# ============================================================

lower_bounds = np.zeros(
    number_of_variables
)

upper_bounds = np.ones(
    number_of_variables
)

bounds = Bounds(
    lower_bounds,
    upper_bounds
)


# ============================================================
# CONSTRAINT 1
# EXACTLY ONE DISCOUNT PER CUSTOMER
# ============================================================

"""
For every customer:

    x[i,0] + x[i,1] + ... + x[i,6] = 1
"""

customer_constraints = np.zeros(
    (n_customers, number_of_variables)
)


for i in range(n_customers):

    start = i * n_discounts

    end = start + n_discounts

    customer_constraints[
        i,
        start:end
    ] = 1


customer_constraint = LinearConstraint(
    customer_constraints,
    np.ones(n_customers),
    np.ones(n_customers)
)


# ============================================================
# CONSTRAINT 2
# TOTAL MARKETING COST <= BUDGET
# ============================================================

budget_coefficients = (
    cost_matrix.flatten()
)


budget_constraint = LinearConstraint(
    budget_coefficients.reshape(1, -1),
    -np.inf,
    BUDGET
)


# ============================================================
# RUN SCIPY OPTIMIZER
# ============================================================

print("\nRunning SciPy optimization...")

result = milp(
    c=objective,
    integrality=np.ones(
        number_of_variables
    ),
    bounds=bounds,
    constraints=[
        customer_constraint,
        budget_constraint
    ],
    options={
        "time_limit": 300
    }
)


# ============================================================
# CHECK OPTIMIZATION RESULT
# ============================================================

if not result.success:
    raise RuntimeError(
        "Optimization failed:\n"
        f"{result.message}"
    )


print(
    "\nOptimization completed successfully."
)


# ============================================================
# CONVERT SOLUTION
# ============================================================

solution = result.x.reshape(
    n_customers,
    n_discounts
)


selected_indices = np.argmax(
    solution,
    axis=1
)


assigned_discounts = (
    discount_levels[selected_indices]
)


assigned_revenue = (
    revenue_matrix[
        np.arange(n_customers),
        selected_indices
    ]
)


assigned_cost = (
    cost_matrix[
        np.arange(n_customers),
        selected_indices
    ]
)


# ============================================================
# FINAL ALLOCATION MATRIX
# ============================================================

allocation = pd.DataFrame({

    "customer_id":
        customer_ids,

    "optimal_discount":
        assigned_discounts,

    "discount_fraction":
        assigned_discounts / 100.0,

    "predicted_revenue":
        assigned_revenue,

    "marketing_cost":
        assigned_cost

})


# ============================================================
# FINAL METRICS
# ============================================================

total_cost = (
    allocation["marketing_cost"]
    .sum()
)

total_revenue = (
    allocation["predicted_revenue"]
    .sum()
)

budget_remaining = (
    BUDGET - total_cost
)

customers_with_discount = (
    allocation["optimal_discount"] > 0
).sum()

average_discount = (
    allocation["optimal_discount"]
    .mean()
)


# ============================================================
# FINAL VALIDATION
# ============================================================

budget_satisfied = (
    total_cost <= BUDGET + 1e-8
)


one_discount_per_customer = (
    allocation["customer_id"].nunique()
    == n_customers
)


print("\n" + "=" * 60)
print("OPTIMIZATION RESULT")
print("=" * 60)

print(
    f"Customers: {n_customers}"
)

print(
    f"Customers receiving discount: "
    f"{customers_with_discount}"
)

print(
    f"Average discount: "
    f"{average_discount:.2f}%"
)

print(
    f"Total predicted revenue: "
    f"₹{total_revenue:.2f}"
)

print(
    f"Total marketing cost: "
    f"₹{total_cost:.2f}"
)

print(
    f"Budget: "
    f"₹{BUDGET:.2f}"
)

print(
    f"Budget remaining: "
    f"₹{budget_remaining:.2f}"
)

print(
    f"Budget constraint satisfied: "
    f"{budget_satisfied}"
)

print(
    f"One assignment per customer: "
    f"{one_discount_per_customer}"
)


# ============================================================
# SAVE FINAL PRESCRIPTION
# ============================================================

allocation.to_csv(
    OUTPUT_PATH,
    index=False
)


print(
    "\nFinal prescription saved to:"
)

print(
    OUTPUT_PATH
)


print("\nSample allocation:")

print(
    allocation.head(10).to_string(
        index=False
    )
)