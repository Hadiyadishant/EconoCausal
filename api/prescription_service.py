import json
import os

import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


PRESCRIPTION_PATH = os.path.join(
    BASE_DIR,
    "data",
    "optimized_discount_assignments.csv"
)


SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "data",
    "runtime_optimization_summary.json"
)


# =========================================================
# LOAD PRESCRIPTION
# =========================================================

def load_prescription():

    if not os.path.exists(
        PRESCRIPTION_PATH
    ):
        raise FileNotFoundError(
            "Optimized prescription file not found. "
            "Set a budget and run optimization first."
        )

    df = pd.read_csv(
        PRESCRIPTION_PATH
    )

    required_columns = [
        "customer_id",
        "optimal_discount",
        "discount_fraction",
        "predicted_revenue",
        "marketing_cost",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Prescription file missing columns: {missing}"
        )

    return df


# =========================================================
# LOAD OPTIMIZATION SUMMARY
# =========================================================

def get_optimization_summary():

    if not os.path.exists(
        SUMMARY_PATH
    ):
        return None

    with open(
        SUMMARY_PATH,
        "r",
        encoding="utf-8"
    ) as handle:

        return json.load(handle)


# =========================================================
# GET PRESCRIPTION
# =========================================================

def get_prescription(
    customer_id=None
):

    df = load_prescription()

    if customer_id is not None:

        df = df[
            df["customer_id"] == customer_id
        ]

    return df.to_dict(
        orient="records"
    )