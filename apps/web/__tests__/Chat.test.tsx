import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { Chat } from '../components/Chat';
import { useChatStore, useGraphStore } from '../lib/store';

// Mock fetch
global.fetch = vi.fn();

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
});
