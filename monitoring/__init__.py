"""
EconoCausal.monitoring
=======================
Data Drift & Monitoring package (Princy — Week 4, Day 1-7).

Public entry point for other modules (e.g. Dishant's API) is:

    from monitoring.drift_detector import check_drift
    result = check_drift(new_df)

See api_hook_snippet.py for the exact integration snippet.
"""

from .drift_detector import (
    MONITORED_NUMERIC_VARS,
    MONITORED_CATEGORICAL_VARS,
    DRIFT_THRESHOLD,
    build_and_save_reference,
    check_drift,
)

__all__ = [
    "MONITORED_NUMERIC_VARS",
    "MONITORED_CATEGORICAL_VARS",
    "DRIFT_THRESHOLD",
    "build_and_save_reference",
    "check_drift",
]
