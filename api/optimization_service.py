import json
import os

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix, vstack


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")

MATRIX_PATH = os.path.join(
    DATA_DIR,
    "customer_optimizer_matrices_final.npz",
)

# Runtime dataset uploaded from React
DATASET_PATH = os.path.join(
    DATA_DIR,
    "runtime_uploaded_dataset.csv",
)

# Latest optimization output
OUTPUT_PATH = os.path.join(
    DATA_DIR,
    "optimized_discount_assignments.csv",
)

# Latest optimization summary
SUMMARY_PATH = os.path.join(
    DATA_DIR,
    "runtime_optimization_summary.json",
)

DEFAULT_BUDGET = 5000.0


# ============================================================
# LOAD RUNTIME CUSTOMER IDS
# ============================================================

def _load_runtime_customer_ids():
    """
    If a dataset was uploaded through the dashboard,
    restrict optimization to those customers.

    If no runtime dataset exists, optimize all customers
    from the prepared optimization matrices.
    """

    if not os.path.exists(DATASET_PATH):
        return None

    df = pd.read_csv(DATASET_PATH)

    if "customer_id" not in df.columns:
        raise ValueError(
            "Uploaded dataset must contain a customer_id column."
        )

    ids = pd.to_numeric(
        df["customer_id"],
        errors="coerce",
    )

    if ids.isna().any():
        raise ValueError(
            "Uploaded dataset contains invalid customer_id values."
        )

    # Customer IDs should be integers.
    if not np.all(np.isclose(ids, ids.round())):
        raise ValueError(
            "customer_id values must be whole numbers."
        )

    return ids.astype(np.int64).to_numpy()


# ============================================================
# LOAD OPTIMIZATION MATRICES
# ============================================================

def _load_matrices():
    if not os.path.exists(MATRIX_PATH):
        raise FileNotFoundError(
            f"Optimization matrix file not found: {MATRIX_PATH}"
        )

    with np.load(MATRIX_PATH, allow_pickle=False) as data:

        customer_ids = np.asarray(
            data["customer_ids"]
        ).copy()

        discount_levels = np.asarray(
            data["discount_levels"],
            dtype=float,
        ).copy()

        revenue_matrix = np.asarray(
            data["revenue_matrix"],
            dtype=float,
        ).copy()

        cost_matrix = np.asarray(
            data["cost_matrix"],
            dtype=float,
        ).copy()

    if revenue_matrix.ndim != 2:
        raise ValueError(
            "revenue_matrix must be a 2-D matrix."
        )

    if cost_matrix.shape != revenue_matrix.shape:
        raise ValueError(
            "cost_matrix and revenue_matrix shapes do not match."
        )

    n_customers, n_discounts = revenue_matrix.shape

    if len(customer_ids) != n_customers:
        raise ValueError(
            "customer_ids length does not match optimization matrices."
        )

    if len(discount_levels) != n_discounts:
        raise ValueError(
            "discount_levels length does not match optimization matrices."
        )

    if not np.isfinite(revenue_matrix).all():
        raise ValueError(
            "Revenue matrix contains invalid values."
        )

    if not np.isfinite(cost_matrix).all():
        raise ValueError(
            "Cost matrix contains invalid values."
        )

    return (
        customer_ids.astype(np.int64),
        discount_levels,
        revenue_matrix,
        cost_matrix,
    )


# ============================================================
# FILTER TO UPLOADED CUSTOMERS
# ============================================================

def _filter_to_runtime_dataset(
    customer_ids,
    discount_levels,
    revenue_matrix,
    cost_matrix,
):
    runtime_ids = _load_runtime_customer_ids()

    if runtime_ids is None:
        return (
            customer_ids,
            discount_levels,
            revenue_matrix,
            cost_matrix,
        )

    matrix_id_to_index = {
        int(customer_id): index
        for index, customer_id in enumerate(customer_ids)
    }

    missing_ids = [
        int(customer_id)
        for customer_id in runtime_ids
        if int(customer_id) not in matrix_id_to_index
    ]

    if missing_ids:
        sample = missing_ids[:10]

        raise ValueError(
            "The uploaded dataset contains customer IDs that are "
            "not present in customer_optimizer_matrices_final.npz. "
            f"Missing IDs: {sample}"
        )

    # Remove duplicates while preserving upload order.
    unique_ids = list(
        dict.fromkeys(
            int(customer_id)
            for customer_id in runtime_ids
        )
    )

    indices = np.array(
        [
            matrix_id_to_index[customer_id]
            for customer_id in unique_ids
        ],
        dtype=np.int64,
    )

    return (
        customer_ids[indices],
        discount_levels,
        revenue_matrix[indices],
        cost_matrix[indices],
    )


# ============================================================
# OPTIMIZATION
# ============================================================

def optimize(
    total_budget: float = DEFAULT_BUDGET,
    max_customers: int | None = None,
):
    """
    Solve the personalized discount allocation problem.

    Objective:
        Maximize total predicted revenue.

    Constraints:
        1. Exactly one discount option per customer.
        2. Total marketing cost <= budget.
        3. Optional maximum number of customers receiving
           a positive discount.

    IMPORTANT:
    The optimization is solved again every time this function
    is called with a different budget.
    """

    total_budget = float(total_budget)

    if not np.isfinite(total_budget):
        raise ValueError(
            "Budget must be a valid number."
        )

    if total_budget <= 0:
        raise ValueError(
            "Budget must be greater than zero."
        )

    if max_customers is not None:
        max_customers = int(max_customers)

        if max_customers <= 0:
            raise ValueError(
                "max_customers must be greater than zero."
            )

    (
        customer_ids,
        discount_levels,
        revenue_matrix,
        cost_matrix,
    ) = _load_matrices()

    (
        customer_ids,
        discount_levels,
        revenue_matrix,
        cost_matrix,
    ) = _filter_to_runtime_dataset(
        customer_ids,
        discount_levels,
        revenue_matrix,
        cost_matrix,
    )

    n_customers = len(customer_ids)
    n_discounts = len(discount_levels)

    if n_customers == 0:
        raise ValueError(
            "No customers available for optimization."
        )

    # --------------------------------------------------------
    # Decision variables
    #
    # x[i,j] = 1 if customer i receives discount j
    #
    # Number of variables:
    # 5000 * 7 = 35000
    # --------------------------------------------------------

    n_variables = n_customers * n_discounts

    # Flatten revenue matrix.
    #
    # milp minimizes, therefore maximize revenue by
    # minimizing negative revenue.
    objective = -revenue_matrix.reshape(-1)

    # Binary decision variables.
    integrality = np.ones(
        n_variables,
        dtype=np.int8,
    )

    bounds = Bounds(
        np.zeros(n_variables),
        np.ones(n_variables),
    )

    # --------------------------------------------------------
    # CONSTRAINT 1
    #
    # Exactly one discount per customer.
    #
    # Sparse matrix instead of a huge dense matrix.
    # --------------------------------------------------------

    rows = np.repeat(
        np.arange(n_customers),
        n_discounts,
    )

    cols = np.arange(n_variables)

    values = np.ones(
        n_variables,
        dtype=float,
    )

    assignment_matrix = csr_matrix(
        (
            values,
            (rows, cols),
        ),
        shape=(
            n_customers,
            n_variables,
        ),
    )

    # --------------------------------------------------------
    # CONSTRAINT 2
    #
    # Total marketing cost <= budget
    # --------------------------------------------------------

    budget_matrix = csr_matrix(
        cost_matrix.reshape(
            1,
            n_variables,
        )
    )

    constraint_matrices = [
        assignment_matrix,
        budget_matrix,
    ]

    lower_bounds = [
        *([1.0] * n_customers),
        -np.inf,
    ]

    upper_bounds = [
        *([1.0] * n_customers),
        total_budget,
    ]

    # --------------------------------------------------------
    # CONSTRAINT 3
    #
    # Optional maximum number of discounted customers.
    # --------------------------------------------------------

    if max_customers is not None:

        positive_discount = (
            discount_levels > 0
        ).astype(float)

        positive_discount_variables = np.tile(
            positive_discount,
            n_customers,
        )

        max_customer_matrix = csr_matrix(
            positive_discount_variables.reshape(
                1,
                n_variables,
            )
        )

        constraint_matrices.append(
            max_customer_matrix
        )

        lower_bounds.append(-np.inf)
        upper_bounds.append(
            float(max_customers)
        )

    # --------------------------------------------------------
    # Combine sparse constraints
    # --------------------------------------------------------

    constraint_matrix = vstack(
        constraint_matrices,
        format="csr",
    )

    constraints = LinearConstraint(
        constraint_matrix,
        np.asarray(lower_bounds),
        np.asarray(upper_bounds),
    )

    # --------------------------------------------------------
    # SOLVE MILP
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

    if not result.success:
        raise RuntimeError(
            "Optimization failed: "
            f"{result.message}"
        )

    # --------------------------------------------------------
    # READ SOLUTION
    # --------------------------------------------------------

    solution = np.asarray(
        result.x,
        dtype=float,
    ).reshape(
        n_customers,
        n_discounts,
    )

    chosen_indices = np.argmax(
        solution,
        axis=1,
    )

    optimal_discount = discount_levels[
        chosen_indices
    ]

    predicted_revenue = revenue_matrix[
        np.arange(n_customers),
        chosen_indices,
    ]

    marketing_cost = cost_matrix[
        np.arange(n_customers),
        chosen_indices,
    ]

    discount_fraction = (
        optimal_discount / 100.0
    )

    # --------------------------------------------------------
    # OUTPUT DATAFRAME
    # --------------------------------------------------------

    output_df = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "optimal_discount": optimal_discount,
            "discount_fraction": discount_fraction,
            "predicted_revenue": predicted_revenue,
            "marketing_cost": marketing_cost,
        }
    )

    output_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    customers_allocated = int(
        (optimal_discount > 0).sum()
    )

    total_predicted_revenue = float(
        predicted_revenue.sum()
    )

    total_marketing_cost = float(
        marketing_cost.sum()
    )

    remaining_budget = float(
        total_budget - total_marketing_cost
    )

    allocation_rate = float(
        customers_allocated / n_customers * 100
    )

    average_discount = float(
        optimal_discount.mean()
    )

    summary = {
        "customers": int(n_customers),
        "customers_allocated": customers_allocated,
        "allocation_rate": allocation_rate,
        "average_discount": average_discount,
        "predicted_revenue": total_predicted_revenue,
        "marketing_cost": total_marketing_cost,
        "total_budget": total_budget,
        "remaining_budget": remaining_budget,
        "max_customers": max_customers,
        "discount_levels": discount_levels.tolist(),
        "optimization_status": "optimal",
        "solver_message": str(result.message),
        "source": "customer_optimizer_matrices_final.npz",
    }

    with open(
        SUMMARY_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
        )

    return summary