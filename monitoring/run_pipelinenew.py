"""
run_pipeline.py
================
EconoCausal — Data Drift & Monitoring
Day 6: Test with normal vs. changed data.
Day 7: Runs the whole Day 1-7 pipeline end to end and generates reports.

Test data is bootstrapped (sampled with replacement) directly from the real
reference data rather than hand-approximated, so the "normal" test set is
genuinely representative of the real distribution. The "changed" test set
takes the same bootstrap and deliberately shifts `income` and `purchase` to
verify the detector actually catches real drift.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from drift_detector import (
    build_and_save_reference,
    load_reference,
    check_drift,
)
from drift_report import save_drift_report


def bootstrap_sample(reference_df: pd.DataFrame, n: int = 500, seed: int = 7) -> pd.DataFrame:
    """Sample n rows WITH replacement directly from the real reference data."""
    return reference_df.sample(n=n, replace=True, random_state=seed).reset_index(drop=True)


def make_changed_sample(reference_df: pd.DataFrame, n: int = 500, seed: int = 7) -> pd.DataFrame:
    """
    Bootstrap from the real reference data, then deliberately shift
    `income` upward and flip `purchase` behavior to simulate real drift.
    """
    df = bootstrap_sample(reference_df, n=n, seed=seed).copy()

    if "income" in df.columns:
        df["income"] = df["income"] * 1.6 + 15000  # shift income up

    if "purchase" in df.columns:
        # Flip purchase outcome (0 <-> 1) to simulate a behavior change.
        df["purchase"] = df["purchase"].apply(lambda v: 1 - int(v) if pd.notna(v) else v)

    return df


def _print_report(drift_result: dict, title: str) -> None:
    print(f"\n{title}")
    print(f"{'Variable':<24}{'Type':<14}{'p-value':<12}{'Status'}")
    print("-" * 60)
    for var, info in drift_result["per_variable"].items():
        p_value = info.get("p_value")
        p_display = f"{p_value:.3f}" if isinstance(p_value, (int, float)) else "N/A"
        print(f"{var:<24}{info.get('type',''):<14}{p_display:<12}{info.get('status','')}")
    print("-" * 60)
    print(f"Overall: {drift_result['overall_status']}\n")


def main():
    print("=== Day 1-7 Drift Monitoring Pipeline ===\n")

    # Day 2: build/load reference (persists baseline_data.csv + baseline_stats.json)
    print("Building reference/baseline dataset...")
    reference_df = build_and_save_reference()
    print(f"Reference built: {reference_df.shape[0]} rows, {len(reference_df.columns)} columns.")

    # Day 6, Test 1: normal data -> expect NO DRIFT
    normal_sample = bootstrap_sample(reference_df, n=500, seed=7)
    normal_result = check_drift(normal_sample)
    _print_report(normal_result, "Test 1 — Normal data (expect NO DRIFT):")
    save_drift_report(normal_result, label="test1_normal")

    # Day 6, Test 2: changed data -> expect DRIFT DETECTED
    changed_sample = make_changed_sample(reference_df, n=500, seed=7)
    changed_result = check_drift(changed_sample)
    _print_report(changed_result, "Test 2 — Changed data (expect DRIFT DETECTED):")
    save_drift_report(changed_result, label="test2_changed")

    # Informational check (not a hard failure) — flags anything worth a
    # second look, but never crashes the pipeline on real data variability.
    if normal_result["overall_status"] != "NO DRIFT":
        print("NOTE: Test 1 (normal data) showed drift — check for a real baseline mismatch.")
    if changed_result["overall_status"] != "DRIFT DETECTED":
        print("NOTE: Test 2 (changed data) did not show overall drift — check the shift logic.")
    if changed_result["per_variable"].get("income", {}).get("status") != "DRIFT WARNING":
        print("NOTE: income was not flagged in Test 2 — the shift may be too small for this dataset.")
    if changed_result["per_variable"].get("purchase", {}).get("status") != "DRIFT WARNING":
        print("NOTE: purchase was not flagged in Test 2 — the flip may not be large enough for this dataset's class balance.")

    print("Pipeline run complete.")
    print("Reports saved to monitoring/drift_reports/ (latest_drift_report.json / .txt).")


if __name__ == "__main__":
    main()
