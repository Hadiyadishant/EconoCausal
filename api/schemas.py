from typing import Any, List, Dict

from pydantic import BaseModel, Field


class CustomerInput(BaseModel):

    age: float
    income: float
    previous_purchases: float
    campaign_response: float
    customer_tenure_days: float
    avg_basket_size: float


class PredictionRequest(BaseModel):

    customers: List[CustomerInput] = Field(
        min_length=1
    )


class DriftRequest(BaseModel):

    data: List[Dict[str, Any]] = Field(
        min_length=1
    )


class PrescriptionRequest(BaseModel):

    customer_id: int | None = None


class PredictionResult(BaseModel):

    customer_index: int
    ite: float


class PredictionResponse(BaseModel):

    status: str
    customers: int
    predictions: List[PredictionResult]


class PrescriptionResult(BaseModel):

    customer_id: int
    optimal_discount: float
    discount_fraction: float
    predicted_revenue: float
    marketing_cost: float