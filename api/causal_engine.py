import os
import sys
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(BASE_DIR)


FEATURE_COLUMNS = [
    "age",
    "income",
    "previous_purchases",
    "campaign_response",
    "customer_tenure_days",
    "avg_basket_size"
]


def preprocess_data(customer_data):
    """
    Convert incoming customer data
    into the feature format required
    by the causal model.
    """

    df = pd.DataFrame(customer_data)

    missing_columns = [
        column
        for column in FEATURE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    return df[FEATURE_COLUMNS]


def get_required_features():
    return FEATURE_COLUMNS