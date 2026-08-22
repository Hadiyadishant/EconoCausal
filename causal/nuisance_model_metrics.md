# Nuisance Model Diagnostics — Week 2

These metrics check the internal Random Forest models used inside
CausalForestDML (the Y-model and T-model). They are diagnostic
checkpoints, not the final project output — the final output is the
ITE distribution, confidence intervals, and the Qini/Uplift curve.

## Outcome model (Random Forest Regressor)
- RMSE on held-out test set: 0.5097

## Treatment model (Random Forest Classifier)
- Accuracy on held-out test set: 0.5810

## ITE summary
- Mean ITE: 0.0407
- Std ITE: 0.0737
- Average Treatment Effect (ATE): 0.0407
- % customers with positive ITE: 71.14%

## Status
Model trained successfully. ite_score.csv exported with confidence
intervals for Princy's Qini/Uplift curve computation.
