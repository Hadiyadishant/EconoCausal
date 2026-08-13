import os
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from dowhy import CausalModel


# Load dataset
DATA_PATH = "data/mockretaildatacleaned.csv"

df = pd.read_csv(DATA_PATH)


# Causal variables
TREATMENT = "discount"
OUTCOME = "purchase"
IDENTIFIER = "customer_id"

CONFOUNDERS = [
    "age",
    "income",
    "previous_purchases",
    "campaign_response",
    "customer_tenure_days",
    "channel",
    "avg_basket_size"
]


# Dataset information
print("\nDataset Information")
print(f"Rows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nColumns:")
print(list(df.columns))


# Validate required columns
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

print(f"\nTreatment : {TREATMENT}")
print(f"Outcome   : {OUTCOME}")
print(f"Identifier: {IDENTIFIER}")

print("\nConfounders:")
for variable in CONFOUNDERS:
    print(f"- {variable}")


# Treatment and outcome values
print("\nDiscount values:")
print(sorted(df[TREATMENT].unique()))

print("\nPurchase values:")
print(sorted(df[OUTCOME].unique()))


# Define causal DAG
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


# Create DoWhy causal model
model = CausalModel(
    data=df,
    treatment=TREATMENT,
    outcome=OUTCOME,
    graph=graph
)

print("\nDAG successfully created and loaded into DoWhy.")


# Identify causal effect
print("\nIdentifying causal effect...")

identified_estimand = model.identify_effect(
    proceed_when_unidentifiable=True
)

print(identified_estimand)


# Create DAG for visualization
G = nx.DiGraph()

for confounder in CONFOUNDERS:
    G.add_edge(confounder, TREATMENT)
    G.add_edge(confounder, OUTCOME)

G.add_edge(TREATMENT, OUTCOME)


# DAG layout
pos = {
    "age": (-3, 3),
    "income": (-2, 3),
    "previous_purchases": (-1, 3),
    "campaign_response": (0, 3),
    "customer_tenure_days": (1, 3),
    "channel": (2, 3),
    "avg_basket_size": (3, 3),

    "discount": (0, 1),
    "purchase": (0, -1)
}


# Draw DAG
plt.figure(figsize=(14, 8))

nx.draw_networkx(
    G,
    pos=pos,
    with_labels=True,
    node_size=4000,
    node_color="white",
    edgecolors="black",
    arrows=True,
    arrowsize=20,
    font_size=9,
    font_weight="bold",
    linewidths=1.2
)

plt.title(
    "EconoCausal - Causal DAG",
    fontsize=16,
    fontweight="bold"
)

plt.axis("off")
plt.tight_layout()


# Save DAG as JPG
output_path = os.path.join(
    os.path.dirname(__file__),
    "dag_graph.jpg"
)

plt.savefig(
    output_path,
    format="jpg",
    dpi=300,
    bbox_inches="tight"
)

print(f"\nDAG graph saved successfully:")
print(output_path)

plt.show()


# Business question
print("\nBusiness Question:")
print(
    "What is the causal effect of giving a customer "
    "a discount on their probability of purchasing?"
)
