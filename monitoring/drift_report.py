"""
drift_report.py
================
EconoCausal — Data Drift & Monitoring
Supports Day 6 (test reporting) and Day 7 (final packaging).

Saves each drift-check result as both a JSON file and a human-readable
text report, and keeps a "latest" pointer so the most recent report is
always easy to find without scanning timestamps.
"""

import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "drift_reports")
LATEST_JSON_PATH = os.path.join(REPORTS_DIR, "latest_drift_report.json")
LATEST_TXT_PATH = os.path.join(REPORTS_DIR, "latest_drift_report.txt")

os.makedirs(REPORTS_DIR, exist_ok=True)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _format_text_report(drift_result: dict, label: str = "") -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("EconoCausal — Drift Report" + (f" ({label})" if label else ""))
    lines.append("Generated (UTC): " + datetime.now(timezone.utc).isoformat())
    lines.append("Threshold (p-value): " + str(drift_result.get("threshold")))
    lines.append("-" * 60)
    lines.append(f"{'Variable':<24}{'Type':<14}{'p-value':<12}{'Status'}")
    lines.append("-" * 60)

    for var, info in drift_result.get("per_variable", {}).items():
        p_value = info.get("p_value")
        p_display = f"{p_value:.3f}" if isinstance(p_value, (int, float)) else "N/A"
        lines.append(f"{var:<24}{info.get('type', ''):<14}{p_display:<12}{info.get('status', '')}")

    lines.append("-" * 60)
    lines.append(f"OVERALL: {drift_result.get('overall_status')}")
    lines.append("=" * 60)
    return "\n".join(lines)


def save_drift_report(drift_result: dict, label: str = "") -> dict:
    """
    Saves the given drift_result (as returned by drift_detector.check_drift)
    as a timestamped JSON + text report, and updates the "latest" pointer
    files. Returns the paths written.
    """
    ts = _timestamp()
    suffix = f"_{label}" if label else ""

    json_path = os.path.join(REPORTS_DIR, f"drift_report_{ts}{suffix}.json")
    txt_path = os.path.join(REPORTS_DIR, f"drift_report_{ts}{suffix}.txt")

    with open(json_path, "w") as f:
        json.dump(drift_result, f, indent=2)

    text_report = _format_text_report(drift_result, label=label)
    with open(txt_path, "w") as f:
        f.write(text_report)

    # Update "latest" pointers (simple copy, always overwritten).
    with open(LATEST_JSON_PATH, "w") as f:
        json.dump(drift_result, f, indent=2)
    with open(LATEST_TXT_PATH, "w") as f:
        f.write(text_report)

    return {
        "json_path": json_path,
        "txt_path": txt_path,
        "latest_json_path": LATEST_JSON_PATH,
        "latest_txt_path": LATEST_TXT_PATH,
    }


def load_latest_report() -> dict:
    """Load the most recently saved drift report (JSON)."""
    if not os.path.exists(LATEST_JSON_PATH):
        raise FileNotFoundError(
            f"No drift report found at {LATEST_JSON_PATH}. Run a drift check first."
        )
    with open(LATEST_JSON_PATH, "r") as f:
        return json.load(f)
