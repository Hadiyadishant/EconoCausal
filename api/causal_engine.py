import os
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from econml.dml import CausalForestDML


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "notebooks",
    "dml_ready_data.csv"
)

SCALER_PATH = os.path.join(
    BASE_DIR,
    "notebooks",
    "confounder_scaler.pkl"
)

ENCODER_PATH = os.path.join(
    BASE_DIR,
    "notebooks",
    "channel_encoder.pkl"
)


X_FEATURES = [
    "age",
    "income",
    "previous_purchases",
    "campaign_response",
    "customer_tenure_days",
    "avg_basket_size",
]


RAW_REQUIRED_COLUMNS = X_FEATURES + [
    "customer_id",
    "discount",
    "purchase",
    "channel",
]


def _prepare_training_data(df):

    required = X_FEATURES + [
        "discount",
        "purchase",
        "channel_online"
    ]

    missing = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Training data missing required columns: {missing}"
        )

    X = df[X_FEATURES].copy()

    W = df[["channel_online"]].copy()

    T = (
        df["discount"] > 0
    ).astype(int)

    Y = df["purchase"]

    return X, W, T, Y


@lru_cache(maxsize=1)
def load_causal_model():

    if not os.path.exists(DATA_PATH):

        raise FileNotFoundError(
            f"DML training data not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    X, W, T, Y = _prepare_training_data(df)

    model_y = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model_t = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model = CausalForestDML(
        model_y=model_y,
        model_t=model_t,
        discrete_treatment=True,
        random_state=42
    )

    model.fit(
        Y,
        T,
        X=X,
        W=W
    )

    return model


@lru_cache(maxsize=1)
def load_preprocessors():

    if not os.path.exists(SCALER_PATH):

        raise FileNotFoundError(
            f"Feature scaler not found: {SCALER_PATH}"
        )

    if not os.path.exists(ENCODER_PATH):

        raise FileNotFoundError(
            f"Channel encoder not found: {ENCODER_PATH}"
        )

    scaler = joblib.load(
        SCALER_PATH
    )

    encoder = joblib.load(
        ENCODER_PATH
    )

    return scaler, encoder


def prepare_customer_features(customers):

    df = pd.DataFrame(customers)

    missing = [
        col
        for col in X_FEATURES
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    X_raw = df[X_FEATURES].copy()

    for col in X_FEATURES:

        X_raw[col] = pd.to_numeric(
            X_raw[col],
            errors="coerce"
        )

    if X_raw.isnull().any().any():

        invalid_columns = (
            X_raw.columns[
                X_raw.isnull().any()
            ].tolist()
        )

        raise ValueError(
            f"Invalid numeric values in columns: "
            f"{invalid_columns}"
        )

    scaler, _ = load_preprocessors()

    X_scaled = scaler.transform(
        X_raw
    )

    X = pd.DataFrame(
        X_scaled,
        columns=X_FEATURES,
        index=X_raw.index
    )

    return X


def predict_ite(customers):

    X = prepare_customer_features(
        customers
    )

    model = load_causal_model()

    ite = np.asarray(
        model.effect(X),
        dtype=float
    )

    return ite.tolist()


def analyze_dataset(rows):

    df = pd.DataFrame(rows)

    missing = [
        col
        for col in RAW_REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Dataset missing required columns: {missing}"
        )

    if df.empty:

        raise ValueError(
            "Dataset contains no rows."
        )

    if df["customer_id"].isna().any():

        raise ValueError(
            "customer_id contains missing values."
        )

    if df["customer_id"].duplicated().any():

        raise ValueError(
            "customer_id must be unique for each uploaded row."
        )

    clean = df.copy()

    clean["customer_id"] = pd.to_numeric(
        clean["customer_id"],
        errors="coerce"
    )

    if clean["customer_id"].isna().any():

        raise ValueError(
            "customer_id must contain numeric values."
        )

    for col in X_FEATURES + [
        "discount",
        "purchase"
    ]:

        clean[col] = pd.to_numeric(
            clean[col],
            errors="coerce"
        )

        if clean[col].isna().any():

            raise ValueError(
                f"Column '{col}' contains invalid numeric values."
            )

    clean["channel"] = (
        clean["channel"]
        .astype(str)
        .str.strip()
    )

    allowed_channels = {
        "in_store",
        "online"
    }

    invalid_channels = sorted(
        set(clean["channel"])
        - allowed_channels
    )

    if invalid_channels:

        raise ValueError(
            "channel contains unsupported values: "
            f"{invalid_channels}. "
            "Allowed values are: in_store, online."
        )

    T = (
        clean["discount"] > 0
    ).astype(int)

    if T.nunique() < 2:

        raise ValueError(
            "Uploaded data must contain both treated "
            "(discount > 0) and control "
            "(discount = 0) customers for Qini analysis."
        )

    ite = np.asarray(
        predict_ite(
            clean.to_dict(
                orient="records"
            )
        ),
        dtype=float
    )

    clean["treatment"] = T

    clean["ITE"] = ite

    clean["segment"] = np.select(
        [
            clean["ITE"] > 0.10,
            clean["ITE"] > 0
        ],
        [
            "Highly Persuadable",
            "Persuadable"
        ],
        default="Not Persuadable"
    )

    return clean