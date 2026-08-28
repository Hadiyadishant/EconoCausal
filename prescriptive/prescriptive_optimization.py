"""
Week 3 - Day 4
Prescriptive Optimization

Owner: Dishant

Uses ONLY Princy's prepared optimization matrices.

Objective:
    Maximize total predicted revenue.

Decision:
    Select exactly one discount level per customer.

Constraint:
    Total marketing cost <= budget.
"""

import os
import numpy as np
import pandas as pd

from scipy.optimize import milp, LinearConstraint, Bounds


# --------------------------------------------------
# Paths
# --------------------------------------------------

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


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BUDGET = 5000.0


# --------------------------------------------------
# Load Princy's data
# --------------------------------------------------

print("=" * 60)
print("DAY 4 - PRESCRIPTIVE OPTIMIZATION")
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


# --------------------------------------------------
# Basic validation
# --------------------------------------------------

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


# --------------------------------------------------
# Decision variables
# --------------------------------------------------

# x[i,j] = 1 if customer i receives discount j

n_variables = n_customers * n_discounts

objective = -revenue_matrix.flatten()

bounds = Bounds(
    np.zeros(n_variables),
    np.ones(n_variables)
)


# --------------------------------------------------
# Exactly one discount per customer
# --------------------------------------------------

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


# --------------------------------------------------
# Budget constraint
# --------------------------------------------------

budget_constraint = LinearConstraint(
    cost_matrix.flatten().reshape(1, -1),
    -np.inf,
    BUDGET
)


# --------------------------------------------------
# Run MILP
# --------------------------------------------------

print("\nRunning SciPy MILP optimizer...")

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


# --------------------------------------------------
# Convert solution
# --------------------------------------------------

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


# --------------------------------------------------
# Create prescription
# --------------------------------------------------

allocation = pd.DataFrame({
    "customer_id": customer_ids,
    "optimal_discount": assigned_discount,
    "discount_fraction": assigned_discount / 100,
    "predicted_revenue": assigned_revenue,
    "marketing_cost": assigned_cost
})


# --------------------------------------------------
# Save result
# --------------------------------------------------

allocation.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\nOptimization completed successfully.")

print(
    f"Prescription saved to:\n{OUTPUT_PATH}"
)


# --------------------------------------------------
# Day 5 - Constraint validation
# --------------------------------------------------

MIN_DISCOUNT = discount_levels.min()
MAX_DISCOUNT = discount_levels.max()

allowed_discounts = set(
    discount_levels.tolist()
)

total_cost = allocation["marketing_cost"].sum()

budget_satisfied = (
    total_cost <= BUDGET + 1e-8
)

one_discount_per_customer = (
    allocation["customer_id"].nunique()
    == n_customers
)

discount_bounds_satisfied = (
    allocation["optimal_discount"].between(
        MIN_DISCOUNT,
        MAX_DISCOUNT
    ).all()
)

allowed_discount_satisfied = (
    allocation["optimal_discount"]
    .isin(allowed_discounts)
    .all()
)


print("\n" + "=" * 60)
print("DAY 5 - CONSTRAINT VALIDATION")
print("=" * 60)

print(
    f"Total marketing cost: ₹{total_cost:.2f}"
)

print(
    f"Budget: ₹{BUDGET:.2f}"
)

print(
    f"Budget constraint: {budget_satisfied}"
)

print(
    f"One discount per customer: "
    f"{one_discount_per_customer}"
)

print(
    f"Discount bounds: "
    f"{discount_bounds_satisfied}"
)

print(
    f"Allowed discount levels: "
    f"{allowed_discount_satisfied}"
)

if not all([
    budget_satisfied,
    one_discount_per_customer,
    discount_bounds_satisfied,
    allowed_discount_satisfied
]):
    raise ValueError(
        "Optimization result failed constraint validation."
    )

print("\nAll Day 5 constraints satisfied.")