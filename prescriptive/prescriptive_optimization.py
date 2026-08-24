import os
import pandas as pd


# Paths

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "revenue_predictions.csv"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "optimized_discount_assignments.csv"
)


# Configuration

BUDGET = 5000.0


# Load Revenue Predictions

df = pd.read_csv(INPUT_PATH)

required_columns = [
    "customer_id",
    "discount",
    "discount_fraction",
    "base_revenue",
    "ITE",
    "predicted_revenue"
]

missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )


# Calculate Discount Cost

df["discount_cost"] = (
    df["base_revenue"] *
    df["discount_fraction"]
)


# Calculate Incremental Revenue

df["incremental_revenue"] = (
    df["predicted_revenue"] -
    df["base_revenue"]
)


# Best option per customer

best_options = (
    df.sort_values(
        "predicted_revenue",
        ascending=False
    )
    .groupby("customer_id")
    .first()
    .reset_index()
)


# Budget Check

total_cost = best_options["discount_cost"].sum()


print("\nInitial allocation")
print(
    f"Total discount cost: ₹{total_cost:.2f}"
)


# If budget exceeded
# reduce customers with lowest
# revenue benefit per cost

if total_cost > BUDGET:

    best_options["benefit_per_cost"] = (
        best_options["incremental_revenue"] /
        best_options["discount_cost"].replace(0, float("inf"))
    )

    best_options = best_options.sort_values(
        "benefit_per_cost",
        ascending=False
    )

    selected = []

    current_cost = 0.0

    for _, row in best_options.iterrows():

        cost = row["discount_cost"]

        if current_cost + cost <= BUDGET:

            selected.append(row)

            current_cost += cost

    best_options = pd.DataFrame(selected)


# Final Allocation Matrix

allocation = best_options[
    [
        "customer_id",
        "discount",
        "discount_fraction",
        "predicted_revenue",
        "discount_cost",
        "ITE"
    ]
].copy()


allocation = allocation.sort_values(
    "customer_id"
)


# Save Prescription

allocation.to_csv(
    OUTPUT_PATH,
    index=False
)


# Final Validation

final_cost = allocation["discount_cost"].sum()

total_revenue = allocation[
    "predicted_revenue"
].sum()


print("\nPRESCRIPTION GENERATED")

print(
    f"Customers allocated: {len(allocation)}"
)

print(
    f"Total marketing cost: ₹{final_cost:.2f}"
)

print(
    f"Budget: ₹{BUDGET:.2f}"
)

print(
    f"Total predicted revenue: ₹{total_revenue:.2f}"
)

print(
    f"Budget constraint satisfied: "
    f"{final_cost <= BUDGET}"
)


print(
    f"\nSaved allocation matrix:\n{OUTPUT_PATH}"
)