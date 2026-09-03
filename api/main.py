from fastapi import FastAPI
from api.schemas import PredictionRequest


app = FastAPI(
    title="EconoCausal API",
    description="REST API for causal effect prediction",
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
def predict(
    request: PredictionRequest
):

    return {
        "status": "received",
        "customers": len(request.customers),
        "message": "Prediction endpoint ready"
    }