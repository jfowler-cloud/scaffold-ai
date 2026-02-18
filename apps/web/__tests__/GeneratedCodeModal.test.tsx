import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GeneratedCodeModal } from '../components/GeneratedCodeModal';
import { useChatStore } from '../lib/store';

describe('GeneratedCodeModal', () => {
  const mockOnDismiss = () => {};

  beforeEach(() => {
    useChatStore.setState({ messages: [], isLoading: false, generatedFiles: [] });
  });

  it('should show empty state when no files generated', () => {
    render(<GeneratedCodeModal visible={true} onDismiss={mockOnDismiss} />);
    
    expect(screen.getByText(/no code generated yet/i)).toBeInTheDocument();
    expect(screen.getByText(/click the "generate code" button/i)).toBeInTheDocument();
  });

  it('should render tabs when files are present', () => {
    useChatStore.setState({
      messages: [],
      isLoading: false,
      generatedFiles: [
        { path: 'lib/stack.ts', content: 'export class Stack {}' },
        { path: 'bin/app.ts', content: 'new Stack()' },
      ],
    });

    render(<GeneratedCodeModal visible={true} onDismiss={mockOnDismiss} />);
    
    expect(screen.getByText('stack.ts')).toBeInTheDocument();
    expect(screen.getByText('app.ts')).toBeInTheDocument();
  });

  it('should display file content in code block', () => {
    const content = 'export class MyStack {}';
    useChatStore.setState({
      messages: [],
      isLoading: false,
      generatedFiles: [
        { path: 'lib/stack.ts', content },
      ],
    });

    render(<GeneratedCodeModal visible={true} onDismiss={mockOnDismiss} />);
    
    expect(screen.getByText(content)).toBeInTheDocument();
  });

  it('should display full file path', () => {
    useChatStore.setState({
      messages: [],
      isLoading: false,
      generatedFiles: [
        { path: 'packages/infrastructure/lib/stack.ts', content: 'code' },
      ],
    });

    render(<GeneratedCodeModal visible={true} onDismiss={mockOnDismiss} />);
    
    expect(screen.getByText('packages/infrastructure/lib/stack.ts')).toBeInTheDocument();
  });

  it('should not render when visible is false', () => {
    useChatStore.setState({
      messages: [],
      isLoading: false,
      generatedFiles: [
        { path: 'lib/stack.ts', content: 'code' },
      ],
    });

    const { container } = render(<GeneratedCodeModal visible={false} onDismiss={mockOnDismiss} />);
    
    // Modal should not be visible in DOM when visible=false
    expect(container.querySelector('[role="dialog"]')).not.toBeInTheDocument();
  });
});
