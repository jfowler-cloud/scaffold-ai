import { describe, it, expect } from 'vitest';
import { BACKEND_URL } from '../lib/config';

describe('config', () => {
  it('should export a BACKEND_URL string', () => {
    expect(typeof BACKEND_URL).toBe('string');
    expect(BACKEND_URL.length).toBeGreaterThan(0);
  });

  it('should default to localhost:8001', () => {
    // In test env no VITE_ vars are set, so falls back to default
    expect(BACKEND_URL).toBe('http://localhost:8001');
  });
});
