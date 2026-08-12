
import pandas as pd
from dowhy import CausalModel

data = pd.read_csv("data/mock_retail_data.csv")

model = CausalModel(
    data=data,
    treatment="discount",
    outcome="purchase",
    graph="""
    digraph {
        age -> discount;
        age -> purchase;

        income -> discount;
        income -> purchase;

        previous_purchases -> discount;
        previous_purchases -> purchase;

        loyalty_score -> discount;
        loyalty_score -> purchase;

        discount -> purchase;
    }
    """
)

identified_estimand = model.identify_effect()

print(identified_estimand)