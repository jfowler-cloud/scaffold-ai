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
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Response', updated_graph: null, generated_files: [] }),
    });

    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Create a Lambda function' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  it('should display error message on fetch failure', async () => {
    (global.fetch as any).mockRejectedValueOnce(new TypeError('Network error'));

    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument();
    });
  });

  it('should display error message on 502/503 response', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 502,
    });

    render(<Chat />);

    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument();
    });
  });

  it('should show loading spinner while processing', async () => {
    (global.fetch as any).mockImplementationOnce(() =>
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => ({ message: 'Done', updated_graph: null, generated_files: [] }),
      }), 100))
    );

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
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Created', updated_graph: updatedGraph, generated_files: [] }),
    });

    render(<Chat />);
    const input = screen.getByPlaceholderText(/describe your application architecture/i);
    fireEvent.change(input, { target: { value: 'Build a lambda' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() => {
      expect(useGraphStore.getState().nodes.length).toBe(1);
    });
  });

  it('should save generated files when response contains them', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        message: 'Generated',
        updated_graph: null,
        generated_files: [{ path: 'lib/stack.ts', content: 'code' }],
      }),
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
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        message: 'Security Review: FAILED - issues found',
        updated_graph: null,
        generated_files: [],
      }),
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
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Code generated', generated_files: [{ path: 'a.ts', content: 'x' }] }),
    });

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
    (global.fetch as any).mockResolvedValueOnce({ ok: false, status: 500 });

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
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        message: 'Architecture created',
        updated_graph: { nodes: [{ id: '1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'L', type: 'lambda' } }], edges: [] },
        generated_files: [],
      }),
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

  it('should handle plannerData fetch error', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('fail'));

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
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        message: 'Security Review: FAILED - issues found',
        updated_graph: null,
        generated_files: [],
      }),
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
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Code generated', generated_files: [] }),
    });
    fireEvent.click(screen.getByRole('button', { name: /mark resolved/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
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
});
