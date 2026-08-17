import os
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from econml.dml import CausalForestDML


# Load data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "mockretaildatacleaned.csv"
)

df = pd.read_csv(DATA_PATH)


# Treatment
# 0 = No discount
# 1 = Discount
T = (df["discount"] > 0).astype(int)


# Outcome
Y = df["purchase"]


# Features
features = [
    "age",
    "income",
    "previous_purchases",
    "campaign_response",
    "customer_tenure_days",
    "channel",
    "avg_basket_size"
]

X = df[features].copy()


# Convert categorical channel to numeric
X = pd.get_dummies(
    X,
    columns=["channel"],
    drop_first=True
)


# Random Forest models
model_y = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model_t = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)


# EconML Double ML model
dml_model = CausalForestDML(
    model_y=model_y,
    model_t=model_t,
    discrete_treatment=True,
    random_state=42
)


# Train model
print("Training Double ML model...")

dml_model.fit(
    Y,
    T,
    X=X
)

print("Double ML training completed successfully.")


# Estimate Individual Treatment Effect
ite = dml_model.effect(X)


print("\nITE Validation")

print("Number of ITE values:", len(ite))
print("Missing ITE values:", np.isnan(ite).sum())

print("Mean ITE:", ite.mean())
print("Std ITE:", ite.std())
print("Minimum ITE:", ite.min())
print("Maximum ITE:", ite.max())

print("\nPositive ITE customers:", (ite > 0).sum())
print(
    "Positive ITE percentage:",
    (ite > 0).mean() * 100
)

print("\nITE estimated successfully.")
