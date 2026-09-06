
from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def load_test_customer():
    return {
        "age": 30,
        "income": 50000,
        "previous_purchases": 10,
        "customer_tenure_days": 300,
        "avg_basket_size": 250,
        "discount": 10,
        "campaign_response": 1,
        "channel": "online",
        "purchase": 1
    }


def test_drift_api_normal_data():

    customer = load_test_customer()

    response = client.post(
        "/drift",
        json={
            "data": [customer]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "drift" in data
    assert "overall_status" in data["drift"]
    assert "threshold" in data["drift"]
    assert "per_variable" in data["drift"]


def test_drift_api_empty_data():

    response = client.post(
        "/drift",
        json={
            "data": []
        }
    )

    assert response.status_code == 422
