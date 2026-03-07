import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Canvas } from '../components/Canvas';
import { useGraphStore } from '../lib/store';

// Mock ReactFlow and its sub-components
vi.mock('@xyflow/react', () => ({
  ReactFlow: ({ children, onNodeClick, onPaneClick, nodes, edges }: any) => (
    <div data-testid="react-flow" onClick={onPaneClick}>
      {nodes?.map((n: any) => (
        <div key={n.id} data-testid={`node-${n.id}`} onClick={(e) => { e.stopPropagation(); onNodeClick(e, n); }}>
          {n.data.label}
        </div>
      ))}
      {children}
    </div>
  ),
  Background: () => <div data-testid="background" />,
  Controls: () => <div data-testid="controls" />,
  MiniMap: () => <div data-testid="minimap" />,
  Panel: ({ children, position }: any) => <div data-testid={`panel-${position}`}>{children}</div>,
  BackgroundVariant: { Dots: 'dots' },
  MarkerType: { ArrowClosed: 'arrowclosed' },
}));

vi.mock('@cloudscape-design/components/button', () => ({
  default: ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>,
}));

vi.mock('@cloudscape-design/components/button-dropdown', () => ({
  default: ({ children, items, onItemClick }: any) => (
    <div>
      <span>{children}</span>
      {items?.map((item: any) => (
        <button key={item.id} data-testid={`dropdown-${item.id}`} onClick={() => onItemClick({ detail: { id: item.id } })}>
          {item.text}
        </button>
      ))}
    </div>
  ),
}));

vi.mock('@cloudscape-design/components/space-between', () => ({
  default: ({ children }: any) => <div>{children}</div>,
}));

describe('Canvas', () => {
  beforeEach(() => {
    useGraphStore.setState({ nodes: [], edges: [], selectedNode: null });
  });

  it('renders ReactFlow with controls', () => {
    render(<Canvas />);
    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
    expect(screen.getByTestId('background')).toBeInTheDocument();
    expect(screen.getByTestId('controls')).toBeInTheDocument();
    expect(screen.getByTestId('minimap')).toBeInTheDocument();
  });

  it('renders layout dropdown', () => {
    render(<Canvas />);
    expect(screen.getByText('Layout')).toBeInTheDocument();
    expect(screen.getByText('Horizontal Flow')).toBeInTheDocument();
    expect(screen.getByText('Vertical Flow')).toBeInTheDocument();
  });

  it('renders Add Service and More Services dropdowns', () => {
    render(<Canvas />);
    expect(screen.getByText('Add Service')).toBeInTheDocument();
    expect(screen.getByText('More Services')).toBeInTheDocument();
  });

  it('adds a node when Add Service item clicked', () => {
    render(<Canvas />);
    fireEvent.click(screen.getByTestId('dropdown-lambda'));
    expect(useGraphStore.getState().nodes.length).toBe(1);
    expect(useGraphStore.getState().nodes[0].type).toBe('lambda');
  });

  it('adds a node from More Services dropdown', () => {
    render(<Canvas />);
    fireEvent.click(screen.getByTestId('dropdown-queue'));
    expect(useGraphStore.getState().nodes.length).toBe(1);
    expect(useGraphStore.getState().nodes[0].type).toBe('queue');
  });

  it('sets selected node on node click', () => {
    useGraphStore.setState({
      nodes: [{ id: 'n1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'My Lambda', type: 'lambda' } }],
      edges: [],
      selectedNode: null,
    });
    render(<Canvas />);
    fireEvent.click(screen.getByTestId('node-n1'));
    // The mock fires onNodeClick which calls setSelectedNode
    // Since our mock passes the node object, verify it was set
    expect(useGraphStore.getState().selectedNode).not.toBeNull();
  });

  it('clears selected node on pane click', () => {
    useGraphStore.setState({
      nodes: [{ id: 'n1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'My Lambda', type: 'lambda' } }],
      edges: [],
      selectedNode: { id: 'n1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'My Lambda', type: 'lambda' } },
    });
    render(<Canvas />);
    fireEvent.click(screen.getByTestId('react-flow'));
    expect(useGraphStore.getState().selectedNode).toBeNull();
  });

  it('applies layout when layout item clicked', () => {
    const spy = vi.spyOn(useGraphStore.getState(), 'applyLayout');
    render(<Canvas />);
    fireEvent.click(screen.getByTestId('dropdown-horizontal'));
    expect(spy).toHaveBeenCalledWith('horizontal');
  });

  it('renders nodes from store', () => {
    useGraphStore.setState({
      nodes: [
        { id: 'n1', type: 'database', position: { x: 0, y: 0 }, data: { label: 'My DB', type: 'database' } },
        { id: 'n2', type: 'api', position: { x: 100, y: 0 }, data: { label: 'My API', type: 'api' } },
      ],
      edges: [],
    });
    render(<Canvas />);
    expect(screen.getByText('My DB')).toBeInTheDocument();
    expect(screen.getByText('My API')).toBeInTheDocument();
  });

  it('styles edges with smoothstep and markers', () => {
    useGraphStore.setState({
      nodes: [
        { id: 'n1', type: 'lambda', position: { x: 0, y: 0 }, data: { label: 'A', type: 'lambda' } },
        { id: 'n2', type: 'lambda', position: { x: 100, y: 0 }, data: { label: 'B', type: 'lambda' } },
      ],
      edges: [{ id: 'e1', source: 'n1', target: 'n2' }],
    });
    // Just verify it renders without error — edge styling is applied in useMemo
    render(<Canvas />);
    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
  });
});
