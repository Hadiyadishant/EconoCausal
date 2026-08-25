import os
import pandas as pd
import numpy as np


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "mockretaildatacleaned.csv"
)

ITE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "ite_score.csv"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "revenue_predictions.csv"
)


# --------------------------------------------------
# Discount levels
# --------------------------------------------------

DISCOUNT_LEVELS = [0, 5, 10, 15, 20, 25, 30]


# --------------------------------------------------
# Load customer data
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

ite_df = pd.read_csv(ITE_PATH)


# --------------------------------------------------
# Validate ITE data
# --------------------------------------------------

required_ite_columns = [
    "customer_id",
    "ITE"
]

missing = [
    col
    for col in required_ite_columns
    if col not in ite_df.columns
]

if missing:
    raise ValueError(
        f"Missing columns in ite_scores.csv: {missing}"
    )


# --------------------------------------------------
# Merge ITE with customer data
# --------------------------------------------------

df = df.merge(
    ite_df[["customer_id", "ITE"]],
    on="customer_id",
    how="inner"
)


# --------------------------------------------------
# Validate customer revenue information
# --------------------------------------------------

if "avg_basket_size" not in df.columns:
    raise ValueError(
        "avg_basket_size column is required."
    )


if df["avg_basket_size"].isnull().any():
    raise ValueError(
        "avg_basket_size contains missing values."
    )


# --------------------------------------------------
# Revenue formulation
# --------------------------------------------------

# avg_basket_size represents the customer's
# potential order value / base revenue.

df["base_revenue"] = df["avg_basket_size"]


# --------------------------------------------------
# Generate revenue for every discount level
# --------------------------------------------------

records = []


for _, customer in df.iterrows():

    customer_id = customer["customer_id"]

    base_revenue = customer["base_revenue"]

    ITE = customer["ITE"]

    for discount in DISCOUNT_LEVELS:

        discount_fraction = discount / 100.0

        # Binary ITE interpretation:
        #
        # ITE represents the estimated change in
        # purchase probability when moving from
        # no discount -> discount treatment.
        #
        # The discount fraction is used here as a
        # simple personalization scaling factor.

        treatment_effect = (
            ITE * discount_fraction
        )

        predicted_purchase_probability = (
            0.5 + treatment_effect
        )

        # Keep probability within valid range.
        predicted_purchase_probability = np.clip(
            predicted_purchase_probability,
            0.0,
            1.0
        )

        predicted_revenue = (
            predicted_purchase_probability
            * base_revenue
        )

        records.append({
            "customer_id": customer_id,
            "discount": discount,
            "discount_fraction": discount_fraction,
            "base_revenue": base_revenue,
            "ITE": ITE,
            "predicted_purchase_probability":
                predicted_purchase_probability,
            "predicted_revenue":
                predicted_revenue
        })


# --------------------------------------------------
# Create prediction dataframe
# --------------------------------------------------

revenue_df = pd.DataFrame(records)


# --------------------------------------------------
# Validation
# --------------------------------------------------

print(
    f"Customers available: "
    f"{df['customer_id'].nunique()}"
)

print(
    f"Discount options: "
    f"{DISCOUNT_LEVELS}"
)

print(
    "\nTotal revenue prediction rows:",
    len(revenue_df)
)


print("\nRevenue prediction validation:")

print(
    "Missing predicted revenue:",
    revenue_df["predicted_revenue"].isnull().sum()
)

print(
    "Minimum predicted revenue:",
    revenue_df["predicted_revenue"].min()
)

print(
    "Maximum predicted revenue:",
    revenue_df["predicted_revenue"].max()
)


# --------------------------------------------------
# Display sample
# --------------------------------------------------

print("\nSample predictions:")

print(
    revenue_df[
        [
            "customer_id",
            "discount",
            "discount_fraction",
            "base_revenue",
            "ITE",
            "predicted_purchase_probability",
            "predicted_revenue"
        ]
    ].head(14)
)


# --------------------------------------------------
# Save predictions
# --------------------------------------------------

revenue_df.to_csv(
    OUTPUT_PATH,
    index=False
)


print(
    "\nRevenue prediction completed."
)

print(
    "\nSaved revenue predictions to:"
)

print(OUTPUT_PATH)