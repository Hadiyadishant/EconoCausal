"""
Optimization Formulation


Purpose:
Define the prescriptive optimization problem for customer discount allocation.

Objective:
Maximize total predicted revenue.

Constraints:
1. Total marketing cost <= available budget
2. 0 <= discount <= maximum discount
"""

import numpy as np
import pandas as pd


# 1. Optimization Configuration

BUDGET = 5000.0
MAX_DISCOUNT = 0.30


# 2. Load Prediction Inputs

def load_prediction_inputs(file_path):
    """
    Load customer-level prediction results.

    Expected columns:
        customer_id
        predicted_revenue
        ite
    """

    df = pd.read_csv(file_path)

    required_columns = [
        "customer_id",
        "predicted_revenue",
        "ite"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return df


# 3. Define Revenue Function

def predicted_revenue(discount, base_revenue, ite):
    """
    Estimate revenue after assigning a discount.

    A simple formulation is:

        Predicted Revenue =
            Base Revenue + (ITE × Discount)

    This is a formulation layer. The exact revenue
    function can later be replaced by the team's
    final business model.
    """

    return base_revenue + (ite * discount)


# 4. Define Marketing Cost Function

def marketing_cost(discount, base_revenue):
    """
    Estimate marketing/discount cost.

    Here discount is represented as a fraction.

    Example:
        revenue = 1000
        discount = 0.10

        cost = 1000 × 0.10 = 100
    """

    return discount * base_revenue


# 5. Optimization Objective

def total_predicted_revenue(discounts, base_revenue, ite):
    """
    Calculate total predicted revenue for all customers.
    """

    revenues = predicted_revenue(
        discounts,
        base_revenue,
        ite
    )

    return np.sum(revenues)


# 6. Budget Constraint

def total_marketing_cost(discounts, base_revenue):
    """
    Calculate total marketing cost.
    """

    costs = marketing_cost(
        discounts,
        base_revenue
    )

    return np.sum(costs)


def budget_constraint(discounts, base_revenue):
    """
    Budget constraint:

        Total Marketing Cost <= Budget
    """

    return BUDGET - total_marketing_cost(
        discounts,
        base_revenue
    )

# 7. Discount Bounds

def get_discount_bounds(number_of_customers):
    """
    Define:

        0 <= discount_i <= MAX_DISCOUNT
    """

    return [
        (0.0, MAX_DISCOUNT)
        for _ in range(number_of_customers)
    ]


# 8. Optimization Problem Summary


def print_optimization_problem():
    """
    Display the mathematical formulation.
    """

    print("PRESCRIPTIVE OPTIMIZATION PROBLEM")
   

    print("\nObjective:")
    print("Maximize total predicted revenue")

    print("\nMathematical Form:")
    print("max Σ R_i(d_i)")

    print("\nSubject to:")
    print("Σ C_i(d_i) <= Budget")
    print("0 <= d_i <= Maximum Discount")

    print("\nConfiguration:")
    print(f"Budget = {BUDGET}")
    print(f"Maximum Discount = {MAX_DISCOUNT}")


# 9. Main


if __name__ == "__main__":
    print_optimization_problem()
