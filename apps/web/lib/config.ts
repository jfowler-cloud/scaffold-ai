// Frontend configuration
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || "http://localhost:8000";

// Validate URL format
if (!/^https?:\/\/.+/.test(BACKEND_URL)) {
  console.error("Invalid BACKEND_URL format:", BACKEND_URL);
}

export const config = {
  backendUrl: BACKEND_URL,
  apiTimeout: 60000, // 60 seconds
  retryAttempts: 3,
  retryDelay: 1000, // 1 second
} as const;

export default config;
