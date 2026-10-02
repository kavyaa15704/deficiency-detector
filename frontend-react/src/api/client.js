import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const client = axios.create({ baseURL: API_URL });

export function setAuthToken(token) {
  if (token) {
    client.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete client.defaults.headers.common.Authorization;
  }
}

export async function registerUser(username, email, password) {
  const { data } = await client.post("/register", { username, email, password });
  return data;
}

export async function loginUser(username, password) {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);
  const { data } = await client.post("/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function fetchSymptoms() {
  const { data } = await client.get("/symptoms");
  return data.symptoms;
}

export async function predictDeficiencies(symptoms) {
  const { data } = await client.post("/predict", { symptoms });
  return data;
}

export async function fetchRecentPredictions(limit = 10) {
  const { data } = await client.get("/predictions/recent", { params: { limit } });
  return data.predictions;
}

export function apiErrorMessage(error) {
  return error?.response?.data?.detail || "Something went wrong. Is the API running?";
}
