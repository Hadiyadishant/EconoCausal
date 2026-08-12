# Data Dictionary

Rows: 5,010 (5,000 unique customers + 10 intentionally injected duplicate rows)
Purpose: Mock retail discount campaign dataset for causal graphing (DoWhy) and later Double ML / ITE estimation (EconML).

# Column Reference

| Column | Type | Range / Values | Description | Causal Role |
|---|---|---|---|---|
| customer_id | int | 1–5000 | Unique identifier for a customer. Not unique across rows because 10 duplicate rows were intentionally injected (see Data Quality Notes). | Identifier (not used in modeling) |
| age | int | 18–80 | Customer age in years. | Confounder |
| income | float | ~15,000–200,000 | Estimated annual income (USD), rounded to nearest 100. Contains missing values (see below). | Confounder |
| previous_purchases | int | 0–40 | Count of purchases the customer made prior to this campaign. | Confounder |
| campaign_response | float | 0.0–1.0 | Historical propensity score: how responsive this customer has been to past marketing campaigns. Contains missing values (see below). | Confounder |
| customer_tenure_days | int | 1–4000 | Number of days the person has been a customer. Correlated with previous_purchases but a distinct loyalty/recency signal. | Confounder |
| channel | string | {online, in_store} | Channel the customer is primarily associated with. Categorical confounder — online-channel and more responsive customers skew slightly toward getting discounts. | Confounder |
| avg_basket_size | float | ~5–300 | Average dollar amount per past basket/order. Distinct economic signal from income. Contains missing values (see below). | Confounder |
| discount | int | {0, 5, 10, 15, 20, 25, 30} | Discount percentage offered to the customer in this campaign. 0 = no discount offered. | Treatment |
| purchase | int | {0, 1} | Whether the customer purchased after the campaign (1 = yes, 0 = no). | Outcome |

# Why These Are Confounders (not just features)

age, income, previous_purchases, campaign_response, customer_tenure_days,
channel, and avg_basket_size were generated so that they influence both:
1. The probability and size of the discount a customer received (marketing historically
   targets higher-income, more purchase-active, more responsive customers with bigger
   discounts), 
2. The probability of purchase (these same traits independently make someone more likely
   to buy, discount or not).

This is intentional, deliberate confounding — it mimics real-world marketing data, which is
observational, not a randomized experiment. A naive model that regresses purchase on
discount without adjusting for these variables will overstate the effect of the discount,
because it partly just picks up "high-value customers get bigger discounts AND buy more
anyway." This is exactly the gap that Double Machine Learning (Week 2+) is designed to close.

There is also a genuine (simulated) causal effect of discount on purchase baked into the
data-generating process — larger discounts do increase purchase probability, and the effect
is heterogeneous (stronger for lower-income customers). This gives the team real signal to
recover in later weeks.

# Data Quality Notes (intentional, for the validation task)

- Missing values: income has ~1% missing (50 rows), campaign_response has ~0.5%
  missing (25 rows), avg_basket_size has ~0.5% missing (25 rows).
- Duplicates: 10 fully duplicated rows (including customer_id) were injected on top of
  the 5,000 unique customers, bringing the total to 5,010 rows.
- No invalid values: age is bounded to [18, 80], discount only takes the 7 defined
  values, purchase is strictly binary — these were validated after generation.

# Overlap / Positivity

For causal identification to work, every type of customer needs a realistic chance of
appearing in both the treated (discount > 0) and untreated (discount = 0) groups — this
is called overlap or positivity. The data was generated so that even high-propensity
customers (high income, high tenure, online channel) still have a meaningful chance of
receiving no discount, and low-propensity customers still sometimes get one. This was
checked by bucketing each confounder and confirming both
groups are represented in every bucket. Without this, DoWhy/EconML would have no way to
estimate a treatment effect for the buckets that are all-treated or all-untreated.