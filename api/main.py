import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

from fastapi import (
    FastAPI,
    HTTPException
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from api.causal_engine import (
    analyze_dataset,
    predict_ite
)

from api.optimization_service import (
    DATASET_PATH,
    DEFAULT_BUDGET,
    optimize
)

from api.prescription_service import (
    get_optimization_summary,
    get_prescription
)

from api.schemas import (
    BudgetRequest,
    DatasetUploadRequest,
    DriftRequest,
    PredictionRequest
)

from monitoring.drift_detector import (
    check_drift
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ANALYSIS_PATH = os.path.join(
    BASE_DIR,
    "data",
    "runtime_causal_analysis.json"
)

DATASET_META_PATH = os.path.join(
    BASE_DIR,
    "data",
    "runtime_dataset_meta.json"
)

BUDGET_PATH = os.path.join(
    BASE_DIR,
    "data",
    "runtime_budget.json"
)


app = FastAPI(
    title="EconoCausal API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


def _save_json(
    path,
    payload
):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as handle:

        json.dump(
            payload,
            handle,
            indent=2
        )


def _load_json(path):

    if not os.path.exists(
        path
    ):

        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as handle:

        return json.load(handle)


def _compute_qini(
    df,
    n_points=100
):

    ranked = (
        df.sort_values(
            "ITE",
            ascending=False
        )
        .reset_index(drop=True)
    )

    n = len(ranked)

    treated_total = int(
        (
            ranked[
                "treatment"
            ] > 0
        ).sum()
    )

    control_total = int(
        (
            ranked[
                "treatment"
            ] == 0
        ).sum()
    )

    fractions = []

    qini_values = []

    for fraction in np.linspace(
        0,
        1,
        n_points
    ):

        cutoff = int(
            np.ceil(
                fraction * n
            )
        )

        subset = ranked.iloc[
            :cutoff
        ]

        treated_sum = subset.loc[
            subset["treatment"] > 0,
            "purchase"
        ].sum()

        control_sum = subset.loc[
            subset["treatment"] == 0,
            "purchase"
        ].sum()

        if (
            treated_total > 0
            and control_total > 0
        ):

            qini = (
                treated_sum
                -
                control_sum
                *
                (
                    treated_total
                    /
                    control_total
                )
            )

        else:

            qini = 0.0

        fractions.append(
            float(fraction)
        )

        qini_values.append(
            float(qini)
        )

    random_baseline = (
        np.linspace(
            0,
            qini_values[-1],
            n_points
        )
        .tolist()
    )

    # Same definition as the Week 2
    # causal_analysis.ipynb:
    # mean ITE within each decile.

    ranked["decile"] = pd.qcut(
        ranked.index,
        10,
        labels=False,
        duplicates="drop"
    )

    uplift_curve = (
        ranked
        .groupby("decile")["ITE"]
        .mean()
    )

    uplift_by_decile = {
        str(int(index)):
            float(value)

        for index, value
        in uplift_curve.items()
    }

    return {

        "fractions":
            fractions,

        "qini_values":
            qini_values,

        "random_baseline":
            random_baseline,

        "uplift_by_decile":
            uplift_by_decile,

        "customers":
            n
    }


@app.get("/")
def home():

    return {
        "message":
            "EconoCausal API is running"
    }


@app.get("/health")
def health():

    return {
        "status":
            "healthy"
    }


@app.post("/predict")
def predict(
    request: PredictionRequest
):

    try:

        customers = [
            customer.model_dump()
            for customer
            in request.customers
        ]

        ite = predict_ite(
            customers
        )

        return {

            "status":
                "success",

            "customers":
                len(customers),

            "predictions": [

                {
                    "customer_index":
                        i,

                    "ite":
                        value
                }

                for i, value
                in enumerate(ite)
            ]
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=
                f"Prediction failed: "
                f"{str(exc)}"
        )


@app.post("/dataset/upload")
def upload_dataset(
    request: DatasetUploadRequest
):

    try:

        analyzed = analyze_dataset(
            request.data
        )

        os.makedirs(
            os.path.dirname(
                DATASET_PATH
            ),
            exist_ok=True
        )

        # Store the uploaded raw
        # customer dataset.

        analyzed.drop(
            columns=[
                "treatment",
                "ITE",
                "segment"
            ],
            errors="ignore"
        ).to_csv(
            DATASET_PATH,
            index=False
        )

        qini = _compute_qini(
            analyzed
        )

        analysis = {

            "status":
                "success",

            "file_name":
                request.file_name,

            "rows":
                int(len(analyzed)),

            "columns":
                analyzed.columns.tolist(),

            "positive_ite":
                int(
                    (
                        analyzed["ITE"]
                        > 0
                    ).sum()
                ),

            "negative_ite":
                int(
                    (
                        analyzed["ITE"]
                        < 0
                    ).sum()
                ),

            "mean_ite":
                float(
                    analyzed["ITE"].mean()
                ),

            "ate":
                float(
                    analyzed["ITE"].mean()
                ),

            "qini":
                qini,

            "segment_counts":
                analyzed[
                    "segment"
                ]
                .value_counts()
                .to_dict()
        }

        _save_json(
            ANALYSIS_PATH,
            analysis
        )

        _save_json(
            DATASET_META_PATH,
            {

                "file_name":
                    request.file_name,

                "rows":
                    int(
                        len(analyzed)
                    ),

                "columns":
                    analyzed.columns.tolist()
            }
        )

        return analysis

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=
                f"Dataset analysis failed: "
                f"{str(exc)}"
        )


@app.get("/dataset/status")
def dataset_status():

    analysis = _load_json(
        ANALYSIS_PATH
    )

    metadata = _load_json(
        DATASET_META_PATH
    )

    return {

        "uploaded":
            analysis is not None,

        "dataset":
            metadata,

        "analysis":
            analysis
    }


@app.get("/insights")
def insights():

    analysis = _load_json(
        ANALYSIS_PATH
    )

    if analysis is None:

        raise HTTPException(
            status_code=404,
            detail=
                "No uploaded dataset has "
                "been analyzed yet."
        )

    return {

        **analysis["qini"],

        "file_name":
            analysis["file_name"],

        "rows":
            analysis["rows"],

        "positive_ite":
            analysis["positive_ite"],

        "negative_ite":
            analysis["negative_ite"],

        "mean_ite":
            analysis["mean_ite"],

        "ate":
            analysis["ate"],

        "segment_counts":
            analysis["segment_counts"]
    }


@app.get("/budget")
def get_budget():

    budget = _load_json(
        BUDGET_PATH
    )

    if budget is None:

        return {

            "total_budget":
                DEFAULT_BUDGET,

            "max_customers":
                None
        }

    return budget


@app.post("/optimize")
def run_optimization(
    request: BudgetRequest
):

    try:

        summary = optimize(
            request.total_budget,
            request.max_customers
        )

        _save_json(
            BUDGET_PATH,
            {

                "total_budget":
                    request.total_budget,

                "max_customers":
                    request.max_customers,

                "updated_at":
                    datetime.now().isoformat()
            }
        )

        return {

            "status":
                "success",

            "optimization":
                summary
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=
                f"Optimization failed: "
                f"{str(exc)}"
        )


@app.get("/prescription")
def prescription(
    customer_id: int | None = None
):

    try:

        result = get_prescription(
            customer_id
        )

        summary = (
            get_optimization_summary()
        )

        return {

            "status":
                "success",

            "count":
                len(result),

            "prescriptions":
                result,

            "optimization":
                summary
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=
                f"Prescription retrieval failed: "
                f"{str(exc)}"
        )


@app.post("/drift")
def detect_drift(
    request: DriftRequest
):

    try:

        new_data = pd.DataFrame(
            request.data
        )

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

        missing = [
            column
            for column
            in required_columns
            if column
            not in new_data.columns
        ]

        if missing:

            raise HTTPException(
                status_code=400,
                detail=
                    f"Missing required drift "
                    f"columns: {missing}"
            )

        result = check_drift(
            new_data
        )

        return {

            "status":
                "success",

            "drift":
                result
        }

    except HTTPException:

        raise

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=
                f"Drift detection failed: "
                f"{str(exc)}"
        )