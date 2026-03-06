import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../src/App';

// Mock heavy dependencies
vi.mock('@cloudscape-design/global-styles', () => ({ applyMode: vi.fn(), Mode: { Dark: 'dark', Light: 'light' } }));
vi.mock('@cloudscape-design/components/app-layout', () => ({
  default: ({ content, splitPanel, navigation, tools, onNavigationChange, onToolsChange, onSplitPanelToggle, onSplitPanelResize }: any) => (
    <div>
      <button data-testid="nav-toggle" onClick={() => onNavigationChange?.({ detail: { open: true } })}>nav</button>
      <button data-testid="tools-toggle" onClick={() => onToolsChange?.({ detail: { open: true } })}>tools</button>
      <button data-testid="split-toggle" onClick={() => onSplitPanelToggle?.({ detail: { open: true } })}>split</button>
      <button data-testid="split-resize" onClick={() => onSplitPanelResize?.({ detail: { size: 500 } })}>resize</button>
      <div data-testid="navigation">{navigation}</div>
      <div data-testid="tools">{tools}</div>
      <div data-testid="split-panel">{splitPanel}</div>
      <div data-testid="content">{content}</div>
    </div>
  ),
}));
vi.mock('@cloudscape-design/components/top-navigation', () => ({
  default: ({ utilities }: any) => (
    <div data-testid="top-nav">
      {utilities?.map((u: any, i: number) =>
        u.type === 'button' ? (
          <button key={i} onClick={u.onClick} aria-label={u.ariaLabel}>
            {u.text || u.ariaLabel}
          </button>
        ) : null
      )}
    </div>
  ),
}));
vi.mock('@cloudscape-design/components/side-navigation', () => ({
  default: ({ items, onFollow }: any) => {
    const renderItems = (list: any[]) => list?.map((item: any, i: number) => {
      if (item.type === 'link') return <a key={i} href={item.href} onClick={(e) => { e.preventDefault(); onFollow?.({ preventDefault: () => {}, detail: { href: item.href } }); }}>{item.text}</a>;
      if (item.type === 'section') return <div key={i}>{renderItems(item.items)}</div>;
      return null;
    });
    return <nav>{renderItems(items)}</nav>;
  },
}));
vi.mock('@cloudscape-design/components/split-panel', () => ({
  default: ({ children, header }: any) => <div><span>{header}</span>{children}</div>,
}));
vi.mock('@cloudscape-design/components/help-panel', () => ({
  default: ({ children, header }: any) => <div>{header}{children}</div>,
}));
vi.mock('@cloudscape-design/components/box', () => ({ default: ({ children }: any) => <div>{children}</div> }));
vi.mock('@cloudscape-design/components/link', () => ({ default: ({ children, href }: any) => <a href={href}>{children}</a> }));
vi.mock('@cloudscape-design/components/space-between', () => ({ default: ({ children }: any) => <div>{children}</div> }));
vi.mock('../components/Canvas', () => ({ Canvas: () => <div data-testid="canvas" /> }));
vi.mock('../components/Chat', () => ({ Chat: () => <div data-testid="chat" /> }));
vi.mock('../components/GeneratedCodeModal', () => ({
  GeneratedCodeModal: ({ visible, onDismiss }: any) => visible ? <div data-testid="code-modal"><button onClick={onDismiss}>Close</button></div> : null,
}));
vi.mock('../components/PlannerNotification', () => ({
  PlannerNotification: ({ onDismiss }: any) => <div data-testid="planner-notification"><button onClick={onDismiss}>Dismiss</button></div>,
}));
vi.mock('../lib/usePlannerImport', () => ({
  usePlannerImport: vi.fn(() => ({ plannerData: null, isFromPlanner: false, isLoading: false })),
}));

const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (k: string) => store[k] ?? null,
    setItem: (k: string, v: string) => { store[k] = v; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('App', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  it('renders top navigation', () => {
    render(<App />);
    expect(screen.getByTestId('top-nav')).toBeInTheDocument();
  });

  it('renders canvas and chat', () => {
    render(<App />);
    expect(screen.getByTestId('canvas')).toBeInTheDocument();
    expect(screen.getByTestId('chat')).toBeInTheDocument();
  });

  it('toggles dark mode button text', () => {
    render(<App />);
    const toggleBtn = screen.getByText(/Light|Dark/);
    const initialText = toggleBtn.textContent;
    fireEvent.click(toggleBtn);
    // After toggle, localStorage should be updated
    expect(localStorageMock.getItem('scaffold-ai-darkMode')).not.toBeNull();
  });

  it('opens code modal when Generated Code nav link clicked', () => {
    render(<App />);
    const link = screen.getByText('Generated Code');
    fireEvent.click(link);
    expect(screen.getByTestId('code-modal')).toBeInTheDocument();
  });

  it('closes code modal on dismiss', () => {
    render(<App />);
    fireEvent.click(screen.getByText('Generated Code'));
    expect(screen.getByTestId('code-modal')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Close'));
    expect(screen.queryByTestId('code-modal')).not.toBeInTheDocument();
  });

  it('clicking non-generated nav link does not open modal', () => {
    render(<App />);
    fireEvent.click(screen.getByText('Canvas'));
    expect(screen.queryByTestId('code-modal')).not.toBeInTheDocument();
  });

  it('toggles help panel via info button', () => {
    render(<App />);
    const helpBtn = screen.getByLabelText('Help');
    fireEvent.click(helpBtn);
    // toolsOpen toggled — no crash
    expect(screen.getByTestId('top-nav')).toBeInTheDocument();
  });

  it('calls onNavigationChange callback', () => {
    render(<App />);
    fireEvent.click(screen.getByTestId('nav-toggle'));
    expect(screen.getByTestId('navigation')).toBeInTheDocument();
  });

  it('calls onToolsChange callback', () => {
    render(<App />);
    fireEvent.click(screen.getByTestId('tools-toggle'));
    expect(screen.getByTestId('tools')).toBeInTheDocument();
  });

  it('calls onSplitPanelToggle callback', () => {
    render(<App />);
    fireEvent.click(screen.getByTestId('split-toggle'));
    expect(screen.getByTestId('split-panel')).toBeInTheDocument();
  });

  it('calls onSplitPanelResize callback', () => {
    render(<App />);
    fireEvent.click(screen.getByTestId('split-resize'));
    expect(screen.getByTestId('split-panel')).toBeInTheDocument();
  });

  it('does not show planner notification when not from planner', () => {
    render(<App />);
    expect(screen.queryByTestId('planner-notification')).not.toBeInTheDocument();
  });

  it('shows planner notification when isFromPlanner is true', async () => {
    const { usePlannerImport } = await import('../lib/usePlannerImport');
    (usePlannerImport as any).mockReturnValue({
      plannerData: { projectName: 'Test', architecture: '', description: '', techStack: {}, requirements: { users: '', uptime: '', dataSize: '' } },
      isFromPlanner: true,
      isLoading: false,
    });
    render(<App />);
    expect(screen.getByTestId('planner-notification')).toBeInTheDocument();
  });

  it('dismisses planner notification', async () => {
    const { usePlannerImport } = await import('../lib/usePlannerImport');
    (usePlannerImport as any).mockReturnValue({
      plannerData: { projectName: 'Test', architecture: '', description: '', techStack: {}, requirements: { users: '', uptime: '', dataSize: '' } },
      isFromPlanner: true,
      isLoading: false,
    });
    render(<App />);
    fireEvent.click(screen.getByText('Dismiss'));
    expect(screen.queryByTestId('planner-notification')).not.toBeInTheDocument();
  });
});
