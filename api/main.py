from fastapi import FastAPI, HTTPException

from api.schemas import PredictionRequest
from api.causal_engine import predict_ite


app = FastAPI(
    title="EconoCausal API",
    version="1.0.0"
)


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

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )