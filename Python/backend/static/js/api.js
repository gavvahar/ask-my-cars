function buildQueryString(filters) {
  const params = new URLSearchParams();
  if (filters.makes !== undefined) {
    params.append("makes", filters.makes.join(","));
  }
  if (filters.year_min !== undefined) {
    params.append("year_min", filters.year_min);
  }
  if (filters.year_max !== undefined) {
    params.append("year_max", filters.year_max);
  }
  if (filters.fuel_types !== undefined) {
    params.append("fuel_types", filters.fuel_types.join(","));
  }
  return params.toString();
}

async function handleResponse(response) {
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Request failed (${response.status}): ${body}`);
  }
  return response.json();
}

export async function getFilterOptions() {
  const response = await fetch("/api/filters/options");
  return handleResponse(response);
}

export async function getDashboard(filters = {}) {
  const query = buildQueryString(filters);
  const response = await fetch(`/api/dashboard${query ? `?${query}` : ""}`);
  return handleResponse(response);
}

export async function postAiSummary(filters = {}) {
  const query = buildQueryString(filters);
  const response = await fetch(`/api/ai-summary${query ? `?${query}` : ""}`, {
    method: "POST",
  });
  return handleResponse(response);
}
