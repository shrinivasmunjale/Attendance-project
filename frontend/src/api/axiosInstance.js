import axios from "axios";

const instance = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

// Attach JWT token to every request
instance.interceptors.request.use((config) => {
  try {
    const stored = localStorage.getItem("auth-storage");
    if (stored) {
      const parsed = JSON.parse(stored);
      // Zustand persist wraps state under { state: { token: ... } }
      const token = parsed?.state?.token ?? parsed?.token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
  } catch (e) {
    console.warn("Could not read auth token:", e);
  }
  return config;
});

// Handle 401 globally
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth-storage");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default instance;
