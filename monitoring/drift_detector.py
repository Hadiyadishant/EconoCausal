"""
drift_detector.py
==================
EconoCausal — Data Drift & Monitoring
Student 2 (Princy) — Day 1 to Day 5 deliverables.

Day 1: Define which variables are monitored for drift.
Day 2: Build & persist the reference/baseline dataset.
Day 3: Design (documented below) — KS test for numeric, Chi-square for categorical.
Day 4: Implement the actual drift calculations.
Day 5: Add the threshold/warning system + the single public entry point
       (`check_drift`) that Dishant's API calls.
"""

import json
import os
import warnings

import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REAL_DATA_PATH = os.path.join(BASE_DIR, "..", "data", "mockretaildatacleaned.csv")
REFERENCE_DIR = os.path.join(BASE_DIR, "reference_data")
BASELINE_DATA_PATH = os.path.join(REFERENCE_DIR, "baseline_data.csv")
BASELINE_STATS_PATH = os.path.join(REFERENCE_DIR, "baseline_stats.json")

os.makedirs(REFERENCE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Day 1 — Monitored variables
# ---------------------------------------------------------------------------
# NOTE: campaign_response looked like it might be a yes/no flag at first
# glance, but the real dataset shows it's a continuous propensity-style
# value (range ~0-0.408). It is monitored as NUMERIC, not categorical,
# so its drift is measured with the KS test rather than chi-square.
MONITORED_NUMERIC_VARS = [
    "age",
    "income",
    "previous_purchases",
    "customer_tenure_days",
    "avg_basket_size",
    "discount",
    "campaign_response",
]

MONITORED_CATEGORICAL_VARS = [
    "channel",
    "purchase",
]

# ---------------------------------------------------------------------------
# Day 5 — Threshold
# ---------------------------------------------------------------------------
DRIFT_THRESHOLD = 0.05  # p-value below this => drift


# ---------------------------------------------------------------------------
# Day 2 — Reference / baseline dataset
# ---------------------------------------------------------------------------
def _generate_synthetic_fallback(n_rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Synthetic stand-in dataset used ONLY if the real CSV is missing, so the
    pipeline never breaks during development. Shapes loosely mirror the
    real data's ranges (e.g. campaign_response in [0, 0.408]).
    """
    warnings.warn(
        f"Real dataset not found at {REAL_DATA_PATH}. "
        "Falling back to a synthetic dataset for development purposes only. "
        "Do NOT use this fallback baseline in production.",
        stacklevel=2,
    )
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "age": rng.integers(18, 75, n_rows),
            "income": rng.normal(55000, 18000, n_rows).round(2),
            "previous_purchases": rng.poisson(5, n_rows),
            "customer_tenure_days": rng.integers(1, 3650, n_rows),
            "avg_basket_size": rng.gamma(2.0, 25.0, n_rows).round(2),
            "discount": rng.uniform(0, 0.5, n_rows).round(3),
            "campaign_response": rng.uniform(0, 0.408, n_rows).round(4),
            "channel": rng.choice(["online", "in_store", "mobile_app"], n_rows),
            "purchase": rng.choice([0, 1], n_rows, p=[0.6, 0.4]),
        }
    )
    return df


def _load_real_or_fallback() -> pd.DataFrame:
    if os.path.exists(REAL_DATA_PATH):
        return pd.read_csv(REAL_DATA_PATH)
    return _generate_synthetic_fallback()


def build_baseline_stats(df: pd.DataFrame) -> dict:
    """
    Compute reference statistics per monitored variable.
      - numeric  -> mean, std, min, max, n
      - categorical -> value counts (as a dict, keys as str)
    """
    stats_dict = {"numeric": {}, "categorical": {}}

    for col in MONITORED_NUMERIC_VARS:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        stats_dict["numeric"][col] = {
            "mean": float(series.mean()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
            "n": int(series.shape[0]),
            # raw values kept separately in baseline_data.csv for the KS test;
            # summary stats here are for quick reference/reporting only.
        }

    for col in MONITORED_CATEGORICAL_VARS:
        if col not in df.columns:
            continue
        counts = df[col].value_counts(dropna=True)
        # JSON always stores dict keys as strings -> normalize now so the
        # baseline on disk and the baseline in memory are always consistent.
        stats_dict["categorical"][col] = {str(k): int(v) for k, v in counts.items()}

    return stats_dict


def build_and_save_reference() -> pd.DataFrame:
    """
    Loads the historical dataset (real CSV, or synthetic fallback with a
    warning), computes baseline stats, and persists both to disk:
      - reference_data/baseline_data.csv   (full historical dataset)
      - reference_data/baseline_stats.json (precomputed stats/distributions)
    Returns the baseline dataframe.
    """
    df = _load_real_or_fallback()

    keep_cols = [c for c in MONITORED_NUMERIC_VARS + MONITORED_CATEGORICAL_VARS if c in df.columns]
    baseline_df = df[keep_cols].copy()
    baseline_df.to_csv(BASELINE_DATA_PATH, index=False)

    stats_dict = build_baseline_stats(baseline_df)
    with open(BASELINE_STATS_PATH, "w") as f:
        json.dump(stats_dict, f, indent=2)

    return baseline_df


def load_reference() -> pd.DataFrame:
    """Load the persisted baseline dataset, building it first if needed."""
    if not os.path.exists(BASELINE_DATA_PATH):
        return build_and_save_reference()
    return pd.read_csv(BASELINE_DATA_PATH)


# ---------------------------------------------------------------------------
# Day 3 — Design (documented, not code):
#
#   reference data + new data -> drift calculation -> drift score -> threshold -> WARNING / OK
#
#   numeric vars     -> Kolmogorov-Smirnov (KS) two-sample test
#   categorical vars -> Chi-square goodness-of-fit test
#   threshold        -> p-value < 0.05 => drift
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Day 4 — Drift calculations
# ---------------------------------------------------------------------------
def calculate_numeric_drift(reference_values, new_values) -> dict:
    """
    Two-sample Kolmogorov-Smirnov test between reference and new numeric
    values. Returns statistic, p-value, and status.
    """
    reference_values = pd.Series(reference_values).dropna()
    new_values = pd.Series(new_values).dropna()

    if len(reference_values) == 0 or len(new_values) == 0:
        return {"statistic": None, "p_value": None, "status": "INSUFFICIENT_DATA"}

    statistic, p_value = stats.ks_2samp(reference_values, new_values)
    status = "DRIFT WARNING" if p_value < DRIFT_THRESHOLD else "NO DRIFT"
    return {"statistic": float(statistic), "p_value": float(p_value), "status": status}


def calculate_categorical_drift(reference_values, new_values) -> dict:
    """
    Chi-square goodness-of-fit test between reference and new categorical
    distributions.

    Category keys are normalized to strings on both sides — this matters
    because saving/reloading the baseline through JSON always turns dict
    keys into strings (e.g. purchase 0/1 -> "0"/"1"), and comparisons would
    silently fail to match otherwise.
    """
    ref_counts = pd.Series(reference_values).astype(str).value_counts()
    new_counts = pd.Series(new_values).astype(str).value_counts()

    # Align on the union of categories seen in either sample.
    all_categories = sorted(set(ref_counts.index) | set(new_counts.index))
    if len(all_categories) < 2:
        return {"statistic": None, "p_value": None, "status": "INSUFFICIENT_DATA"}

    ref_aligned = ref_counts.reindex(all_categories, fill_value=0).astype(float)
    new_aligned = new_counts.reindex(all_categories, fill_value=0).astype(float)

    # Rescale reference proportions to the new sample's total count so
    # chisquare compares distributions, not raw magnitudes.
    new_total = new_aligned.sum()
    ref_total = ref_aligned.sum()
    if ref_total == 0 or new_total == 0:
        return {"statistic": None, "p_value": None, "status": "INSUFFICIENT_DATA"}

    expected = ref_aligned / ref_total * new_total
    # Avoid zero-expected-frequency errors in chisquare.
    expected = expected.replace(0, 1e-6)

    statistic, p_value = stats.chisquare(f_obs=new_aligned.values, f_exp=expected.values)
    status = "DRIFT WARNING" if p_value < DRIFT_THRESHOLD else "NO DRIFT"
    return {"statistic": float(statistic), "p_value": float(p_value), "status": status}


# ---------------------------------------------------------------------------
# Day 5 — Threshold / warning system + public entry point
# ---------------------------------------------------------------------------
def evaluate_drift(reference_df: pd.DataFrame, new_df: pd.DataFrame) -> dict:
    """
    Runs numeric (KS) and categorical (Chi-square) drift tests across all
    monitored variables.

    Returns:
        {
          "per_variable": {var_name: {statistic, p_value, status, type}, ...},
          "overall_status": "NO DRIFT" | "DRIFT DETECTED"
        }

    KNOWN LIMITATION (flagged, not fixed): testing 9 variables independently
    at p < 0.05 each gives a ~30-40% chance of at least one false "drift"
    flag on data with no real change (multiple-comparisons effect). Worth
    knowing if a lone variable flips occasionally in production.
    """
    per_variable = {}
    any_drift = False

    for col in MONITORED_NUMERIC_VARS:
        if col not in reference_df.columns or col not in new_df.columns:
            continue
        result = calculate_numeric_drift(reference_df[col], new_df[col])
        result["type"] = "numeric"
        per_variable[col] = result
        if result["status"] == "DRIFT WARNING":
            any_drift = True

    for col in MONITORED_CATEGORICAL_VARS:
        if col not in reference_df.columns or col not in new_df.columns:
            continue
        result = calculate_categorical_drift(reference_df[col], new_df[col])
        result["type"] = "categorical"
        per_variable[col] = result
        if result["status"] == "DRIFT WARNING":
            any_drift = True

    return {
        "per_variable": per_variable,
        "overall_status": "DRIFT DETECTED" if any_drift else "NO DRIFT",
    }


def check_drift(new_df: pd.DataFrame) -> dict:
    """
    Single entry point for the API layer.

    Loads the persisted baseline, evaluates drift against `new_df`, and
    returns a ready-to-serialize dict:

        {
          "overall_status": "NO DRIFT" | "DRIFT DETECTED",
          "threshold": 0.05,
          "per_variable": {...}
        }
    """
    reference_df = load_reference()
    result = evaluate_drift(reference_df, new_df)
    return {
        "overall_status": result["overall_status"],
        "threshold": DRIFT_THRESHOLD,
        "per_variable": result["per_variable"],
    }


if __name__ == "__main__":
    # Quick manual smoke test.
    ref = build_and_save_reference()
    print(f"Baseline built: {ref.shape[0]} rows, columns: {list(ref.columns)}")
    sample = ref.sample(n=min(500, len(ref)), random_state=1)
    print(json.dumps(check_drift(sample), indent=2)[:500], "...")
