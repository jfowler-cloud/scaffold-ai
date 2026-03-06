import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { usePlannerImport } from '../lib/usePlannerImport';

const setSearch = (params: Record<string, string>) => {
  const search = new URLSearchParams(params).toString();
  Object.defineProperty(window, 'location', {
    value: { search: search ? `?${search}` : '' },
    writable: true,
  });
};

describe('usePlannerImport', () => {
  beforeEach(() => {
    setSearch({});
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('returns null plannerData when not from planner', () => {
    const { result } = renderHook(() => usePlannerImport());
    expect(result.current.plannerData).toBeNull();
    expect(result.current.isFromPlanner).toBe(false);
  });

  it('parses prompt when from=planner and prompt param present', async () => {
    const prompt = 'Project: My App\nArchitecture: Serverless\nTech Stack: frontend: React\nUsers: 1K | Uptime: 99% | Data: 1GB';
    setSearch({ from: 'planner', prompt });
    const { result } = renderHook(() => usePlannerImport());
    await waitFor(() => expect(result.current.plannerData).not.toBeNull());
    expect(result.current.plannerData?.projectName).toBe('My App');
    expect(result.current.plannerData?.architecture).toBe('Serverless');
    expect(result.current.isFromPlanner).toBe(true);
  });

  it('fetches from API when session param present', async () => {
    setSearch({ from: 'planner', session: 'abc123' });
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        project_name: 'API Project',
        description: 'desc',
        architecture: 'Microservices',
        tech_stack: { backend: 'Lambda' },
        requirements: { users: '10K', uptime: '99.9%', dataSize: '5GB' },
      }),
    });
    const { result } = renderHook(() => usePlannerImport());
    await waitFor(() => expect(result.current.plannerData).not.toBeNull());
    expect(result.current.plannerData?.projectName).toBe('API Project');
    expect(result.current.plannerData?.architecture).toBe('Microservices');
  });

  it('falls back to prompt parsing when API fetch fails', async () => {
    const prompt = 'Project: Fallback App\nArchitecture: Monolith';
    setSearch({ from: 'planner', session: 'bad-session', prompt });
    (global.fetch as any).mockResolvedValueOnce({ ok: false });
    const { result } = renderHook(() => usePlannerImport());
    await waitFor(() => expect(result.current.plannerData).not.toBeNull());
    expect(result.current.plannerData?.projectName).toBe('Fallback App');
  });

  it('falls back to prompt parsing when fetch throws', async () => {
    const prompt = 'App: Error App';
    setSearch({ from: 'planner', session: 'err', prompt });
    (global.fetch as any).mockRejectedValueOnce(new Error('network'));
    const { result } = renderHook(() => usePlannerImport());
    await waitFor(() => expect(result.current.plannerData).not.toBeNull());
    expect(result.current.plannerData?.projectName).toBe('Error App');
  });

  it('uses default project name when no project line found', async () => {
    setSearch({ from: 'planner', prompt: 'Just some description text' });
    const { result } = renderHook(() => usePlannerImport());
    await waitFor(() => expect(result.current.plannerData).not.toBeNull());
    expect(result.current.plannerData?.projectName).toBe('Imported Project');
  });

  it('parses tech stack key-value pairs', async () => {
    setSearch({ from: 'planner', prompt: 'Project: Test\nTech Stack: frontend: React, backend: Lambda' });
    const { result } = renderHook(() => usePlannerImport());
    await waitFor(() => expect(result.current.plannerData).not.toBeNull());
    expect(result.current.plannerData?.techStack).toEqual({ frontend: 'React', backend: 'Lambda' });
  });

  it('parses requirements from pipe-separated line', async () => {
    setSearch({ from: 'planner', prompt: 'Project: Test\nUsers: 5K | Uptime: 99.5% | Data: 2GB' });
    const { result } = renderHook(() => usePlannerImport());
    await waitFor(() => expect(result.current.plannerData).not.toBeNull());
    expect(result.current.plannerData?.requirements.users).toBe('5K');
    expect(result.current.plannerData?.requirements.uptime).toBe('99.5%');
    expect(result.current.plannerData?.requirements.dataSize).toBe('2GB');
  });
});
