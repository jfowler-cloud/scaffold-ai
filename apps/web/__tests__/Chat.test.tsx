import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { Chat } from '../components/Chat';
import { useChatStore, useGraphStore } from '../lib/store';

// Mock the API module
const mockSendChat = vi.fn();
vi.mock('../lib/api', () => ({
  sendChat: (...args: any[]) => mockSendChat(...args),
}));

// Mock the security-autofix module
const mockAnalyzeAndFix = vi.fn();
const mockGetSecurityScore = vi.fn();
vi.mock('../lib/security-autofix', () => ({
  analyzeAndFix: (...args: any[]) => mockAnalyzeAndFix(...args),
  getSecurityScore: (...args: any[]) => mockGetSecurityScore(...args),
}));

// Mock JSZip for handleDownloadZip tests
const mockFile = vi.fn();
const mockGenerateAsync = vi.fn();
vi.mock('jszip', () => ({
  default: class {
    file = mockFile;
    generateAsync = mockGenerateAsync;
  },
}));

// Mock react-markdown
vi.mock('react-markdown', () => ({
  default: ({ children }: any) => <span data-testid="markdown">{children}</span>,
}));

// Mock remark-gfm
vi.mock('remark-gfm', () => ({
  default: () => {},
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

// Mock Cloudscape Input for session rename
vi.mock('@cloudscape-design/components/input', () => ({
  default: ({ value, onChange, onBlur, onKeyDown, autoFocus }: any) => (
    <input
      value={value ?? ''}
      autoFocus={autoFocus}
      onChange={e => onChange?.({ detail: { value: e.target.value } })}
      onBlur={onBlur}
      onKeyDown={e => onKeyDown?.({ detail: { key: e.key } })}
      data-testid="rename-input"
    />
  ),
}));

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

  it('should render session sidebar with New Chat button', () => {
    render(<Chat />);
    expect(screen.getByRole('button', { name: /new chat/i })).toBeInTheDocument();
  });

  it('should show empty state in session sidebar', () => {
    render(<Chat />);
    expect(screen.getByText(/no chat sessions yet/i)).toBeInTheDocument();
  });

  it('should create new session when New Chat clicked', () => {
    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /new chat/i }));
    // After creating, the "No chat sessions" message should be replaced by the new session
    expect(screen.queryByText(/no chat sessions yet/i)).not.toBeInTheDocument();
  });

  it('should disable Generate Code button when no nodes exist', () => {
    render(<Chat />);
    expect(screen.getByRole('button', { name: /generate code/i })).toBeDisabled();
  });

  it('should enable Generate Code button when nodes exist', () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [], selectedNode: null,
    });
    render(<Chat />);
    expect(screen.getByRole('button', { name: /generate code/i })).not.toBeDisabled();
  });

  it('should clear input after sending message', async () => {
    mockSendChat.mockResolvedValueOnce({ message: 'Response' });
    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Create a Lambda function' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => { expect(input).toHaveValue(''); });
  });

  it('should display error message on send failure', async () => {
    mockSendChat.mockRejectedValueOnce(new Error('Network error'));
    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument();
    });
  });

  it('should display error message on workflow failure', async () => {
    mockSendChat.mockRejectedValueOnce(new Error('Workflow failed'));
    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument();
    });
  });

  it('should show loading spinner while processing', async () => {
    mockSendChat.mockResolvedValueOnce({ message: 'Done' });
    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    expect(useChatStore.getState().isLoading).toBe(true);
    await waitFor(() => { expect(useChatStore.getState().isLoading).toBe(false); });
  });

  it('should update graph when response contains updated_graph', async () => {
    const updatedGraph = {
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Lambda', type: 'lambda' } }],
      edges: [{ id: 'e1', source: '1', target: '2' }],
    };
    mockSendChat.mockResolvedValueOnce({ message: 'Created', updated_graph: updatedGraph });

    render(<Chat />);
    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Build a lambda' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => { expect(useGraphStore.getState().nodes.length).toBe(1); });
  });

  it('should save generated files when response contains them', async () => {
    mockSendChat.mockResolvedValueOnce({
      message: 'Generated',
      generated_files: [{ path: 'lib/stack.ts', content: 'code' }],
    });

    render(<Chat />);
    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Generate code' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => { expect(useChatStore.getState().generatedFiles.length).toBe(1); });
  });

  it('should show security failed banner when response contains FAILED', async () => {
    mockSendChat.mockResolvedValueOnce({ message: 'Security Review: FAILED - issues found' });

    render(<Chat />);
    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Check security' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/security review failed/i)).toBeInTheDocument();
    });
  });

  it('should call sendChat when Generate Code clicked', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [], selectedNode: null,
    });
    mockSendChat.mockResolvedValueOnce({ message: 'Code generated', generated_files: [{ path: 'a.ts', content: 'x' }] });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /generate code/i }));

    await waitFor(() => {
      expect(mockSendChat).toHaveBeenCalledWith('generate code', expect.anything(), 'cdk');
    });
  });

  it('should show error when generate code fails', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [], selectedNode: null,
    });
    mockSendChat.mockRejectedValueOnce(new Error('Failed'));

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /generate code/i }));

    await waitFor(() => {
      expect(screen.getByText(/error generating code/i)).toBeInTheDocument();
    });
  });

  it('should call analyzeAndFix when Fix Security clicked', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [], selectedNode: null,
    });
    mockAnalyzeAndFix.mockReturnValueOnce({
      updatedGraph: { nodes: [{ id: '1', data: { type: 'lambda' } }], edges: [] },
      changes: ['Added encryption'],
    });
    mockGetSecurityScore.mockReturnValueOnce({ score: 95, maxScore: 100, percentage: 95 });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /fix security/i }));

    await waitFor(() => {
      expect(screen.getByText(/security improvements applied/i)).toBeInTheDocument();
    });
  });

  it('should show no issues message when security fix returns no changes', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [], selectedNode: null,
    });
    mockAnalyzeAndFix.mockReturnValueOnce({ updatedGraph: null, changes: [] });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /fix security/i }));

    await waitFor(() => {
      expect(screen.getByText(/no security issues found/i)).toBeInTheDocument();
    });
  });

  it('should show error when security fix throws', async () => {
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [], selectedNode: null,
    });
    mockAnalyzeAndFix.mockImplementationOnce(() => { throw new Error('fix failed'); });

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
    mockSendChat.mockResolvedValueOnce({
      message: 'Architecture created',
      updated_graph: { nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'L', type: 'lambda' } }], edges: [] },
    });

    render(<Chat plannerData={{ description: 'Build a serverless API' }} />);

    await waitFor(() => {
      expect(mockSendChat).toHaveBeenCalledWith(
        expect.stringContaining('Build a serverless API'),
        expect.anything(),
        'cdk',
      );
    });
  });

  it('should auto-submit with structured plannerData fields', async () => {
    mockSendChat.mockResolvedValueOnce({ message: 'Architecture created' });

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
      const userInput = mockSendChat.mock.calls[0][0];
      expect(userInput).toContain('My App');
      expect(userInput).toContain('Full Serverless');
      expect(userInput).toContain('React');
      expect(userInput).toContain('Lambda');
      expect(userInput).toContain('1K-10K');
    });
  });

  it('should include review findings in planner auto-submit', async () => {
    mockSendChat.mockResolvedValueOnce({ message: 'Architecture created' });

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
      const userInput = mockSendChat.mock.calls[0][0];
      expect(userInput).toContain('critical/high');
      expect(userInput).toContain('Needs auth');
    });
  });

  it('should handle plannerData fetch error', async () => {
    mockSendChat.mockRejectedValueOnce(new Error('Network error'));

    render(<Chat plannerData={{ description: 'Build something' }} />);

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument();
    });
  });

  it('should show welcome message when no messages', () => {
    render(<Chat />);
    expect(screen.getByText(/welcome to scaffold ai/i)).toBeInTheDocument();
  });

  it('should render keyboard shortcut hints in welcome', () => {
    render(<Chat />);
    expect(screen.getByText(/to focus input/i)).toBeInTheDocument();
  });

  it('should handle Mark Resolved button in security banner', async () => {
    // First trigger security failure
    mockSendChat.mockResolvedValueOnce({ message: 'Security Review: FAILED - issues found' });

    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [], selectedNode: null,
    });

    render(<Chat />);
    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Check security' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/security review failed/i)).toBeInTheDocument();
    });

    // Click Mark Resolved — should call sendChat again with skip_security_check
    mockSendChat.mockResolvedValueOnce({ message: 'Code generated' });
    fireEvent.click(screen.getByRole('button', { name: /mark resolved/i }));

    await waitFor(() => {
      expect(mockSendChat).toHaveBeenCalledTimes(2);
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
    expect(mockSendChat).not.toHaveBeenCalled();
  });

  it('should not generate code when already loading', () => {
    useChatStore.setState({ isLoading: true });
    useGraphStore.setState({
      nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'Test', type: 'lambda' } }],
      edges: [],
    });
    render(<Chat />);
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
      edges: [], selectedNode: null,
    });
    mockAnalyzeAndFix.mockReturnValueOnce({
      updatedGraph: {
        nodes: [{ id: '1', data: { type: 'lambda', label: 'Secured Lambda' } }],
        edges: [],
      },
      changes: ['Added WAF', 'Enabled encryption'],
    });
    mockGetSecurityScore.mockReturnValueOnce({ score: 100, maxScore: 100, percentage: 100 });

    render(<Chat />);
    fireEvent.click(screen.getByRole('button', { name: /fix security/i }));

    await waitFor(() => {
      expect(screen.getByText(/security improvements applied/i)).toBeInTheDocument();
    });
  });

  it('should submit on Enter key via textarea', async () => {
    mockSendChat.mockResolvedValueOnce({ message: 'Response' });

    render(<Chat />);
    const textarea = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });

    await waitFor(() => { expect(mockSendChat).toHaveBeenCalled(); });
  });

  it('should not submit on Shift+Enter', async () => {
    render(<Chat />);
    const textarea = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(textarea, { target: { value: 'Hello' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });

    expect(mockSendChat).not.toHaveBeenCalled();
  });

  it('should change IaC format via select', () => {
    render(<Chat />);
    const select = screen.getByTestId('iac-select');
    fireEvent.change(select, { target: { value: 'terraform' } });
    expect(select).toHaveValue('terraform');
  });

  it('should toggle sidebar visibility', () => {
    render(<Chat />);
    // Sidebar is open by default, find close button
    const closeBtn = screen.getByLabelText(/close sessions/i);
    fireEvent.click(closeBtn);
    // Sidebar collapsed, should show open button
    expect(screen.getByLabelText(/open sessions/i)).toBeInTheDocument();
  });

  it('should delete a session', async () => {
    render(<Chat />);
    // Create a session first
    fireEvent.click(screen.getByRole('button', { name: /new chat/i }));
    // The session should be visible - look for its delete button
    const deleteBtn = screen.getByTitle('Delete');
    fireEvent.click(deleteBtn);
    // After deleting, should show empty state again
    expect(screen.getByText(/no chat sessions yet/i)).toBeInTheDocument();
  });
});
