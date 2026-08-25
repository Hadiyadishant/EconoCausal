import os
import pandas as pd


# Paths

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# IMPORTANT:
# This is Princy's prediction output.
INPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "revenue_predictions.csv"
)

# Configuration

BUDGET = 5000.0


# Load Princy's prediction output

df = pd.read_csv(INPUT_PATH)


# Validate required fields

required_columns = [
    "customer_id",
    "discount",
    "discount_fraction",
    "predicted_revenue"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns from "
        f"Princy's prediction output: {missing_columns}"
    )


# Customer and discount information

customers = df["customer_id"].unique()

discount_levels = sorted(
    df["discount"].unique()
)


print("OPTIMIZATION INPUT PREPARATION")

print(
    f"\nCustomers: {len(customers)}"
)

print(
    f"Discount levels: {discount_levels}"
)

print(
    f"Prediction rows: {len(df)}"
)

# Create customer × discount revenue matrix
#
# NOTE:

# reshaping data here.


revenue_matrix = df.pivot(
    index="customer_id",
    columns="discount",
    values="predicted_revenue"
)


# Validate matrix

if revenue_matrix.isnull().any().any():

    raise ValueError(
        "Some customers do not have predicted "
        "revenue for every discount level."
    )


print("\nRevenue matrix created.")

print(
    revenue_matrix.head()
)

# Optimization variables

# One decision variable per customer:

# d_1, d_2, d_3, ..., d_n

# These variables will be used by the SciPy


number_of_customers = len(customers)

print(
    "\nOptimization variables:"
)

print(
    f"Number of decision variables: "
    f"{number_of_customers}"
)

print(
    "Each variable represents the discount "
    "assigned to one customer."
)


# Objective definition

def maximize_total_revenue(discounts):
    """
    Objective concept for the optimizer.

    The optimizer will select one discount
    for every customer.

    The objective is to maximize the
    total predicted revenue.

    This function currently documents the
    optimization objective. The actual SciPy
    optimization will be implemented in
    prescriptive_optimization.py.
    """

    return "MAXIMIZE TOTAL PREDICTED REVENUE"


# Budget constraint definition

def budget_constraint(total_marketing_cost):
    """
    Budget constraint:

        Total Marketing Cost <= Budget
    """

    return BUDGET - total_marketing_cost


# Optimization formulation summary

print("\nMATHEMATICAL FORMULATION")

print(
    "Objective:"
)

print(
    "Maximize Σ predicted_revenue_i(d_i)"
)

print(
    "\nConstraint:"
)

print(
    "Σ marketing_cost_i(d_i) <= budget"
)

print(
    "\nDecision variables:"
)

print(
    "d_1, d_2, ..., d_n"
)

print(
    "\nBudget:"
)

print(
    f"₹{BUDGET:.2f}"
)

# Main

if __name__ == "__main__":

    print(
        "\nDay 3 optimization input preparation "
        "completed successfully."
    )