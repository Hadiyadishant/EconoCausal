import os
import pandas as pd
from functools import lru_cache

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from econml.dml import CausalForestDML


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "notebooks",
    "dml_ready_data.csv"
)


X_FEATURES = [
    "age",
    "income",
    "previous_purchases",
    "campaign_response",
    "customer_tenure_days",
    "avg_basket_size"
]


@lru_cache(maxsize=1)
def load_causal_model():

    df = pd.read_csv(DATA_PATH)

    T = (df["discount"] > 0).astype(int)
    Y = df["purchase"]

    X = df[X_FEATURES].copy()

    W = df[["channel_online"]].copy()

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


def predict_ite(customers):

    df = pd.DataFrame(customers)

    missing = [
        col for col in X_FEATURES
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    X = df[X_FEATURES].copy()

    model = load_causal_model()

    ite = model.effect(X)

    return ite.tolist()