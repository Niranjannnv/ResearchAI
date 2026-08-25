import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: attach access token
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("researchai_access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor: handle 401 and refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      if (typeof window !== "undefined") {
        const refreshToken = localStorage.getItem("researchai_refresh_token");
        if (refreshToken) {
          try {
            const { data } = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
              refresh_token: refreshToken,
            });
            localStorage.setItem("researchai_access_token", data.access_token);
            localStorage.setItem("researchai_refresh_token", data.refresh_token);
            originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
            return api(originalRequest);
          } catch (refreshErr) {
            localStorage.removeItem("researchai_access_token");
            localStorage.removeItem("researchai_refresh_token");
            window.location.href = "/login";
          }
        }
      }
    }
    return Promise.reject(error);
  }
);
