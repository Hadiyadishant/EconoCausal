from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_prediction():

    payload = {
        "customers": [
            {
                "age": 30,
                "income": 50000,
                "previous_purchases": 10,
                "campaign_response": 1,
                "customer_tenure_days": 300,
                "avg_basket_size": 250
            }
        ]
    }

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["customers"] == 1
    assert len(data["predictions"]) == 1


def test_invalid_request():

    response = client.post(
        "/predict",
        json={"customers": []}
    )

    assert response.status_code == 422