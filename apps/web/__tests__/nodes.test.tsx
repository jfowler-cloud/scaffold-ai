import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { APINode } from '../components/nodes/APINode';
import { AuthNode } from '../components/nodes/AuthNode';
import { CdnNode } from '../components/nodes/CdnNode';
import { DatabaseNode } from '../components/nodes/DatabaseNode';
import { EventsNode } from '../components/nodes/EventsNode';
import { FrontendNode } from '../components/nodes/FrontendNode';
import { LambdaNode } from '../components/nodes/LambdaNode';
import { NotificationNode } from '../components/nodes/NotificationNode';
import { QueueNode } from '../components/nodes/QueueNode';
import { StorageNode } from '../components/nodes/StorageNode';
import { StreamNode } from '../components/nodes/StreamNode';
import { WorkflowNode } from '../components/nodes/WorkflowNode';
import { SecurityBadge } from '../components/nodes/SecurityBadge';

// Minimal props factory for node components
const makeProps = (label: string, type: string, selected = false) => ({
  id: 'test-id',
  type,
  selected,
  dragging: false,
  zIndex: 0,
  isConnectable: true,
  positionAbsoluteX: 0,
  positionAbsoluteY: 0,
  data: { label, type, config: undefined },
});

vi.mock('@xyflow/react', () => ({
  Handle: ({ type, position }: any) => <div data-testid={`handle-${type}`} data-position={position} />,
  Position: { Left: 'left', Right: 'right', Top: 'top', Bottom: 'bottom' },
  memo: (fn: any) => fn,
}));

describe('Node components', () => {
  const nodes = [
    { Component: APINode, label: 'My API', type: 'api', subtitle: 'API Endpoint' },
    { Component: AuthNode, label: 'My Auth', type: 'auth', subtitle: 'Cognito' },
    { Component: CdnNode, label: 'My CDN', type: 'cdn', subtitle: 'CloudFront' },
    { Component: DatabaseNode, label: 'My DB', type: 'database', subtitle: 'DynamoDB' },
    { Component: EventsNode, label: 'My Events', type: 'events', subtitle: 'EventBridge' },
    { Component: FrontendNode, label: 'My Frontend', type: 'frontend', subtitle: 'Next.js' },
    { Component: LambdaNode, label: 'My Lambda', type: 'lambda', subtitle: 'Lambda' },
    { Component: NotificationNode, label: 'My SNS', type: 'notification', subtitle: 'SNS' },
    { Component: QueueNode, label: 'My Queue', type: 'queue', subtitle: 'SQS' },
    { Component: StorageNode, label: 'My Storage', type: 'storage', subtitle: 'S3' },
    { Component: StreamNode, label: 'My Stream', type: 'stream', subtitle: 'Kinesis' },
    { Component: WorkflowNode, label: 'My Workflow', type: 'workflow', subtitle: 'Step Functions' },
  ];

  nodes.forEach(({ Component, label, type }) => {
    it(`${type}: renders label`, () => {
      render(<Component {...makeProps(label, type)} />);
      expect(screen.getByText(label)).toBeInTheDocument();
    });

    it(`${type}: renders selected state`, () => {
      const { container } = render(<Component {...makeProps(label, type, true)} />);
      expect(container.firstChild).toBeInTheDocument();
    });
  });
});

describe('SecurityBadge', () => {
  it('renders nothing when no config', () => {
    const { container } = render(<SecurityBadge />);
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when config has no security flags', () => {
    const { container } = render(<SecurityBadge config={{}} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders badge when encryption is set', () => {
    const { container } = render(<SecurityBadge config={{ encryption: true }} />);
    expect(container.firstChild).not.toBeNull();
  });

  it('renders badge for all security flags', () => {
    const config = {
      encryption: true,
      vpc_enabled: true,
      waf_enabled: true,
      block_public_access: true,
      pitr: true,
      has_dlq: true,
      tracing: true,
      mfa: 'REQUIRED',
      security_headers: true,
    };
    const { container } = render(<SecurityBadge config={config} />);
    expect(container.firstChild).not.toBeNull();
  });
});
