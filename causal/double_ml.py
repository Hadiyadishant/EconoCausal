import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from econml.dml import CausalForestDML

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