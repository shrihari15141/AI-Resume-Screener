const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export function getToken() {
  return null;
}

export function setSession() {
  clearSession();
}

export function clearSession() {
  localStorage.removeItem("resumeai_token");
  localStorage.removeItem("resumeai_user");
}

export function getUser() {
  return {
    username: "Demo Recruiter",
    email: "recruiter@example.com"
  };
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof data === "string" ? data : data.message || "Request failed.";
    throw new Error(message);
  }
  return data;
}

export const api = {
  login: (payload) => request("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  register: (payload) => request("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  me: () => request("/auth/me"),
  jobs: () => request("/jobs"),
  createJob: (payload) => request("/jobs", { method: "POST", body: JSON.stringify(payload) }),
  updateJob: (id, payload) => request(`/jobs/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  getJob: (id) => request(`/jobs/${id}`),
  analyzeJob: (id) => request(`/jobs/${id}/analyze`, { method: "POST", body: JSON.stringify({}) }),
  closeJob: (id) => request(`/jobs/${id}/close`, { method: "POST", body: JSON.stringify({}) }),
  deleteJob: (id) => request(`/jobs/${id}`, { method: "DELETE" }),
  candidates: (params = {}) => request(`/candidates?${new URLSearchParams(params)}`),
  candidate: (id) => request(`/candidates/${id}`),
  updateCandidateStatus: (id, status) =>
    request(`/candidates/${id}/status`, { method: "PUT", body: JSON.stringify({ status }) }),
  compareCandidates: (candidate_ids) =>
    request("/candidates/compare", { method: "POST", body: JSON.stringify({ candidate_ids }) }),
  uploadResumes: (formData) => request("/screening/upload", { method: "POST", body: formData }),
  batchStatus: (batchId) => request(`/screening/${batchId}/status`),
  batchResults: (batchId) => request(`/screening/${batchId}/results`),
  reports: () => request("/reports"),
  exportCsvUrl: (jobId) => `${API_URL}/export/csv${jobId ? `?job_id=${jobId}` : ""}`,
  exportJsonUrl: (jobId) => `${API_URL}/export/json${jobId ? `?job_id=${jobId}` : ""}`
};

export { API_URL };
