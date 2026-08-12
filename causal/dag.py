
# import pandas as pd
# from dowhy import CausalModel

# data = pd.read_csv("data/mockretaildata.csv")

# model = CausalModel(
#     data=data,
#     treatment="discount",
#     outcome="purchase",
#     graph="""
#     digraph {
#         age -> discount;
#         age -> purchase;

#         income -> discount;
#         income -> purchase;

#         previous_purchases -> discount;
#         previous_purchases -> purchase;

#         loyalty_score -> discount;
#         loyalty_score -> purchase;

#         discount -> purchase;
#     }
#     """
# )

# identified_estimand = model.identify_effect()

# print(identified_estimand)

import pandas as pd
import dowhy
from dowhy import CausalModel


# ============================================================
# 1. Load Dataset
# ============================================================

DATA_PATH = "data/mockretaildata.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 2. Define Causal Variables
# ============================================================

# Treatment:
# Discount offered to the customer.
TREATMENT = "discount"

# Outcome:
# Whether the customer purchased after the campaign.
OUTCOME = "purchase"

# Confounders:
# These variables influence both discount assignment
# and customer purchase behavior.
CONFOUNDERS = [
    "age",
    "income",
    "previous_purchases",
    "campaign_response",
    "customer_tenure_days",
    "channel",
    "avg_basket_size",
]

# Customer ID is only an identifier.
# It should NOT be used as a causal variable.
IDENTIFIER = "customer_id"


# ============================================================
# 3. Validate Required Columns
# ============================================================

required_columns = (
    [IDENTIFIER, TREATMENT, OUTCOME]
    + CONFOUNDERS
)

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("\nAll required columns are present.")


# ============================================================
# 4. Display Causal Roles
# ============================================================

print("\n" + "=" * 60)
print("CAUSAL VARIABLE ROLES")
print("=" * 60)

print(f"Treatment : {TREATMENT}")
print(f"Outcome   : {OUTCOME}")
print(f"Identifier: {IDENTIFIER}")

print("\nConfounders:")

for variable in CONFOUNDERS:
    print(f"  - {variable}")


# ============================================================
# 5. Check Missing Values
# ============================================================

print("\n" + "=" * 60)
print("MISSING VALUE CHECK")
print("=" * 60)

missing_values = df[required_columns].isnull().sum()

print(missing_values)

print("\nRows containing missing values:")

rows_with_missing = df[required_columns].isnull().any(axis=1).sum()

print(rows_with_missing)


# ============================================================
# 6. Remove Missing Values for Week 1 Causal Analysis
# ============================================================

df_clean = df.dropna(
    subset=[TREATMENT, OUTCOME] + CONFOUNDERS
).copy()

print("\n" + "=" * 60)
print("CLEAN DATASET")
print("=" * 60)

print(f"Original rows : {len(df)}")
print(f"Clean rows    : {len(df_clean)}")
print(f"Removed rows  : {len(df) - len(df_clean)}")


# ============================================================
# 7. Check Treatment Values
# ============================================================

print("\n" + "=" * 60)
print("TREATMENT CHECK")
print("=" * 60)

print("Discount values:")

print(
    sorted(
        df_clean[TREATMENT].unique()
    )
)


# ============================================================
# 8. Check Outcome Values
# ============================================================

print("\n" + "=" * 60)
print("OUTCOME CHECK")
print("=" * 60)

print("Purchase values:")

print(
    sorted(
        df_clean[OUTCOME].unique()
    )
)


# ============================================================
# 9. Define the Causal DAG
# ============================================================

# Causal structure:
#
# Confounders ───────► Discount
#      │
#      └─────────────► Purchase
#
# Discount ──────────► Purchase
#
#
# Therefore:
#
# Confounders affect BOTH:
#   1. Discount assignment
#   2. Purchase
#
# This creates confounding.
#
# The main causal relationship we want to estimate is:
#
#              Discount
#                  │
#                  ▼
#              Purchase


graph = """
digraph {

    age -> discount;
    age -> purchase;

    income -> discount;
    income -> purchase;

    previous_purchases -> discount;
    previous_purchases -> purchase;

    campaign_response -> discount;
    campaign_response -> purchase;

    customer_tenure_days -> discount;
    customer_tenure_days -> purchase;

    channel -> discount;
    channel -> purchase;

    avg_basket_size -> discount;
    avg_basket_size -> purchase;

    discount -> purchase;
}
"""


# ============================================================
# 10. Create DoWhy Causal Model
# ============================================================

model = CausalModel(
    data=df_clean,
    treatment=TREATMENT,
    outcome=OUTCOME,
    graph=graph,
)


# ============================================================
# 11. Identify the Causal Effect
# ============================================================

print("\n" + "=" * 60)
print("IDENTIFYING CAUSAL EFFECT")
print("=" * 60)

identified_estimand = model.identify_effect(
    proceed_when_unidentifiable=True
)

print(identified_estimand)


# ============================================================
# 12. Final Summary
# ============================================================

print("\n" + "=" * 60)
print("WEEK 1 DAG SUMMARY")
print("=" * 60)

print("Business Question:")
print(
    "What is the causal effect of giving a customer "
    "a discount on their probability of purchasing?"
)

print("\nTreatment:")
print("discount")

print("\nOutcome:")
print("purchase")

print("\nConfounders:")

for variable in CONFOUNDERS:
    print(f"- {variable}")

print("\nDAG successfully created and loaded into DoWhy.")
