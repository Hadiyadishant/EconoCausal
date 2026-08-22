# EconoCausal

EconoCausal is a causal AI platform designed to estimate the causal impact of
marketing discounts on customer purchasing behavior.

The project combines causal inference, Double Machine Learning, uplift
analysis, and an interactive React dashboard to help identify customers who
are likely to benefit from a marketing treatment.

---

## Project Objective

The main business question is:

**What is the causal effect of giving a customer a discount on their probability**
**of purchasing?**

Traditional machine learning can identify correlations between customer
characteristics and purchases, but correlation does not necessarily imply
causation.

EconoCausal uses causal inference techniques to estimate the effect of a
discount while accounting for observed customer characteristics.

---

# Project Pipeline

The current project follows this causal ML workflow:

Historical Customer Data
        |
        v
Data Validation & Preprocessing
        |
        v
DoWhy Causal DAG
        |
        v
Causal Identification
        |
        v
EconML Double Machine Learning
        |
        v
Individual Treatment Effect (ITE)
        |
        v
ITE Validation
        |
        v
Qini / Uplift Analysis
        |
        v
React + Plotly Dashboard
        |
        v
Business Interpretation

Future stages will extend this pipeline with optimization, API integration,
and data-drift monitoring.

---

# Technology Stack

## Python / Causal ML

- Python
- Pandas
- NumPy
- Scikit-learn
- DoWhy
- EconML
- Random Forest
- Matplotlib
- Seaborn

## Frontend

- React
- Vite
- React Router
- Plotly
- react-plotly.js
- CSS

---

# Dataset

The project uses a cleaned mock retail dataset.

Dataset file:

```text
data/mockretaildatacleaned.csv