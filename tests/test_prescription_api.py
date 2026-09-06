from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_prescription_api():

    response = client.get(
        "/prescription"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "count" in data
    assert "prescriptions" in data


def test_single_customer_prescription():

    response = client.get(
        "/prescription?customer_id=1053"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "prescriptions" in data