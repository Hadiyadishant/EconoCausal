# Causal Engine Information

## Model
CausalForestDML

## Treatment
discount > 0 = 1
discount = 0 = 0

## Customer Features
- age
- income
- previous_purchases
- campaign_response
- customer_tenure_days
- avg_basket_size

## Confounder
- channel

## Prediction
The model estimates Individual Treatment Effect (ITE).

## API Goal
Receive new customer data and return the estimated causal effect.