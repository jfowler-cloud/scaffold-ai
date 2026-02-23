/**
 * Centralized backend URL configuration.
 * Import BACKEND_URL from here instead of repeating the fallback chain in each component.
 */
export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8001";
