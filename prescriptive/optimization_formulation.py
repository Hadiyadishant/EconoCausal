"""
Week 3 - Day 1
Prescriptive Optimization Formulation

Owner: Dishant

Purpose:
Define the mathematical optimization problem for personalized
discount allocation.

The actual customer-level revenue and cost values are NOT generated
here. They come directly from Princy's prepared optimization input.

Decision:
    Choose exactly one discount level for each customer.

Objective:
    Maximize total predicted revenue.

Constraint:
    Total marketing cost must not exceed the available budget.

Discount levels:
    Taken directly from Princy's prepared input data.
"""

import numpy as np


# Configuration

BUDGET = 5000.0

# Mathematical formulation

def print_optimization_problem():
    """
    Print the mathematical formulation used by the optimizer.
    """

    print("=" * 60)
    print("PRESCRIPTIVE OPTIMIZATION PROBLEM")
    print("=" * 60)

    print("\nDecision variables:")
    print("x[i,j] = 1 if discount level j is assigned to customer i")
    print("x[i,j] = 0 otherwise")

    print("\nObjective:")
    print(
        "Maximize Σ Σ revenue[i,j] × x[i,j]"
    )

    print("\nSubject to:")

    print(
        "1. Each customer receives exactly one discount:"
    )

    print(
        "   Σ x[i,j] = 1  for every customer i"
    )

    print(
        "\n2. Total marketing cost must not exceed the budget:"
    )

    print(
        "   Σ Σ cost[i,j] × x[i,j] <= Budget"
    )

    print(
        "\n3. Decision variables are binary:"
    )

    print(
        "   x[i,j] ∈ {0,1}"
    )

    print("\nConfiguration:")
    print(f"Budget = ₹{BUDGET:.2f}")


if __name__ == "__main__":
    print_optimization_problem()