import os
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

PRESCRIPTION_PATH = os.path.join(
    BASE_DIR,
    "data",
    "optimized_discount_assignments.csv"
)


def load_prescription():

    if not os.path.exists(PRESCRIPTION_PATH):
        raise FileNotFoundError(
            "Optimized prescription file not found."
        )

    df = pd.read_csv(PRESCRIPTION_PATH)

    required_columns = [
        "customer_id",
        "optimal_discount",
        "discount_fraction",
        "predicted_revenue",
        "marketing_cost"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Prescription file missing columns: {missing}"
        )

    return df


def get_prescription(customer_id=None):

    df = load_prescription()

    if customer_id is not None:

        df = df[
            df["customer_id"] == customer_id
        ]

    return df.to_dict(orient="records")