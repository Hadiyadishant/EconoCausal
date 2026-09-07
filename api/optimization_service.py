from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

MATRIX_FILE = DATA_DIR / "customer_optimizer_matrices_final.npz"

RUNTIME_DATASET_FILE = DATA_DIR / "runtime_uploaded_dataset.csv"

OUTPUT_FILE = DATA_DIR / "optimized_discount_assignments.csv"

SUMMARY_FILE = DATA_DIR / "runtime_optimization_summary.json"


# ============================================================
# OPTIMIZATION CONSTANTS
# ============================================================

DEFAULT_BUDGET = 5000.0

DISCOUNT_LEVELS = np.array(
    [0, 5, 10, 15, 20, 25, 30],
    dtype=float,
)


# ============================================================
# LOAD OPTIMIZATION MATRICES
# ============================================================

def _load_optimizer_matrices():
    """
    Load the real customer-level optimization matrices
    prepared for Week 3.

    Expected NPZ keys:

        customer_ids
        discount_levels
        revenue_matrix
        cost_matrix
    """

    if not MATRIX_FILE.exists():
        raise FileNotFoundError(
            f"Optimizer matrix file not found: {MATRIX_FILE}"
        )

    data = np.load(MATRIX_FILE)

    required_keys = {
        "customer_ids",
        "discount_levels",
        "revenue_matrix",
        "cost_matrix",
    }

    missing_keys = required_keys.difference(data.files)

    if missing_keys:
        raise ValueError(
            "Optimizer matrix file is missing required keys: "
            + ", ".join(sorted(missing_keys))
        )

    customer_ids = np.asarray(
        data["customer_ids"]
    )

    discount_levels = np.asarray(
        data["discount_levels"],
        dtype=float,
    )

    revenue_matrix = np.asarray(
        data["revenue_matrix"],
        dtype=float,
    )

    cost_matrix = np.asarray(
        data["cost_matrix"],
        dtype=float,
    )

    if revenue_matrix.ndim != 2:
        raise ValueError(
            "revenue_matrix must be a 2-dimensional matrix."
        )

    if cost_matrix.ndim != 2:
        raise ValueError(
            "cost_matrix must be a 2-dimensional matrix."
        )

    if revenue_matrix.shape != cost_matrix.shape:
        raise ValueError(
            "revenue_matrix and cost_matrix must have "
            "the same shape."
        )

    if revenue_matrix.shape[0] != len(customer_ids):
        raise ValueError(
            "Number of customer IDs does not match "
            "the number of rows in revenue_matrix."
        )

    if revenue_matrix.shape[1] != len(discount_levels):
        raise ValueError(
            "Number of discount levels does not match "
            "the number of columns in revenue_matrix."
        )

    return (
        customer_ids,
        discount_levels,
        revenue_matrix,
        cost_matrix,
    )


# ============================================================
# FILTER MATRICES USING UPLOADED DATASET
# ============================================================

def _apply_runtime_customer_filter(
    customer_ids,
    revenue_matrix,
    cost_matrix,
):
    """
    If the user has uploaded a runtime dataset, keep only
    customers present in that uploaded dataset.

    The optimization matrices remain the authoritative
    source for discount-level revenue and cost.
    """

    if not RUNTIME_DATASET_FILE.exists():
        return (
            customer_ids,
            revenue_matrix,
            cost_matrix,
        )

    runtime_df = pd.read_csv(
        RUNTIME_DATASET_FILE
    )

    if "customer_id" not in runtime_df.columns:
        raise ValueError(
            "runtime_uploaded_dataset.csv must contain "
            "'customer_id'."
        )

    runtime_ids = pd.to_numeric(
        runtime_df["customer_id"],
        errors="coerce",
    )

    runtime_ids = (
        runtime_ids
        .dropna()
        .astype(int)
        .unique()
    )

    if len(runtime_ids) == 0:
        raise ValueError(
            "The uploaded dataset contains no valid customer IDs."
        )

    matrix_ids = pd.to_numeric(
        pd.Series(customer_ids),
        errors="coerce",
    )

    matrix_ids = matrix_ids.astype("Int64")

    runtime_id_set = set(
        runtime_ids.tolist()
    )

    mask = matrix_ids.isin(
        runtime_id_set
    ).to_numpy()

    if not np.any(mask):
        raise ValueError(
            "None of the uploaded customer IDs were found "
            "in the optimizer matrices."
        )

    return (
        customer_ids[mask],
        revenue_matrix[mask],
        cost_matrix[mask],
    )


# ============================================================
# BUILD SPARSE CUSTOMER ASSIGNMENT CONSTRAINT
# ============================================================

def _build_customer_assignment_constraint(
    number_of_customers,
    number_of_discounts,
):
    """
    Build the constraint:

        x[i,0] + x[i,1] + ... + x[i,6] = 1

    for every customer i.

    IMPORTANT:
    This is intentionally constructed as a sparse matrix.

    Dense version:

        (5000, 35000)

    would require roughly 1.30 GiB.

    Sparse version stores only the 35,000 ones.
    """

    number_of_variables = (
        number_of_customers *
        number_of_discounts
    )

    rows = np.repeat(
        np.arange(number_of_customers),
        number_of_discounts,
    )

    cols = np.arange(
        number_of_variables
    )

    values = np.ones(
        number_of_variables,
        dtype=float,
    )

    assignment_matrix = coo_matrix(
        (
            values,
            (rows, cols),
        ),
        shape=(
            number_of_customers,
            number_of_variables,
        ),
    ).tocsr()

    return assignment_matrix


# ============================================================
# BUILD BUDGET CONSTRAINT
# ============================================================

def _build_budget_constraint(
    cost_matrix,
):
    """
    Build:

        total marketing cost <= budget

    as a sparse row.
    """

    flattened_cost = np.asarray(
        cost_matrix,
        dtype=float,
    ).reshape(-1)

    number_of_variables = (
        flattened_cost.shape[0]
    )

    rows = np.zeros(
        number_of_variables,
        dtype=np.int32,
    )

    cols = np.arange(
        number_of_variables,
        dtype=np.int32,
    )

    budget_matrix = coo_matrix(
        (
            flattened_cost,
            (rows, cols),
        ),
        shape=(
            1,
            number_of_variables,
        ),
    ).tocsr()

    return budget_matrix


# ============================================================
# BUILD MAX-CUSTOMER CONSTRAINT
# ============================================================

def _build_max_customer_constraint(
    number_of_customers,
    number_of_discounts,
):
    """
    Build:

        sum(x[i,j] for j > 0) <= max_customers

    Only positive-discount choices are counted.

    Discount column 0 corresponds to discount = 0.
    """

    positive_discount_columns = np.arange(
        1,
        number_of_discounts,
    )

    rows = []
    cols = []
    values = []

    for customer_index in range(
        number_of_customers
    ):
        start = (
            customer_index *
            number_of_discounts
        )

        for discount_column in positive_discount_columns:
            rows.append(0)

            cols.append(
                start + discount_column
            )

            values.append(1.0)

    if not cols:
        return coo_matrix(
            (
                1,
                number_of_customers *
                number_of_discounts,
            ),
            dtype=float,
        ).tocsr()

    matrix = coo_matrix(
        (
            np.asarray(
                values,
                dtype=float,
            ),
            (
                np.zeros(
                    len(cols),
                    dtype=np.int32,
                ),
                np.asarray(
                    cols,
                    dtype=np.int32,
                ),
            ),
        ),
        shape=(
            1,
            number_of_customers *
            number_of_discounts,
        ),
    ).tocsr()

    return matrix


# ============================================================
# RUN OPTIMIZATION
# ============================================================

def optimize(
    budget: float = DEFAULT_BUDGET,
    max_customers: int | None = None,
):
    """
    Run budget-constrained personalized discount optimization.

    Objective:

        maximize total predicted revenue

    Subject to:

        exactly one discount per customer
        total marketing cost <= budget
        optional maximum number of customers receiving
        a positive discount

    The optimization uses SciPy MILP with sparse constraints.
    """

    budget = float(budget)

    if not np.isfinite(budget):
        raise ValueError(
            "Budget must be a finite number."
        )

    if budget < 0:
        raise ValueError(
            "Budget cannot be negative."
        )

    if max_customers is not None:
        max_customers = int(
            max_customers
        )

        if max_customers < 0:
            raise ValueError(
                "max_customers cannot be negative."
            )

    # --------------------------------------------------------
    # Load matrices
    # --------------------------------------------------------

    (
        customer_ids,
        discount_levels,
        revenue_matrix,
        cost_matrix,
    ) = _load_optimizer_matrices()

    # --------------------------------------------------------
    # Filter using runtime uploaded dataset
    # --------------------------------------------------------

    (
        customer_ids,
        revenue_matrix,
        cost_matrix,
    ) = _apply_runtime_customer_filter(
        customer_ids,
        revenue_matrix,
        cost_matrix,
    )

    number_of_customers = (
        revenue_matrix.shape[0]
    )

    number_of_discounts = (
        revenue_matrix.shape[1]
    )

    if number_of_customers == 0:
        raise ValueError(
            "No customers are available for optimization."
        )

    if number_of_discounts == 0:
        raise ValueError(
            "No discount options are available."
        )

    # --------------------------------------------------------
    # Validate discount levels
    # --------------------------------------------------------

    if len(discount_levels) != number_of_discounts:
        raise ValueError(
            "Discount-level count does not match "
            "optimization matrix."
        )

    # --------------------------------------------------------
    # Validate numerical values
    # --------------------------------------------------------

    if not np.all(
        np.isfinite(revenue_matrix)
    ):
        raise ValueError(
            "revenue_matrix contains NaN or infinite values."
        )

    if not np.all(
        np.isfinite(cost_matrix)
    ):
        raise ValueError(
            "cost_matrix contains NaN or infinite values."
        )

    if np.any(cost_matrix < 0):
        raise ValueError(
            "cost_matrix contains negative costs."
        )

    # --------------------------------------------------------
    # Number of optimization variables
    # --------------------------------------------------------

    number_of_variables = (
        number_of_customers *
        number_of_discounts
    )

    # --------------------------------------------------------
    # Objective
    #
    # scipy.optimize.milp minimizes.
    #
    # We want:
    #
    #     maximize revenue
    #
    # Therefore:
    #
    #     minimize -revenue
    # --------------------------------------------------------

    objective = (
        -revenue_matrix.reshape(-1)
    )

    # --------------------------------------------------------
    # Variable bounds
    #
    # x[i,j] is binary:
    #
    #     0 = discount option not selected
    #     1 = discount option selected
    # --------------------------------------------------------

    lower_bounds = np.zeros(
        number_of_variables,
        dtype=float,
    )

    upper_bounds = np.ones(
        number_of_variables,
        dtype=float,
    )

    bounds = Bounds(
        lower_bounds,
        upper_bounds,
    )

    integrality = np.ones(
        number_of_variables,
        dtype=np.int8,
    )

    # --------------------------------------------------------
    # Sparse constraint matrices
    # --------------------------------------------------------

    assignment_matrix = (
        _build_customer_assignment_constraint(
            number_of_customers,
            number_of_discounts,
        )
    )

    budget_matrix = (
        _build_budget_constraint(
            cost_matrix
        )
    )

    constraint_matrices = [
        assignment_matrix,
        budget_matrix,
    ]

    lower_constraint = [
        np.ones(
            number_of_customers,
            dtype=float,
        ),
        -np.inf,
    ]

    upper_constraint = [
        np.ones(
            number_of_customers,
            dtype=float,
        ),
        budget,
    ]

    # --------------------------------------------------------
    # Optional maximum number of discounted customers
    # --------------------------------------------------------

    if max_customers is not None:

        if max_customers > number_of_customers:
            max_customers = number_of_customers

        max_customer_matrix = (
            _build_max_customer_constraint(
                number_of_customers,
                number_of_discounts,
            )
        )

        constraint_matrices.append(
            max_customer_matrix
        )

        lower_constraint.append(
            -np.inf
        )

        upper_constraint.append(
            float(max_customers)
        )

    # --------------------------------------------------------
    # Combine sparse matrices
    # --------------------------------------------------------

    from scipy.sparse import vstack

    constraint_matrix = vstack(
        constraint_matrices,
        format="csr",
    )

    constraints = LinearConstraint(
        constraint_matrix,
        np.asarray(
            lower_constraint,
            dtype=float,
        ),
        np.asarray(
            upper_constraint,
            dtype=float,
        ),
    )

    # --------------------------------------------------------
    # Run SciPy MILP
    # --------------------------------------------------------

    result = milp(
        c=objective,
        integrality=integrality,
        bounds=bounds,
        constraints=constraints,
        options={
            "disp": False,
        },
    )

    # --------------------------------------------------------
    # Check optimizer result
    # --------------------------------------------------------

    if not result.success:
        raise RuntimeError(
            "Optimization failed: "
            f"{result.message}"
        )

    if result.x is None:
        raise RuntimeError(
            "Optimization completed without a solution."
        )

    # --------------------------------------------------------
    # Convert solution to customer × discount matrix
    # --------------------------------------------------------

    solution = np.rint(
        result.x
    ).astype(int)

    solution_matrix = solution.reshape(
        number_of_customers,
        number_of_discounts,
    )

    selected_columns = (
        solution_matrix.argmax(axis=1)
    )

    # --------------------------------------------------------
    # Extract selected discount
    # --------------------------------------------------------

    optimal_discount = (
        discount_levels[
            selected_columns
        ]
    )

    predicted_revenue = (
        revenue_matrix[
            np.arange(number_of_customers),
            selected_columns,
        ]
    )

    marketing_cost = (
        cost_matrix[
            np.arange(number_of_customers),
            selected_columns,
        ]
    )

    # --------------------------------------------------------
    # Build output dataframe
    # --------------------------------------------------------

    output_df = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "optimal_discount": optimal_discount,
            "discount_fraction": (
                optimal_discount / 100.0
            ),
            "predicted_revenue": predicted_revenue,
            "marketing_cost": marketing_cost,
        }
    )

    # --------------------------------------------------------
    # Save optimized assignments
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Calculate summary
    # --------------------------------------------------------

    total_marketing_cost = float(
        output_df["marketing_cost"].sum()
    )

    total_predicted_revenue = float(
        output_df["predicted_revenue"].sum()
    )

    customers_allocated = int(
        (
            output_df["optimal_discount"]
            > 0
        ).sum()
    )

    allocation_rate = float(
        customers_allocated /
        number_of_customers
    )

    average_discount = float(
        output_df["optimal_discount"].mean()
    )

    remaining_budget = float(
        budget -
        total_marketing_cost
    )

    summary = {
        "customers": int(
            number_of_customers
        ),

        "customers_allocated": customers_allocated,

        "allocation_rate": allocation_rate,

        "average_discount": average_discount,

        "predicted_revenue": total_predicted_revenue,

        "marketing_cost": total_marketing_cost,

        "budget": budget,

        "remaining_budget": remaining_budget,

        "max_customers": max_customers,

        "discount_levels": (
            discount_levels.tolist()
        ),

        "validation": {
            "budget_respected": bool(
                total_marketing_cost
                <= budget + 1e-6
            ),

            "one_discount_per_customer": bool(
                np.all(
                    solution_matrix.sum(axis=1)
                    == 1
                )
            ),

            "positive_discount_customers": customers_allocated,
        },

        "source": {
            "optimizer_matrix": str(
                MATRIX_FILE
            ),

            "runtime_dataset_used": bool(
                RUNTIME_DATASET_FILE.exists()
            ),
        },

        "output_file": str(
            OUTPUT_FILE
        ),
    }

    # --------------------------------------------------------
    # Save summary
    # --------------------------------------------------------

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
        )

    return {
        **summary,
        "allocations": output_df.to_dict(
            orient="records"
        ),
    }