from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def sample_rows():

    return [

        {

            "customer_id": 1053,

            "age": 41,

            "income": 28100,

            "previous_purchases": 2,

            "campaign_response": 0.106,

            "customer_tenure_days": 82,

            "channel": "in_store",

            "avg_basket_size": 18.61,

            "discount": 15,

            "purchase": 0

        },

        {

            "customer_id": 2991,

            "age": 48,

            "income": 53100,

            "previous_purchases": 5,

            "campaign_response": 0.206,

            "customer_tenure_days": 483,

            "channel": "in_store",

            "avg_basket_size": 44.66,

            "discount": 0,

            "purchase": 0

        }

    ]


def test_optimize_endpoint():

    response = client.post(

        "/optimize",

        json={
            "total_budget": 5000
        }

    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    assert (
        data["optimization"]["budget"]
        == 5000
    )


def test_dataset_upload_missing_columns():

    response = client.post(

        "/dataset/upload",

        json={

            "file_name":
                "bad.csv",

            "data": [

                {
                    "customer_id": 1
                }

            ]

        }

    )

    assert (
        response.status_code
        == 400
    )


def test_dataset_requires_control_and_treatment():

    rows = sample_rows()

    rows[1]["discount"] = 10

    response = client.post(

        "/dataset/upload",

        json={

            "file_name":
                "sample.csv",

            "data":
                rows

        }

    )

    assert (
        response.status_code
        == 400
    )