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
  } catch (err) {
    // Network-level failure (server not running, CORS blocked, offline, etc.)
    throw new Error(
      "Unable to reach the EconoCausal API. Make sure the FastAPI server is running at " +
        API_URL +
        "."
    );
  }

  let data = null;
  try {
    data = await response.json();
  } catch (err) {
    // Response wasn't JSON at all
    data = null;
  }

  if (!response.ok) {
    throw new Error(
      data?.detail || `API request failed (HTTP ${response.status}).`
    );
  }

  return data;
}

export async function getHealth() {
  return request("/health");
}

export async function getPrescription(customerId = null) {
  const endpoint = customerId
    ? `/prescription?customer_id=${customerId}`
    : "/prescription";

  return request(endpoint);
}

export async function predictITE(customers) {
  return request("/predict", {
    method: "POST",
    body: JSON.stringify({ customers }),
  });
}

export async function checkDrift(data) {
  return request("/drift", {
    method: "POST",
    body: JSON.stringify({ data }),
  });
}

export default API_URL;
