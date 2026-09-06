from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from api.schemas import PredictionRequest, DriftRequest
from api.causal_engine import predict_ite
from api.prescription_service import get_prescription
from monitoring.drift_detector import check_drift


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="EconoCausal API",
    version="1.0.0"
)


# --------------------------------------------------
# CORS — required so the React dev server (a different
# origin, e.g. http://localhost:5173) is allowed to call
# this API from the browser. Without this every fetch from
# Prescription.jsx / DataMonitoring.jsx / Dashboard.jsx will
# fail with a CORS error even though the backend is running.
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Health / Home
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "EconoCausal API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# Causal Prediction API
# --------------------------------------------------

@app.post("/predict")
def predict(request: PredictionRequest):

    try:

        # Convert Pydantic customer objects
        # into dictionaries
        customers = [
            customer.model_dump()
            for customer in request.customers
        ]

        # Send customer data to causal engine
        ite = predict_ite(customers)

        # Return ITE predictions
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

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


# --------------------------------------------------
# Data Drift Detection API
# --------------------------------------------------

@app.post("/drift")
def detect_drift(request: DriftRequest):

    try:

        # Convert incoming JSON data
        # into a pandas DataFrame
        new_data = pd.DataFrame(request.data)

        # Check that required monitoring
        # columns are available
        required_columns = [
            "age",
            "income",
            "previous_purchases",
            "customer_tenure_days",
            "avg_basket_size",
            "discount",
            "campaign_response",
            "channel",
            "purchase"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in new_data.columns
        ]

        if missing_columns:

            raise HTTPException(
                status_code=400,
                detail=f"Missing required drift columns: {missing_columns}"
            )

        # Use Princy's existing drift detector
        result = check_drift(new_data)

        return {
            "status": "success",
            "drift": result
        }

    except HTTPException:
        raise

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Drift detection failed: {str(e)}"
        )


# --------------------------------------------------
# Prescription API
# --------------------------------------------------

@app.get("/prescription")
def prescription(customer_id: int | None = None):

    try:

        # Load final Week 3 optimization results
        result = get_prescription(customer_id)

        return {
            "status": "success",
            "count": len(result),
            "prescriptions": result
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Prescription retrieval failed: {str(e)}"
        )