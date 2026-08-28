"""
Day 6 - Optimization Testing

Purpose:
    Test the prescriptive optimization under
    different marketing budgets.
"""

import os
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "optimized_discount_assignments.csv"
)


# ============================================================
# LOAD FINAL PRESCRIPTION
# ============================================================

df = pd.read_csv(
    OUTPUT_PATH
)


# ============================================================
# BASIC VALIDATION
# ============================================================

required_columns = [
    "customer_id",
    "optimal_discount",
    "predicted_revenue",
    "marketing_cost"
]

missing = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing:
    raise ValueError(
        f"Missing columns: {missing}"
    )


# ============================================================
# TEST 1 - CUSTOMER ASSIGNMENT
# ============================================================

customer_count = (
    df["customer_id"].nunique()
)

row_count = len(df)

print("=" * 60)
print("DAY 6 - OPTIMIZATION TESTING")
print("=" * 60)

print(
    f"\nCustomers: {customer_count}"
)

print(
    f"Prescription rows: {row_count}"
)

if customer_count != row_count:

    raise ValueError(
        "Duplicate customer assignments detected."
    )

print(
    "Customer assignment test: PASSED"
)


# ============================================================
# TEST 2 - DISCOUNT LEVELS
# ============================================================

allowed_discounts = {
    0,
    5,
    10,
    15,
    20,
    25,
    30
}

invalid = df[
    ~df["optimal_discount"].isin(
        allowed_discounts
    )
]

if len(invalid) > 0:

    raise ValueError(
        "Invalid discount level detected."
    )

print(
    "Discount level test: PASSED"
)


# ============================================================
# TEST 3 - REVENUE VALIDATION
# ============================================================

if df["predicted_revenue"].isnull().any():

    raise ValueError(
        "Missing predicted revenue."
    )

total_revenue = (
    df["predicted_revenue"].sum()
)

print(
    f"\nTotal predicted revenue: "
    f"₹{total_revenue:.2f}"
)


# ============================================================
# TEST 4 - COST VALIDATION
# ============================================================

if df["marketing_cost"].isnull().any():

    raise ValueError(
        "Missing marketing cost."
    )

total_cost = (
    df["marketing_cost"].sum()
)

print(
    f"Total marketing cost: "
    f"₹{total_cost:.2f}"
)


# ============================================================
# TEST 5 - BUDGET
# ============================================================

BUDGET = 5000.0

budget_remaining = (
    BUDGET - total_cost
)

print(
    f"Budget: ₹{BUDGET:.2f}"
)

print(
    f"Budget remaining: "
    f"₹{budget_remaining:.2f}"
)


if total_cost > BUDGET:

    raise ValueError(
        "Budget exceeded."
    )

print(
    "Budget test: PASSED"
)


# ============================================================
# TEST 6 - CUSTOMER TREATMENT
# ============================================================

customers_treated = (
    df["optimal_discount"] > 0
).sum()

average_discount = (
    df["optimal_discount"].mean()
)

print(
    f"\nCustomers receiving discount: "
    f"{customers_treated}"
)

print(
    f"Average discount: "
    f"{average_discount:.2f}%"
)


# ============================================================
# FINAL
# ============================================================

print("DAY 6 TESTING COMPLETED SUCCESSFULLY")