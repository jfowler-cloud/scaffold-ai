import { describe, it, expect, vi, beforeEach } from 'vitest';
import { POST } from '../app/api/chat/route';
import { NextRequest } from 'next/server';

// Mock fetch
global.fetch = vi.fn();

describe('Chat API Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const createRequest = (body: any) => {
    return new NextRequest('http://localhost:3000/api/chat', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  };

  it('should forward request to backend successfully', async () => {
    const mockResponse = {
      message: 'Architecture created',
      updated_graph: { nodes: [], edges: [] },
      generated_files: [],
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const request = createRequest({
      message: 'Create a Lambda function',
      graph: { nodes: [], edges: [] },
      iac_format: 'cdk',
    });

    const response = await POST(request);
    const data = await response.json();

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/chat',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
    );
    expect(data).toEqual(mockResponse);
  });

  it('should return friendly message on 502 error', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 502,
    });

    const request = createRequest({
      message: 'Test',
      graph: { nodes: [], edges: [] },
    });

    const response = await POST(request);
    const data = await response.json();

    expect(data.message).toContain('Backend service is not available');
  });

  it('should return friendly message on 503 error', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 503,
    });

    const request = createRequest({
      message: 'Test',
      graph: { nodes: [], edges: [] },
    });

    const response = await POST(request);
    const data = await response.json();

    expect(data.message).toContain('Backend service is not available');
  });

  it('should handle fetch TypeError gracefully', async () => {
    (global.fetch as any).mockRejectedValueOnce(new TypeError('fetch failed'));

    const request = createRequest({
      message: 'Test',
      graph: { nodes: [], edges: [] },
    });

    const response = await POST(request);
    const data = await response.json();

    expect(data.message).toContain('Cannot connect to the backend');
  });

  it('should default iac_format to cdk', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'OK' }),
    });

    const request = createRequest({
      message: 'Test',
      graph: { nodes: [], edges: [] },
    });

    await POST(request);

    const fetchCall = (global.fetch as any).mock.calls[0];
    const body = JSON.parse(fetchCall[1].body);
    expect(body.iac_format).toBe('cdk');
  });

  it('should pass custom iac_format', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'OK' }),
    });

    const request = createRequest({
      message: 'Test',
      graph: { nodes: [], edges: [] },
      iac_format: 'terraform',
    });

    await POST(request);

    const fetchCall = (global.fetch as any).mock.calls[0];
    const body = JSON.parse(fetchCall[1].body);
    expect(body.iac_format).toBe('terraform');
  });
});
