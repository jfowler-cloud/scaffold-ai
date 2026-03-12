import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock aws-amplify/auth
vi.mock('aws-amplify/auth', () => ({
  fetchAuthSession: vi.fn().mockResolvedValue({
    credentials: {
      accessKeyId: 'AKID',
      secretAccessKey: 'SECRET',
      sessionToken: 'TOKEN',
    },
  }),
}));

// Mock SFN client
const mockSFNSend = vi.fn();
vi.mock('@aws-sdk/client-sfn', () => {
  return {
    SFNClient: class { send = mockSFNSend },
    StartExecutionCommand: class { constructor(public input: any) {} },
  };
});

// Mock Lambda client
const mockLambdaSend = vi.fn();
vi.mock('@aws-sdk/client-lambda', () => {
  return {
    LambdaClient: class { send = mockLambdaSend },
    InvokeCommand: class { constructor(public input: any) {} },
  };
});

describe('api', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should start execution and poll until success', async () => {
    mockSFNSend.mockResolvedValueOnce({
      executionArn: 'arn:aws:states:us-east-1:123:execution:test',
    });
    mockLambdaSend.mockResolvedValueOnce({
      Payload: new TextEncoder().encode(JSON.stringify({
        statusCode: 200,
        body: JSON.stringify({
          status: 'SUCCEEDED',
          message: 'Done',
          updated_graph: { nodes: [], edges: [] },
          generated_files: [],
        }),
      })),
    });

    const { sendChat } = await import('../lib/api');
    const result = await sendChat('Build a lambda', { nodes: [], edges: [] }, 'cdk');

    expect(result.message).toBe('Done');
    expect(mockSFNSend).toHaveBeenCalledTimes(1);
    expect(mockLambdaSend).toHaveBeenCalledTimes(1);
  });

  it('should throw on workflow failure', async () => {
    mockSFNSend.mockResolvedValueOnce({
      executionArn: 'arn:aws:states:us-east-1:123:execution:test',
    });
    mockLambdaSend.mockResolvedValueOnce({
      Payload: new TextEncoder().encode(JSON.stringify({
        statusCode: 200,
        body: JSON.stringify({
          status: 'FAILED',
          error: 'Something broke',
        }),
      })),
    });

    const { sendChat } = await import('../lib/api');
    await expect(sendChat('Build a lambda', null, 'cdk')).rejects.toThrow('Something broke');
  });

  it('should export startChatExecution and pollExecutionStatus', async () => {
    const api = await import('../lib/api');
    expect(typeof api.startChatExecution).toBe('function');
    expect(typeof api.pollExecutionStatus).toBe('function');
    expect(typeof api.sendChat).toBe('function');
  });
});
