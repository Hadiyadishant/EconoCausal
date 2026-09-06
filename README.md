````markdown
# EconoCausal

EconoCausal is a marketing decision-support system that uses causal inference and prescriptive optimization to estimate the impact of discounts and recommend customer-level discount decisions.

## Project Architecture

```text
Historical Customer Data
          ↓
Data Preprocessing
          ↓
DoWhy DAG
          ↓
EconML Double Machine Learning
          ↓
Individual Treatment Effect (ITE)
          ↓
Uplift / Qini Analysis
          ↓
SciPy Optimization
          ↓
Optimal Discount Prescription
          ↓
FastAPI REST API
          ↓
Drift Detection
          ↓
React Dashboard
````

## Backend API

The backend is implemented using FastAPI.

### Health Check

```text
GET /health
```

Returns:

```json
{
    "status": "healthy"
}
```

### Causal Prediction

```text
POST /predict
```

The endpoint receives customer features and uses the causal engine to calculate Individual Treatment Effects (ITE).

### Drift Detection

```text
POST /drift
```

The endpoint receives customer data and passes it to the monitoring drift detector.

The drift detector compares incoming customer data with the reference dataset and returns:

* Overall drift status
* Drift threshold
* Per-variable statistical results

Example response:

```json
{
    "status": "success",
    "drift": {
        "overall_status": "NO DRIFT",
        "threshold": 0.05,
        "per_variable": {}
    }
}
```

## Causal Model

The causal pipeline uses EconML CausalForestDML.

The treatment variable is based on discount usage:

```text
T = discount > 0
```

The outcome variable is:

```text
Y = purchase
```

Customer features include:

```text
age
income
previous_purchases
campaign_response
customer_tenure_days
avg_basket_size
```

The trained causal model estimates the Individual Treatment Effect (ITE) using:

```text
model.effect(X)
```

## Optimization

The prescriptive optimization module uses predicted revenue/uplift to select customer-level discount assignments.

The optimization is subject to business constraints including:

* Marketing budget ≤ ₹5,000
* One discount per customer
* Allowed discount levels
* Revenue maximization objective

The final output is the recommended discount prescription for each customer.

## Drift Monitoring

The monitoring module compares new customer data against reference data.

Statistical tests are applied to monitored numerical and categorical variables.

The configured drift threshold is:

```text
0.05
```

The monitoring system can return:

```text
NO DRIFT
```

or:

```text
DRIFT DETECTED
```

A drift warning indicates that the current customer-data distribution differs significantly from the reference distribution and should be reviewed before relying on model predictions.

## Running the Backend

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

Start FastAPI:

```powershell
uvicorn api.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## Running Tests

Run all tests:

```powershell
pytest -v
```

Run drift tests:

```powershell
pytest tests/test_drift.py -v
```

Run drift API tests:

```powershell
pytest tests/test_drift_api.py -v
```

## Running the Frontend

Start the React frontend from the frontend directory using the project's configured npm command.

The dashboard provides interfaces for:

* Dataset upload
* Insights
* Budget configuration
* Prescription results
* Model/API results
* Drift monitoring warnings

```
```
