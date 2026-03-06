import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PlannerNotification } from '../components/PlannerNotification';
import { PlannerRefineButton } from '../components/PlannerRefineButton';

vi.mock('@cloudscape-design/components/flashbar', () => ({
  default: ({ items }: any) => (
    <div>
      {items.map((item: any, i: number) => (
        <div key={i}>
          <span>{item.header}</span>
          <span>{item.content}</span>
          {item.dismissible && <button onClick={item.onDismiss}>Dismiss</button>}
        </div>
      ))}
    </div>
  ),
}));

vi.mock('@cloudscape-design/components/button', () => ({
  default: ({ children, onClick }: any) => <button onClick={onClick}>{children}</button>,
}));

describe('PlannerNotification', () => {
  it('renders nothing when plannerData is null', () => {
    const { container } = render(<PlannerNotification plannerData={null} onDismiss={vi.fn()} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders project name and architecture', () => {
    render(
      <PlannerNotification
        plannerData={{ projectName: 'My App', architecture: 'Serverless', description: '', techStack: {}, requirements: { users: '', uptime: '', dataSize: '' } }}
        onDismiss={vi.fn()}
      />
    );
    expect(screen.getByText('Project Plan Imported')).toBeInTheDocument();
    expect(screen.getByText(/My App/)).toBeInTheDocument();
    expect(screen.getByText(/Serverless/)).toBeInTheDocument();
  });

  it('renders without architecture when not provided', () => {
    render(
      <PlannerNotification
        plannerData={{ projectName: 'My App', architecture: '', description: '', techStack: {}, requirements: { users: '', uptime: '', dataSize: '' } }}
        onDismiss={vi.fn()}
      />
    );
    expect(screen.getByText(/My App/)).toBeInTheDocument();
  });

  it('calls onDismiss when dismissed', () => {
    const onDismiss = vi.fn();
    render(
      <PlannerNotification
        plannerData={{ projectName: 'My App', architecture: '', description: '', techStack: {}, requirements: { users: '', uptime: '', dataSize: '' } }}
        onDismiss={onDismiss}
      />
    );
    fireEvent.click(screen.getByText('Dismiss'));
    expect(onDismiss).toHaveBeenCalled();
  });
});

describe('PlannerRefineButton', () => {
  beforeEach(() => {
    Object.assign(navigator, { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } });
    vi.stubGlobal('open', vi.fn());
    vi.stubGlobal('alert', vi.fn());
  });

  it('renders the button', () => {
    render(<PlannerRefineButton architecture={{ type: 'serverless' }} />);
    expect(screen.getByText('Refine in Planner')).toBeInTheDocument();
  });

  it('copies feedback and opens planner on click', async () => {
    render(<PlannerRefineButton architecture={{ type: 'serverless' }} securityScore={80} />);
    fireEvent.click(screen.getByText('Refine in Planner'));
    await vi.waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalled();
      expect(window.open).toHaveBeenCalled();
    });
  });

  it('shows alert when clipboard fails', async () => {
    Object.assign(navigator, { clipboard: { writeText: vi.fn().mockRejectedValue(new Error('denied')) } });
    render(<PlannerRefineButton architecture={{}} />);
    fireEvent.click(screen.getByText('Refine in Planner'));
    await vi.waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Failed to copy feedback to clipboard');
    });
  });

  it('includes low security score feedback', async () => {
    render(<PlannerRefineButton architecture={{}} securityScore={50} />);
    fireEvent.click(screen.getByText('Refine in Planner'));
    await vi.waitFor(() => {
      const written = (navigator.clipboard.writeText as any).mock.calls[0][0];
      expect(written).toContain('Security score is below threshold');
    });
  });
});
