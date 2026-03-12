/**
 * Centralized configuration.
 * BACKEND_URL kept for backward compatibility with tests.
 */
export const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL ||
  import.meta.env.VITE_API_URL ||
  "http://localhost:8001";
