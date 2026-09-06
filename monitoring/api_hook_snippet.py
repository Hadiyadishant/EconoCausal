"""
api_hook_snippet.py
====================
EconoCausal — Data Drift & Monitoring (Day 7)

This file is NOT meant to be run on its own. It shows Dishant EXACTLY what
to add to his real api/main.py so the /predict endpoint returns both the
causal engine's prediction AND the drift status in one response.

Integration diagram (per the team's connection design):

    New customer data -> Dishant's API validation -> causal engine prediction
        -> Princy's drift check -> drift score/warning -> combined API response
"""

# ---------------------------------------------------------------------------
# STEP 1 — add these two imports near the top of api/main.py
# (pandas is needed to turn the customer list into a DataFrame for check_drift)
# ---------------------------------------------------------------------------
#
#   import pandas as pd
#   from monitoring.drift_detector import check_drift
#
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# STEP 2 — inside the /predict endpoint, right after:
#
#   ite = predict_ite(customers)
#
# add these two lines:
#
#   new_df = pd.DataFrame(customers)
#   drift_result = check_drift(new_df)
#
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# STEP 3 — inside the success return dict, add these 3 keys alongside the
# existing "status", "customers", and "predictions" keys:
#
#   "drift_status": drift_result["overall_status"],
#   "drift_details": drift_result["per_variable"],
#   "drift_threshold": drift_result["threshold"]
#
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# FULL BEFORE / AFTER REFERENCE (based on Dishant's actual main.py)
# ---------------------------------------------------------------------------

# --- BEFORE (Dishant's current /predict) -----------------------------------
"""
@app.post("/predict")
def predict(request: PredictionRequest):

    try:

        customers = [
            customer.model_dump()
            for customer in request.customers
        ]

        ite = predict_ite(customers)

        return {
            "status": "success",
            "customers": len(customers),
            "predictions": [
                {
                    "customer_index": i,
                    "ite": value
                }
                for i, value in enumerate(ite)
            ]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
"""

# --- AFTER (with drift check added) -----------------------------------------
"""
@app.post("/predict")
def predict(request: PredictionRequest):

    try:

        customers = [
            customer.model_dump()
            for customer in request.customers
        ]

        ite = predict_ite(customers)

        # Princy's drift check — runs the new customer data against the
        # baseline reference and returns overall status + per-variable detail.
        new_df = pd.DataFrame(customers)
        drift_result = check_drift(new_df)

        return {
            "status": "success",
            "customers": len(customers),
            "predictions": [
                {
                    "customer_index": i,
                    "ite": value
                }
                for i, value in enumerate(ite)
            ],
            "drift_status": drift_result["overall_status"],
            "drift_details": drift_result["per_variable"],
            "drift_threshold": drift_result["threshold"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
"""
