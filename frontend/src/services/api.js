const API_URL = "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  let response;

  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
  } catch (error) {
    throw new Error(
      `Unable to reach the EconoCausal API. Make sure the FastAPI server is running at ${API_URL}.`
    );
  }

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        `API request failed (HTTP ${response.status}).`
    );
  }

  return data;
}


// =========================================================
// HEALTH
// =========================================================

export async function getHealth() {
  return request("/health");
}


// =========================================================
// DATASET
// =========================================================

export async function uploadDataset(fileName, data) {
  return request("/dataset/upload", {
    method: "POST",
    body: JSON.stringify({
      file_name: fileName,
      data,
    }),
  });
}


export async function getDatasetStatus() {
  return request("/dataset/status");
}


// =========================================================
// INSIGHTS
// =========================================================

export async function getInsights() {
  return request("/insights");
}


// =========================================================
// ITE PREDICTION
// =========================================================

export async function predictITE(customers) {
  return request("/predict", {
    method: "POST",
    body: JSON.stringify({
      customers,
    }),
  });
}


// =========================================================
// BUDGET
// =========================================================

export async function getBudget() {
  return request("/budget");
}


export async function optimizeBudget(
  totalBudget,
  maxCustomers = null
) {
  return request("/optimize", {
    method: "POST",
    body: JSON.stringify({
      total_budget: Number(totalBudget),

      max_customers:
        maxCustomers === "" ||
        maxCustomers === null
          ? null
          : Number(maxCustomers),
    }),
  });
}


// =========================================================
// PRESCRIPTION
// =========================================================

export async function getPrescription(
  customerId = null
) {
  const endpoint =
    customerId !== null &&
    customerId !== ""
      ? `/prescription?customer_id=${encodeURIComponent(
          customerId
        )}`
      : "/prescription";

  return request(endpoint);
}


// =========================================================
// DRIFT MONITORING
// =========================================================

export async function checkDrift(data) {
  return request("/drift", {
    method: "POST",
    body: JSON.stringify({
      data,
    }),
  });
}


export default API_URL;