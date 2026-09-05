from pydantic import BaseModel , Field
from typing import List


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


class PredictionResult(BaseModel):

    customer_index: int
    ite: float


class PredictionResponse(BaseModel):

    status: str
    customers: int
    predictions: List[PredictionResult]