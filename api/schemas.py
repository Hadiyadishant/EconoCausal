from typing import Any, Dict, List

from pydantic import BaseModel, Field


class CustomerInput(BaseModel):

    age: float
    income: float
    previous_purchases: float
    campaign_response: float
    customer_tenure_days: float
    avg_basket_size: float


class PredictionRequest(BaseModel):

    customers: List[
        CustomerInput
    ] = Field(
        min_length=1
    )


class DriftRequest(BaseModel):

    data: List[
        Dict[str, Any]
    ] = Field(
        min_length=1
    )


class DatasetUploadRequest(BaseModel):

    file_name: str = Field(
        min_length=1
    )

    data: List[
        Dict[str, Any]
    ] = Field(
        min_length=1
    )


class BudgetRequest(BaseModel):

    total_budget: float = Field(
        gt=0
    )

    max_customers: int | None = Field(
        default=None,
        gt=0
    )


class PredictionResult(BaseModel):

    customer_index: int
    ite: float


class PredictionResponse(BaseModel):

    status: str
    customers: int
    predictions: List[
        PredictionResult
    ]