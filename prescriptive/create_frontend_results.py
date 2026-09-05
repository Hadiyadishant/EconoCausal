import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "optimized_discount_assignments.csv"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "frontend",
    "public",
    "data",
    "optimization_results.json"
)

BUDGET = 5000.0

df = pd.read_csv(INPUT_PATH)

required = [
    "customer_id",
    "optimal_discount",
    "discount_fraction",
    "predicted_revenue",
    "marketing_cost"
]

missing = [c for c in required if c not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

result = {
    "customers": int(len(df)),
    "customers_allocated": int(
        (df["optimal_discount"] > 0).sum()
    ),
    "predicted_revenue": float(
        df["predicted_revenue"].sum()
    ),
    "marketing_cost": float(
        df["marketing_cost"].sum()
    ),
    "budget": BUDGET,
    "budget_remaining": float(
        BUDGET - df["marketing_cost"].sum()
    ),
    "allocations": df[
        required
    ].to_dict(orient="records")
}

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True
)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print("Frontend optimization results created.")
print(f"Customers: {result['customers']}")
print(f"Customers allocated: {result['customers_allocated']}")
print(f"Revenue: ₹{result['predicted_revenue']:.2f}")
print(f"Marketing cost: ₹{result['marketing_cost']:.2f}")
print(f"Budget remaining: ₹{result['budget_remaining']:.2f}")
print(f"Saved to: {OUTPUT_PATH}")