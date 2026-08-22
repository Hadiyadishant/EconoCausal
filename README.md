Causal Analysis — Week 2
Business Question

What is the causal effect of a discount on a customer's probability of purchasing?

The dataset is observational, so customers receiving different discount levels may differ in other ways too (income, past purchases, etc.).
These differences can affect both the discount and the purchase outcome, creating confounding.
This notebook identifies those confounders and builds a causal model to isolate the true effect of discount on purchase.

DataSource:

 ../data/mockretaildatacleaned.csv

Shape: 5,000 rows × 10 columns, no missing values, no duplicates

Variable Roles:

customer_id:Identifier

discount:Treatment (T) — levels 0,5,10,15,20,25,30; representation not yet finalized

purchase:Outcome (Y)

age, income, previous_purchases, campaign_response, customer_tenure_days,avg_basket_size:Confounders (X)

channel:Confounder (W) — categorical, in_store/online

What This Does:

1.Defines treatment, outcome, identifier, and confounders.

2.Shows treatment isn't binary in the raw data (7 discount levels).

3.Builds the causal DAG and loads it into DoWhy.

4.Identifies the causal effect — valid backdoor/general-adjustment estimand using the 7 confounders.

5.Runs DML-readiness checks: column presence, missing values, dtypes, channel inspection.

6.Builds the feature matrix: one-hot encodes channel, scales numeric confounders.

7.Assembles final X (5000,7), T (5000,1), Y (5000,1).

8.Runs sanity checks (row match, no missing values, no leakage).

9.Exports dml_ready_data.csv for Double ML modeling.

Outputs:
	

column_roles.csv:Column role documentation

channel_encoder.pkl:Fitted OneHotEncoder for channel

confounder_scaler.pkl:Fitted StandardScaler for numeric confounders

dml_ready_data.csv:Final X/T/Y dataset (5000 × 10)


Key Assumption:

Unconfoundedness: after adjusting for the 7 confounders, no unobserved variable affects both discount and purchase.