import os
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from econml.dml import CausalForestDML


# =========================================================
# PATHS
# =========================================================

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


# =========================================================
# FEATURES
# =========================================================

X_FEATURES = [
    "age",
    "income",
    "previous_purchases",
    "campaign_response",
    "customer_tenure_days",
    "avg_basket_size",
]

RAW_REQUIRED_COLUMNS = [
    "customer_id",
    *X_FEATURES,
    "discount",
    "purchase",
    "channel",
]


# =========================================================
# TRAINING DATA PREPARATION
# =========================================================

def _prepare_training_data(df):

    required_columns = [
        *X_FEATURES,
        "discount",
        "purchase",
        "channel_online",
    ]

    missing = [
        col
        for col in required_columns
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

    Y = pd.to_numeric(
        df["purchase"],
        errors="coerce"
    )

    if Y.isna().any():
        raise ValueError(
            "Training outcome 'purchase' contains invalid values."
        )

    return X, W, T, Y


# =========================================================
# LOAD / TRAIN CAUSAL MODEL
# =========================================================

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
        random_state=42,
        n_jobs=-1
    )

    model_t = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
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


# =========================================================
# LOAD PREPROCESSORS
# =========================================================

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


# =========================================================
# CUSTOMER FEATURE PREPARATION
# =========================================================

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
            "Invalid numeric values in columns: "
            f"{invalid_columns}"
        )

    scaler, _ = load_preprocessors()

    # IMPORTANT:
    # The CausalForest was trained using the standardized
    # features from dml_ready_data.csv.
    X_scaled = scaler.transform(
        X_raw
    )

    X = pd.DataFrame(
        X_scaled,
        columns=X_FEATURES,
        index=X_raw.index
    )

    return X


# =========================================================
# ITE PREDICTION
# =========================================================

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


# =========================================================
# COMPLETE DATASET ANALYSIS
# =========================================================

def analyze_dataset(rows):

    df = pd.DataFrame(rows)

    if df.empty:
        raise ValueError(
            "Dataset contains no rows."
        )

    missing = [
        col
        for col in RAW_REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Dataset missing required columns: {missing}"
        )

    clean = df.copy()

    # -----------------------------------------------------
    # CUSTOMER ID
    # -----------------------------------------------------

    clean["customer_id"] = pd.to_numeric(
        clean["customer_id"],
        errors="coerce"
    )

    if clean["customer_id"].isna().any():
        raise ValueError(
            "customer_id must contain numeric values."
        )

    if clean["customer_id"].duplicated().any():
        raise ValueError(
            "customer_id must be unique for each uploaded row."
        )

    # -----------------------------------------------------
    # NUMERIC COLUMNS
    # -----------------------------------------------------

    numeric_columns = [
        *X_FEATURES,
        "discount",
        "purchase",
    ]

    for col in numeric_columns:

        clean[col] = pd.to_numeric(
            clean[col],
            errors="coerce"
        )

        if clean[col].isna().any():

            raise ValueError(
                f"Column '{col}' contains invalid numeric values."
            )

    # -----------------------------------------------------
    # CHANNEL
    # -----------------------------------------------------

    clean["channel"] = (
        clean["channel"]
        .astype(str)
        .str.strip()
    )

    allowed_channels = {
        "in_store",
        "online",
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

    # -----------------------------------------------------
    # TREATMENT
    # -----------------------------------------------------

    T = (
        clean["discount"] > 0
    ).astype(int)

    if T.nunique() < 2:

        raise ValueError(
            "Uploaded data must contain both treated "
            "(discount > 0) and control "
            "(discount = 0) customers."
        )

    # -----------------------------------------------------
    # ITE
    # -----------------------------------------------------

    ite = np.asarray(
        predict_ite(
            clean.to_dict(
                orient="records"
            )
        ),
        dtype=float
    )

    if len(ite) != len(clean):
        raise ValueError(
            "ITE prediction count does not match dataset rows."
        )

    clean["treatment"] = T

    clean["ITE"] = ite

    # -----------------------------------------------------
    # SEGMENTATION
    # -----------------------------------------------------

    clean["segment"] = np.select(
        [
            clean["ITE"] > 0.10,
            clean["ITE"] > 0,
        ],
        [
            "Highly Persuadable",
            "Persuadable",
        ],
        default="Not Persuadable"
    )

    return clean