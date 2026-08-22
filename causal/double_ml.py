import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from econml.dml import CausalForestDML

try:
    from sklearn.metrics import root_mean_squared_error
    HAS_RMSE_FUNC = True
except ImportError:
    from sklearn.metrics import mean_squared_error
    HAS_RMSE_FUNC = False


# 1. LOAD DATA

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "notebooks",
    "dml_ready_data.csv"
)

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully.")
print("Dataset shape:", df.shape)


# 2. DEFINE TREATMENT (T)

# Binary treatment:
# 0 = No discount
# 1 = Any discount

T = (df["discount"] > 0).astype(int)

print("\nTreatment Distribution:")
print(T.value_counts())


# 3. DEFINE OUTCOME (Y)

# Binary purchase outcome
Y = df["purchase"]


# 4. DEFINE CONFOUNDERS (X)

# X = Customer-level confounders
X_features = [
    "age",
    "income",
    "previous_purchases",
    "campaign_response",
    "customer_tenure_days",
    "avg_basket_size"
]

X = df[X_features].copy()

print("\nX Shape:", X.shape)


# 5. DEFINE ADDITIONAL CONTROL VARIABLES (W)

# W = Channel
# Categorical variable:
# in_store / online

W = df[["channel_online"]].copy()

# Convert categorical channel to numeric
W = pd.get_dummies(
    W,
    columns=["channel_online"],
    drop_first=True
)

print("W Shape:", W.shape)


# 6. DEFINE MACHINE LEARNING MODELS

# Model for predicting the outcome Y
model_y = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

# Model for predicting the treatment T
model_t = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)


# 6B. NUISANCE MODEL DIAGNOSTICS

# These checks are separate from the final CausalForestDML fit below.
# They exist only to sanity-check that the Y-model and T-model are
# reasonably good BEFORE trusting the causal (ITE) estimates that
# depend on them. This is not the final project output.

print("\n" + "=" * 50)
print("NUISANCE MODEL DIAGNOSTICS")
print("=" * 50)

XW = pd.concat([X, W], axis=1)

XW_train, XW_test, Y_train, Y_test, T_train, T_test = train_test_split(
    XW, Y, T, test_size=0.2, random_state=42
)

# Outcome model diagnostic (Random Forest Regressor)
diag_model_y = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)
diag_model_y.fit(XW_train, Y_train)
y_pred = diag_model_y.predict(XW_test)

if HAS_RMSE_FUNC:
    rmse = root_mean_squared_error(Y_test, y_pred)
else:
    rmse = mean_squared_error(Y_test, y_pred, squared=False)

print("Y-model RMSE (held-out test set):", rmse)

# Treatment model diagnostic (Random Forest Classifier)
diag_model_t = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)
diag_model_t.fit(XW_train, T_train)
t_pred = diag_model_t.predict(XW_test)
t_accuracy = accuracy_score(T_test, t_pred)

print("T-model Accuracy (held-out test set):", t_accuracy)

if rmse > 0.4:
    print("WARNING: Y-model RMSE looks high — review features/model before trusting ITE.")
if t_accuracy < 0.55:
    print("WARNING: T-model accuracy is close to random — review features/model before trusting ITE.")


# 7. CREATE CAUSAL FOREST DML MODEL

dml_model = CausalForestDML(
    model_y=model_y,
    model_t=model_t,
    discrete_treatment=True,
    random_state=42
)


# 8. TRAIN CAUSAL FOREST DML MODEL

print("\nTraining Causal Forest DML model...")

dml_model.fit(
    Y,
    T,
    X=X,
    W=W
)

print("Causal Forest DML training completed successfully.")

# 9. ESTIMATE INDIVIDUAL TREATMENT EFFECT (ITE)

ite = dml_model.effect(X)

print("\nITE estimated successfully.")


# 9B. ITE CONFIDENCE INTERVALS

# Point estimates alone don't show how confident the model is.
# These bounds show whether the effect for each customer is
# reliably different from zero, or could just be noise.

ite_lower, ite_upper = dml_model.effect_interval(X, alpha=0.05)

print("\n95% Confidence Interval — sample (first 5 customers):")
for i in range(5):
    print(f"  Customer {i}: ITE = {ite[i]:.4f}  [{ite_lower[i]:.4f}, {ite_upper[i]:.4f}]")


# 10. ITE VALIDATION

print("\n" + "=" * 50)
print("ITE VALIDATION")
print("=" * 50)

print("Number of ITE values:", len(ite))
print("Missing ITE values:", np.isnan(ite).sum())

print("Mean ITE:", ite.mean())
print("Std ITE:", ite.std())
print("Minimum ITE:", ite.min())
print("Maximum ITE:", ite.max())


# Count ITE categories
positive_ite = (ite > 0).sum()
negative_ite = (ite < 0).sum()
zero_ite = (ite == 0).sum()

print("\nPositive ITE customers:", positive_ite)
print("Negative ITE customers:", negative_ite)
print("Zero ITE customers:", zero_ite)

print(
    "Positive ITE percentage:",
    (ite > 0).mean() * 100
)

print(
    "Negative ITE percentage:",
    (ite < 0).mean() * 100
)


# 11. CALCULATE AVERAGE TREATMENT EFFECT (ATE)

ate = dml_model.ate(X)

print("\n" + "=" * 50)
print("AVERAGE TREATMENT EFFECT (ATE)")
print("=" * 50)

print("Average Treatment Effect:", ate)


# 12. CREATE ITE RESULTS DATAFRAME


results = df.copy()

results["treatment"] = T
results["ITE"] = ite
results["ITE_lower"] = ite_lower
results["ITE_upper"] = ite_upper


# 13. CUSTOMER SEGMENTATION

results["segment"] = np.select(
    [
        results["ITE"] > 0.10,
        results["ITE"] > 0
    ],
    [
        "Highly Persuadable",
        "Persuadable"
    ],
    default="Not Persuadable"
)


# 14. CUSTOMER SEGMENT ANALYSIS

print("\n" + "=" * 50)
print("CUSTOMER SEGMENTS")
print("=" * 50)

print(
    results["segment"].value_counts()
)


# 15. TOP CUSTOMERS BY ITE

top_customers = results.sort_values(
    "ITE",
    ascending=False
)

print("\n" + "=" * 50)
print("TOP 20 CUSTOMERS BY ITE")
print("=" * 50)

print(
    top_customers[
        [
            "age",
            "income",
            "previous_purchases",
            "discount",
            "purchase",
            "ITE",
            "ITE_lower",
            "ITE_upper",
            "segment"
        ]
    ].head(20)
)


# 16. ITE DISTRIBUTION

plt.figure(figsize=(8, 5))

plt.hist(
    ite,
    bins=30
)

plt.axvline(
    0,
    linestyle="--"
)

plt.xlabel("Individual Treatment Effect")
plt.ylabel("Number of Customers")
plt.title("Distribution of Individual Treatment Effects")

# Save graph as JPG
GRAPH_PATH = os.path.join(
    BASE_DIR,
    "data",
    "ite_distribution.jpg"
)

plt.savefig(
    GRAPH_PATH,
    format="jpg",
    dpi=300,
    bbox_inches="tight"
)

print("\nITE distribution graph saved successfully.")
print("Graph:", GRAPH_PATH)
plt.show()

plt.close()


# 17. SAVE ITE RESULTS

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "ite_score.csv"
)

results.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n" + "=" * 50)
print("RESULT SAVING")
print("=" * 50)

print("ITE results saved successfully.")
print("Output:", OUTPUT_PATH)


# 18. SAVE NUISANCE MODEL DIAGNOSTICS

METRICS_PATH = os.path.join(
    BASE_DIR,
    "causal",
    "nuisance_model_metrics.md"
)

metrics_note = f"""# Nuisance Model Diagnostics — Week 2

These metrics check the internal Random Forest models used inside
CausalForestDML (the Y-model and T-model). They are diagnostic
checkpoints, not the final project output — the final output is the
ITE distribution, confidence intervals, and the Qini/Uplift curve.

## Outcome model (Random Forest Regressor)
- RMSE on held-out test set: {rmse:.4f}

## Treatment model (Random Forest Classifier)
- Accuracy on held-out test set: {t_accuracy:.4f}

## ITE summary
- Mean ITE: {ite.mean():.4f}
- Std ITE: {ite.std():.4f}
- Average Treatment Effect (ATE): {ate:.4f}
- % customers with positive ITE: {positive_ite / len(ite) * 100:.2f}%

## Status
Model trained successfully. ite_score.csv exported with confidence
intervals for Princy's Qini/Uplift curve computation.
"""

with open(METRICS_PATH, "w") as f:
    f.write(metrics_note)

print("Nuisance model diagnostics saved successfully.")
print("Output:", METRICS_PATH)
