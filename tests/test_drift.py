import pandas as pd

from monitoring.drift_detector import check_drift


# --------------------------------------------------
# Helper: Load the reference/baseline dataset
# --------------------------------------------------

def load_reference():

    return pd.read_csv(
        "monitoring/reference_data/baseline_data.csv"
    )


# --------------------------------------------------
# TEST 1: Normal / Similar Data
# Expected: NO DRIFT
# --------------------------------------------------


def test_normal_data():
    reference = load_reference()

    # Use the same baseline distribution as incoming data.
    # This gives us a deterministic NO DRIFT test.
    new_data = reference.copy()

    result = check_drift(new_data)

    print("\nNORMAL DATA TEST")
    print("Overall status:", result["overall_status"])
    print("Threshold:", result["threshold"])

    assert result["overall_status"] == "NO DRIFT"



# --------------------------------------------------
# TEST 2: Changed Numeric Data
# Expected: DRIFT DETECTED
# --------------------------------------------------

def test_changed_numeric_data():

    reference = load_reference()

    new_data = reference.sample(
        n=min(500, len(reference)),
        random_state=42
    ).copy()

    # Deliberately change the income distribution
    new_data["income"] = new_data["income"] * 5

    result = check_drift(new_data)

    print("\nCHANGED NUMERIC DATA TEST")
    print("Overall status:", result["overall_status"])
    print("Threshold:", result["threshold"])

    assert result["overall_status"] == "DRIFT DETECTED"


# --------------------------------------------------
# TEST 3: Changed Categorical Data
# Expected: DRIFT DETECTED
# --------------------------------------------------

def test_changed_categorical_data():

    reference = load_reference()

    new_data = reference.sample(
        n=min(500, len(reference)),
        random_state=42
    ).copy()

    # Deliberately change the channel distribution
    if "channel" in new_data.columns:
        new_data["channel"] = "online"

    result = check_drift(new_data)

    print("\nCHANGED CATEGORICAL DATA TEST")
    print("Overall status:", result["overall_status"])
    print("Threshold:", result["threshold"])

    assert result["overall_status"] == "DRIFT DETECTED"


# --------------------------------------------------
# TEST 4: Check Drift Result Structure
# --------------------------------------------------

def test_drift_result_structure():

    reference = load_reference()

    new_data = reference.sample(
        n=min(100, len(reference)),
        random_state=42
    ).copy()

    result = check_drift(new_data)

    # Check top-level response structure
    assert "overall_status" in result
    assert "threshold" in result
    assert "per_variable" in result

    # Check valid status
    assert result["overall_status"] in [
        "NO DRIFT",
        "DRIFT DETECTED"
    ]

    # Check threshold
    assert result["threshold"] == 0.05

    # Check per-variable results
    assert isinstance(result["per_variable"], dict)
