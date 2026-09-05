"""
Week 3 - Day 7
Prescriptive Optimization - Final Version

Owner: Dishant

Uses ONLY Princy's prepared optimization matrices.

Input:
    data/customer_optimizer_matrices_final.npz

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
print("DAY 7 - FINAL PRESCRIPTIVE OPTIMIZATION")
print("=" * 60)

print("\nLoading Princy's optimization matrices...")

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(
        f"Princy's input file not found:\n{INPUT_PATH}"
    )

data = np.load(INPUT_PATH, allow_pickle=True)

customer_ids = data["customer_ids"]
discount_levels = data["discount_levels"]
revenue_matrix = data["revenue_matrix"]
cost_matrix = data["cost_matrix"]


# ============================================================
# VALIDATION
# ============================================================

n_customers = len(customer_ids)
n_discounts = len(discount_levels)

if revenue_matrix.shape != (n_customers, n_discounts):
    raise ValueError("Revenue matrix shape is invalid.")

if cost_matrix.shape != (n_customers, n_discounts):
    raise ValueError("Cost matrix shape is invalid.")

if np.isnan(revenue_matrix).any():
    raise ValueError("Revenue matrix contains NaN values.")

if np.isnan(cost_matrix).any():
    raise ValueError("Cost matrix contains NaN values.")

if (revenue_matrix < 0).any():
    raise ValueError("Revenue matrix contains negative values.")

if (cost_matrix < 0).any():
    raise ValueError("Cost matrix contains negative values.")

print(f"Customers: {n_customers}")
print(f"Discount levels: {discount_levels.tolist()}")


# ============================================================
# DECISION VARIABLES
# ============================================================

# x[i,j] = 1 when customer i receives discount j

n_variables = n_customers * n_discounts

objective = -revenue_matrix.flatten()

bounds = Bounds(
    np.zeros(n_variables),
    np.ones(n_variables)
)


# ============================================================
# ONE DISCOUNT PER CUSTOMER
# ============================================================

customer_matrix = np.zeros(
    (n_customers, n_variables)
)

for i in range(n_customers):
    start = i * n_discounts
    end = start + n_discounts
    customer_matrix[i, start:end] = 1

customer_constraint = LinearConstraint(
    customer_matrix,
    np.ones(n_customers),
    np.ones(n_customers)
)


# ============================================================
# BUDGET CONSTRAINT
# ============================================================

budget_constraint = LinearConstraint(
    cost_matrix.flatten().reshape(1, -1),
    -np.inf,
    BUDGET
)


# ============================================================
# RUN FINAL OPTIMIZATION
# ============================================================

print("\nRunning final SciPy MILP optimization...")

result = milp(
    c=objective,
    integrality=np.ones(n_variables),
    bounds=bounds,
    constraints=[
        customer_constraint,
        budget_constraint
    ],
    options={"time_limit": 300}
)

if not result.success:
    raise RuntimeError(
        f"Optimization failed: {result.message}"
    )


# ============================================================
# CREATE FINAL ASSIGNMENT
# ============================================================

solution = result.x.reshape(
    n_customers,
    n_discounts
)

selected = np.argmax(
    solution,
    axis=1
)

assigned_discount = discount_levels[selected]

assigned_revenue = revenue_matrix[
    np.arange(n_customers),
    selected
]

assigned_cost = cost_matrix[
    np.arange(n_customers),
    selected
]


allocation = pd.DataFrame({
    "customer_id": customer_ids,
    "optimal_discount": assigned_discount,
    "discount_fraction": assigned_discount / 100.0,
    "predicted_revenue": assigned_revenue,
    "marketing_cost": assigned_cost
})


# ============================================================
# FINAL METRICS
# ============================================================

total_revenue = allocation["predicted_revenue"].sum()
total_cost = allocation["marketing_cost"].sum()

budget_remaining = BUDGET - total_cost

customers_with_discount = (
    allocation["optimal_discount"] > 0
).sum()

average_discount = (
    allocation["optimal_discount"].mean()
)


# ============================================================
# FINAL VALIDATION
# ============================================================

budget_satisfied = total_cost <= BUDGET + 1e-8

one_discount_per_customer = (
    allocation["customer_id"].nunique()
    == n_customers
)

allowed_discount = (
    allocation["optimal_discount"]
    .isin(discount_levels)
    .all()
)


if not (
    budget_satisfied
    and one_discount_per_customer
    and allowed_discount
):
    raise ValueError(
        "Final optimization validation failed."
    )


# ============================================================
# SAVE FINAL PRESCRIPTION
# ============================================================

allocation.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 60)
print("FINAL OPTIMIZATION RESULT")
print("=" * 60)

print(f"Customers: {n_customers}")
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
    f"One discount per customer: "
    f"{one_discount_per_customer}"
)

print(
    f"Allowed discount levels: "
    f"{allowed_discount}"
)

print("\nFinal prescription saved to:")
print(OUTPUT_PATH)

print("\nSample allocation:")
print(
    allocation.head(10).to_string(index=False)
)

print("\n" + "=" * 60)
print("DAY 7 COMPLETED SUCCESSFULLY")
print("=" * 60)