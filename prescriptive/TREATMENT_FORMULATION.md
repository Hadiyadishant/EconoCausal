# Treatment Formulation

## Week 2 Treatment Representation

The Week 2 causal model represents treatment as a binary variable:

- T = 0 → No discount
- T = 1 → Customer received a discount

The original dataset contains multiple discount levels:

0%, 5%, 10%, 15%, 20%, 25%, 30%.

For the Week 2 Double Machine Learning model, these levels were converted into:

```text
discount = 0 → T = 0
discount > 0 → T = 1