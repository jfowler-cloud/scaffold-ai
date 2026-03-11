import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { Chat } from '../components/Chat';
import { useChatStore, useGraphStore } from '../lib/store';

// Mock fetch
global.fetch = vi.fn();

// Mock JSZip for handleDownloadZip tests
const mockFile = vi.fn();
const mockGenerateAsync = vi.fn();
vi.mock('jszip', () => ({
  default: class {
    file = mockFile;
    generateAsync = mockGenerateAsync;
  },
}));

// Mock Cloudscape Textarea to expose onKeyDown with detail format
vi.mock('@cloudscape-design/components/textarea', () => ({
  default: ({ value, onChange, onKeyDown, placeholder, rows, disabled }: any) => (
    <textarea
      value={value ?? ''}
      placeholder={placeholder}
      rows={rows}
      disabled={disabled}
      onChange={e => onChange?.({ detail: { value: e.target.value } })}
      onKeyDown={e => onKeyDown?.({ detail: { key: e.key, shiftKey: e.shiftKey }, preventDefault: () => e.preventDefault() })}
    />
  ),
}));

// Mock Cloudscape Select to expose onChange
vi.mock('@cloudscape-design/components/select', () => ({
  default: ({ selectedOption, onChange, options, disabled }: any) => (
    <select
      value={selectedOption?.value ?? ''}
      disabled={disabled}
      onChange={e => {
        const opt = options?.find((o: any) => o.value === e.target.value);
        onChange?.({ detail: { selectedOption: opt } });
      }}
      data-testid="iac-select"
    >
      {options?.map((o: any) => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  ),
}));

/**
 * Helper: mock a fire-and-poll chat cycle.
 * First call returns execution_arn, second call returns SUCCEEDED with result.
 */
function mockChatFireAndPoll(result: { message?: string; updated_graph?: any; generated_files?: any[] }) {
  (global.fetch as any)
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ execution_arn: 'arn:aws:states:us-east-1:123:execution:test' }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'SUCCEEDED',
        message: result.message ?? '',
        updated_graph: result.updated_graph ?? null,
        generated_files: result.generated_files ?? [],
      }),
    });
}

/**
 * Helper: mock a fire-and-poll chat cycle that fails at the start.
 */
function mockChatStartFailure() {
  (global.fetch as any).mockRejectedValueOnce(new TypeError('Network error'));
}

/**
 * Helper: mock a fire-and-poll where start succeeds but poll returns FAILED.
 */
function mockChatPollFailure(error = 'Workflow failed') {
  (global.fetch as any)
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ execution_arn: 'arn:aws:states:us-east-1:123:execution:test' }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'FAILED', error }),
    });
}

/**
 * Helper: mock a start that returns non-ok response.
 */
function mockChatStartNonOk() {
  (global.fetch as any).mockResolvedValueOnce({
    ok: false,
    status: 502,
    json: async () => ({ detail: 'Bad gateway' }),
  });
}

describe('Chat', () => {
  beforeEach(() => {
    useChatStore.setState({ messages: [], isLoading: false, generatedFiles: [] });
    useGraphStore.setState({ nodes: [], edges: [], selectedNode: null });
    vi.clearAllMocks();
  });

  it('should render chat input and send button', () => {
    render(<Chat />);

    expect(screen.getByPlaceholderText(/describe your application architecture/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('should disable Generate Code button when no nodes exist', () => {
    render(<Chat />);

    const generateButton = screen.getByRole('button', { name: /generate code/i });
    expect(generateButton).toBeDisabled();
  });

  it('should enable Generate Code button when nodes exist', () => {
    useGraphStore.setState({
      nodes: [
        { id: '1', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }
      ],
      edges: [],
      selectedNode: null,
    });

    render(<Chat />);

    const generateButton = screen.getByRole('button', { name: /generate code/i });
    expect(generateButton).not.toBeDisabled();
  });

  it('should clear input after sending message', async () => {
    mockChatFireAndPoll({ message: 'Response' });

    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Create a Lambda function' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  it('should display error message on fetch failure', async () => {
    mockChatStartFailure();

    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument();
    });
  });

  it('should display error message on non-ok start response', async () => {
    mockChatStartNonOk();

    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument();
    });
  });

  it('should display error message on workflow failure', async () => {
    mockChatPollFailure();

    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument();
    });
  });

  it('should show loading spinner while processing', async () => {
    mockChatFireAndPoll({ message: 'Done' });

    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    expect(useChatStore.getState().isLoading).toBe(true);

    await waitFor(() => {
      expect(useChatStore.getState().isLoading).toBe(false);
    });
  });

  it('should update graph when response contains updated_graph', async () => {
    const updatedGraph = {
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Lambda', type: 'lambda' } }],
      edges: [{ id: 'e1', source: '1', target: '2' }],
    };
    mockChatFireAndPoll({ message: 'Created', updated_graph: updatedGraph });

    render(<Chat />);
    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Build a lambda' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(useGraphStore.getState().nodes.length).toBe(1);
    });
  });

  it('should save generated files when response contains them', async () => {
    mockChatFireAndPoll({
      message: 'Generated',
      generated_files: [{ path: 'lib/stack.ts', content: 'code' }],
    });

    render(<Chat />);
    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Generate code' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(useChatStore.getState().generatedFiles.length).toBe(1);
    });
  });

  it('should show security failed banner when response contains FAILED', async () => {
    mockChatFireAndPoll({
      message: 'Security Review: FAILED - issues found',
    });

    render(<Chat />);
    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Check security' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/security review failed/i)).toBeInTheDocument();
    });
  });

  it('should call generate code endpoint when Generate Code clicked', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [],
      selectedNode: null,
    });
    mockChatFireAndPoll({ message: 'Code generated', generated_files: [{ path: 'a.ts', content: 'x' }] });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /generate code/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/chat'),
        expect.objectContaining({ method: 'POST' })
      );
    });
  });

  it('should show error when generate code fails', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [],
      selectedNode: null,
    });
    mockChatStartNonOk();

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /generate code/i }));

    await waitFor(() => {
      expect(screen.getByText(/error generating code/i)).toBeInTheDocument();
    });
  });

  it('should call security autofix endpoint when Fix Security clicked', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [],
      selectedNode: null,
    });
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        updated_graph: { nodes: [{ id: '1', data: { type: 'lambda' } }], edges: [] },
        changes: ['Added encryption'],
        security_score: { percentage: 95 },
      }),
    });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /fix security/i }));

    await waitFor(() => {
      expect(screen.getByText(/security improvements applied/i)).toBeInTheDocument();
    });
  });

  it('should show no issues message when security fix returns no changes', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [],
      selectedNode: null,
    });
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ updated_graph: null, changes: [], security_score: null }),
    });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /fix security/i }));

    await waitFor(() => {
      expect(screen.getByText(/no security issues found/i)).toBeInTheDocument();
    });
  });

  it('should show error when security fix fails', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [],
      selectedNode: null,
    });
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /fix security/i }));

    await waitFor(() => {
      expect(screen.getByText(/security fix error/i)).toBeInTheDocument();
    });
  });

  it('should open deploy modal when Deploy clicked', () => {
    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /deploy to aws/i }));
    expect(screen.getByText(/coming soon/i)).toBeInTheDocument();
  });

  it('should auto-submit with plannerData', async () => {
    mockChatFireAndPoll({
      message: 'Architecture created',
      updated_graph: { nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'L', type: 'lambda' } }], edges: [] },
    });

    render(<Chat plannerData={{ description: 'Build a serverless API' }} />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/chat'),
        expect.objectContaining({
          body: expect.stringContaining('Build a serverless API'),
        })
      );
    });
  });

  it('should auto-submit with structured plannerData fields', async () => {
    mockChatFireAndPoll({ message: 'Architecture created' });

    render(
      <Chat plannerData={{
        projectName: 'My App',
        description: 'Build a serverless API',
        architecture: 'Full Serverless',
        techStack: { frontend: 'React', backend: 'Lambda' },
        requirements: { users: '1K-10K', uptime: '99.9%', dataSize: '<1GB' },
      }} />
    );

    await waitFor(() => {
      const body = (global.fetch as any).mock.calls[0][1].body;
      expect(body).toContain('My App');
      expect(body).toContain('Full Serverless');
      expect(body).toContain('React');
      expect(body).toContain('Lambda');
      expect(body).toContain('1K-10K');
    });
  });

  it('should include review findings in planner auto-submit', async () => {
    mockChatFireAndPoll({ message: 'Architecture created' });

    render(
      <Chat plannerData={{
        projectName: 'My App',
        description: 'Build a serverless API',
        architecture: '',
        techStack: {},
        requirements: { users: '', uptime: '', dataSize: '' },
        reviewFindings: [{ category: 'Security', findings: ['No auth'], recommendations: ['Add Cognito'], risk_level: 'critical' }],
        reviewSummary: 'Needs auth',
      }} />
    );

    await waitFor(() => {
      const body = (global.fetch as any).mock.calls[0][1].body;
      expect(body).toContain('critical/high');
      expect(body).toContain('Needs auth');
    });
  });

  it('should handle plannerData fetch error', async () => {
    mockChatStartFailure();

    render(<Chat plannerData={{ description: 'Build something' }} />);

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument();
    });
  });

  it('should show welcome message when no messages', () => {
    render(<Chat />);
    expect(screen.getByText(/welcome to scaffold ai/i)).toBeInTheDocument();
  });

  it('should handle Mark Resolved button in security banner', async () => {
    // First trigger security failure
    mockChatFireAndPoll({
      message: 'Security Review: FAILED - issues found',
    });

    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [],
      selectedNode: null,
    });

    render(<Chat />);
    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Check security' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/security review failed/i)).toBeInTheDocument();
    });

    // Now click Mark Resolved — should call handleGenerateCode(true)
    mockChatFireAndPoll({ message: 'Code generated' });
    fireEvent.click(screen.getByRole('button', { name: /mark resolved/i }));

    await waitFor(() => {
      // 2 fire-and-poll cycles = 4 fetch calls total
      expect(global.fetch).toHaveBeenCalledTimes(4);
    });
  });

  it('should close deploy modal when Got it clicked', () => {
    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /deploy to aws/i }));
    expect(screen.getByText(/coming soon/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /got it/i }));
  });

  it('should not submit when input is empty', () => {
    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /send/i }));
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('should not generate code when already loading', () => {
    useChatStore.setState({ isLoading: true });
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [],
    });
    render(<Chat />);
    // Generate Code button should be disabled when loading
    expect(screen.getByRole('button', { name: /generate code/i })).toBeDisabled();
  });

  it('should download zip when files exist', async () => {
    mockGenerateAsync.mockResolvedValueOnce(new Blob(['zip']));
    const createObjectURL = vi.fn(() => 'blob:url');
    const revokeObjectURL = vi.fn();
    Object.defineProperty(global, 'URL', {
      value: { createObjectURL, revokeObjectURL },
      writable: true,
    });

    useChatStore.setState({
      generatedFiles: [{ path: 'lib/stack.ts', content: 'code here' }],
    });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /download zip/i }));

    await waitFor(() => {
      expect(screen.getByText(/downloaded 1 files as zip/i)).toBeInTheDocument();
    });
  });

  it('should show error when zip download fails', async () => {
    mockGenerateAsync.mockRejectedValueOnce(new Error('zip failed'));

    useChatStore.setState({
      generatedFiles: [{ path: 'a.ts', content: 'x' }],
    });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /download zip/i }));

    await waitFor(() => {
      expect(screen.getByText(/download failed.*zip failed/i)).toBeInTheDocument();
    });
  });

  it('should not download zip when no files', () => {
    useChatStore.setState({ generatedFiles: [] });
    render(<Chat />);
    expect(screen.getByRole('button', { name: /download zip/i })).toBeDisabled();
  });

  it('should handle security fix with normalized nodes', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [],
      selectedNode: null,
    });
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        updated_graph: {
          nodes: [{ id: '1', data: { type: 'lambda', label: 'Secured Lambda' } }],
          edges: [],
        },
        changes: ['Added WAF', 'Enabled encryption'],
        security_score: { percentage: 100 },
      }),
    });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /fix security/i }));

    await waitFor(() => {
      expect(screen.getByText(/security improvements applied/i)).toBeInTheDocument();
    });
  });

  it('should submit on Enter key via textarea', async () => {
    mockChatFireAndPoll({ message: 'Response' });

    render(<Chat />);
    const textarea = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  it('should not submit on Shift+Enter', async () => {
    render(<Chat />);
    const textarea = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });

    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('should change IaC format via select', () => {
    render(<Chat />);
    const select = screen.getByTestId('iac-select');
    fireEvent.change(select, { target: { value: 'terraform' } });
    expect(select).toHaveValue('terraform');
  });
});
