import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';

// Mock DynamoDB
const mockSend = vi.fn();
vi.mock('@aws-sdk/client-dynamodb', () => ({
  DynamoDBClient: class { constructor() {} },
}));
vi.mock('@aws-sdk/lib-dynamodb', () => ({
  DynamoDBDocumentClient: { from: () => ({ send: mockSend }) },
  GetCommand: class { input: unknown; constructor(input: unknown) { this.input = input; } },
}));
vi.mock('aws-amplify/auth', () => ({
  fetchAuthSession: vi.fn().mockResolvedValue({
    credentials: { accessKeyId: 'test', secretAccessKey: 'test', sessionToken: 'test' },
  }),
}));

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
    mockSend.mockReset();
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

  it('fetches from DynamoDB when session param present', async () => {
    setSearch({ from: 'planner', session: 'abc123' });
    mockSend.mockResolvedValueOnce({
      Item: {
        project_name: 'DDB Project',
        description: 'desc',
        architecture: 'Microservices',
        tech_stack: { backend: 'Lambda' },
        requirements: { users: '10K', uptime: '99.9%', dataSize: '5GB' },
      },
    });
    const { result } = renderHook(() => usePlannerImport());
    await waitFor(() => expect(result.current.plannerData).not.toBeNull());
    expect(result.current.plannerData?.projectName).toBe('DDB Project');
    expect(result.current.plannerData?.architecture).toBe('Microservices');
  });

  it('falls back to prompt parsing when DynamoDB returns no item', async () => {
    const prompt = 'Project: Fallback App\nArchitecture: Monolith';
    setSearch({ from: 'planner', session: 'bad-session', prompt });
    mockSend.mockResolvedValueOnce({ Item: undefined });
    const { result } = renderHook(() => usePlannerImport());
    await waitFor(() => expect(result.current.plannerData).not.toBeNull());
    expect(result.current.plannerData?.projectName).toBe('Fallback App');
  });

  it('falls back to prompt parsing when DynamoDB throws', async () => {
    const prompt = 'App: Error App';
    setSearch({ from: 'planner', session: 'err', prompt });
    mockSend.mockRejectedValueOnce(new Error('AccessDeniedException'));
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
