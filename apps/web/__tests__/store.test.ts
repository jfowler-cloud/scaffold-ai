import { describe, it, expect, beforeEach } from 'vitest';
import { useGraphStore, useChatStore } from '../lib/store';
import type { AppNode } from '../lib/store';

describe('useGraphStore', () => {
  beforeEach(() => {
    useGraphStore.setState({ nodes: [], edges: [], selectedNode: null });
  });

  describe('addNode', () => {
    it('should add a node to the store', () => {
      const node: AppNode = {
        id: '1',
        type: 'default',
        position: { x: 0, y: 0 },
        data: { label: 'Test Node', type: 'lambda' },
      };

      useGraphStore.getState().addNode(node);
      expect(useGraphStore.getState().nodes).toHaveLength(1);
      expect(useGraphStore.getState().nodes[0]).toEqual(node);
    });
  });

  describe('removeNode', () => {
    it('should remove a node and its connected edges', () => {
      const node1: AppNode = {
        id: '1',
        type: 'default',
        position: { x: 0, y: 0 },
        data: { label: 'Node 1', type: 'lambda' },
      };
      const node2: AppNode = {
        id: '2',
        type: 'default',
        position: { x: 100, y: 0 },
        data: { label: 'Node 2', type: 'database' },
      };

      useGraphStore.setState({
        nodes: [node1, node2],
        edges: [{ id: 'e1-2', source: '1', target: '2' }],
      });

      useGraphStore.getState().removeNode('1');
      
      expect(useGraphStore.getState().nodes).toHaveLength(1);
      expect(useGraphStore.getState().nodes[0].id).toBe('2');
      expect(useGraphStore.getState().edges).toHaveLength(0);
    });
  });

  describe('updateNode', () => {
    it('should update node data', () => {
      const node: AppNode = {
        id: '1',
        type: 'default',
        position: { x: 0, y: 0 },
        data: { label: 'Original', type: 'lambda' },
      };

      useGraphStore.setState({ nodes: [node] });
      useGraphStore.getState().updateNode('1', { label: 'Updated' });

      expect(useGraphStore.getState().nodes[0].data.label).toBe('Updated');
      expect(useGraphStore.getState().nodes[0].data.type).toBe('lambda');
    });
  });

  describe('setGraph', () => {
    it('should replace nodes and edges', () => {
      const nodes: AppNode[] = [
        { id: '1', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Node 1', type: 'api' } },
        { id: '2', type: 'default', position: { x: 100, y: 0 }, data: { label: 'Node 2', type: 'lambda' } },
      ];
      const edges = [{ id: 'e1-2', source: '1', target: '2' }];

      useGraphStore.getState().setGraph(nodes, edges);

      expect(useGraphStore.getState().nodes).toEqual(nodes);
      expect(useGraphStore.getState().edges).toEqual(edges);
    });
  });

  describe('onConnect', () => {
    it('should add an edge when connecting nodes', () => {
      const connection = { source: '1', target: '2' };
      
      useGraphStore.getState().onConnect(connection);

      expect(useGraphStore.getState().edges).toHaveLength(1);
      expect(useGraphStore.getState().edges[0].source).toBe('1');
      expect(useGraphStore.getState().edges[0].target).toBe('2');
    });
  });

  describe('applyLayout', () => {
    const createTestNodes = (): AppNode[] => [
      { id: '1', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Frontend', type: 'frontend' } },
      { id: '2', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Auth', type: 'auth' } },
      { id: '3', type: 'default', position: { x: 0, y: 0 }, data: { label: 'API', type: 'api' } },
      { id: '4', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Lambda', type: 'lambda' } },
      { id: '5', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Database', type: 'database' } },
    ];

    it('should apply horizontal layout with type-based columns', () => {
      useGraphStore.setState({ nodes: createTestNodes(), edges: [] });
      useGraphStore.getState().applyLayout('horizontal');

      const nodes = useGraphStore.getState().nodes;
      
      // Frontend (col 0) should be leftmost
      expect(nodes.find(n => n.id === '1')?.position.x).toBe(50);
      // Auth (col 1) should be next
      expect(nodes.find(n => n.id === '2')?.position.x).toBe(400);
      // API (col 2) should be next
      expect(nodes.find(n => n.id === '3')?.position.x).toBe(750);
      // Lambda (col 3) should be next
      expect(nodes.find(n => n.id === '4')?.position.x).toBe(1100);
      // Database (col 6) should be rightmost
      expect(nodes.find(n => n.id === '5')?.position.x).toBe(2150);
    });

    it('should apply vertical layout with type-based rows', () => {
      useGraphStore.setState({ nodes: createTestNodes(), edges: [] });
      useGraphStore.getState().applyLayout('vertical');

      const nodes = useGraphStore.getState().nodes;
      
      // Frontend (row 0) should be topmost
      expect(nodes.find(n => n.id === '1')?.position.y).toBe(50);
      // Auth (row 1) should be next
      expect(nodes.find(n => n.id === '2')?.position.y).toBe(270);
      // Database (row 6) should be bottommost
      expect(nodes.find(n => n.id === '5')?.position.y).toBe(1370);
    });

    it('should apply grid layout', () => {
      useGraphStore.setState({ nodes: createTestNodes(), edges: [] });
      useGraphStore.getState().applyLayout('grid');

      const nodes = useGraphStore.getState().nodes;
      
      // 5 nodes = 3 cols (ceil(sqrt(5)))
      expect(nodes[0].position).toEqual({ x: 50, y: 50 });
      expect(nodes[1].position).toEqual({ x: 400, y: 50 });
      expect(nodes[2].position).toEqual({ x: 750, y: 50 });
      expect(nodes[3].position).toEqual({ x: 50, y: 270 });
      expect(nodes[4].position).toEqual({ x: 400, y: 270 });
    });

    it('should apply circular layout', () => {
      useGraphStore.setState({ nodes: createTestNodes(), edges: [] });
      useGraphStore.getState().applyLayout('circular');

      const nodes = useGraphStore.getState().nodes;
      
      // All nodes should be roughly equidistant from center (400, 300)
      nodes.forEach(node => {
        const dx = node.position.x - 400;
        const dy = node.position.y - 300;
        const distance = Math.sqrt(dx * dx + dy * dy);
        expect(distance).toBeCloseTo(200, 0); // radius = max(200, 5 * 40) = 200
      });
    });

    it('should handle empty nodes array', () => {
      useGraphStore.setState({ nodes: [], edges: [] });
      useGraphStore.getState().applyLayout('horizontal');
      
      expect(useGraphStore.getState().nodes).toHaveLength(0);
    });

    it('should stack nodes of same type in rows (horizontal)', () => {
      const nodes: AppNode[] = [
        { id: '1', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Lambda 1', type: 'lambda' } },
        { id: '2', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Lambda 2', type: 'lambda' } },
        { id: '3', type: 'default', position: { x: 0, y: 0 }, data: { label: 'Lambda 3', type: 'lambda' } },
      ];
      
      useGraphStore.setState({ nodes, edges: [] });
      useGraphStore.getState().applyLayout('horizontal');

      const updatedNodes = useGraphStore.getState().nodes;
      
      // All lambdas should be in same column (x), different rows (y)
      expect(updatedNodes[0].position.x).toBe(updatedNodes[1].position.x);
      expect(updatedNodes[1].position.x).toBe(updatedNodes[2].position.x);
      expect(updatedNodes[0].position.y).toBe(50);
      expect(updatedNodes[1].position.y).toBe(270);
      expect(updatedNodes[2].position.y).toBe(490);
    });
  });
});

describe('useChatStore', () => {
  beforeEach(() => {
    useChatStore.setState({ messages: [], isLoading: false, generatedFiles: [] });
  });

  describe('addMessage', () => {
    it('should add a message to the store', () => {
      const message = { id: '1', role: 'user' as const, content: 'Hello' };
      
      useChatStore.getState().addMessage(message);
      
      expect(useChatStore.getState().messages).toHaveLength(1);
      expect(useChatStore.getState().messages[0]).toEqual(message);
    });

    it('should append messages in order', () => {
      useChatStore.getState().addMessage({ id: '1', role: 'user', content: 'First' });
      useChatStore.getState().addMessage({ id: '2', role: 'assistant', content: 'Second' });
      
      const messages = useChatStore.getState().messages;
      expect(messages).toHaveLength(2);
      expect(messages[0].content).toBe('First');
      expect(messages[1].content).toBe('Second');
    });
  });

  describe('setLoading', () => {
    it('should set loading state', () => {
      useChatStore.getState().setLoading(true);
      expect(useChatStore.getState().isLoading).toBe(true);

      useChatStore.getState().setLoading(false);
      expect(useChatStore.getState().isLoading).toBe(false);
    });
  });

  describe('setGeneratedFiles', () => {
    it('should set generated files', () => {
      const files = [
        { path: 'lib/stack.ts', content: 'export class Stack {}' },
        { path: 'bin/app.ts', content: 'new Stack()' },
      ];
      
      useChatStore.getState().setGeneratedFiles(files);
      
      expect(useChatStore.getState().generatedFiles).toEqual(files);
    });
  });

  describe('clearMessages', () => {
    it('should clear all messages', () => {
      useChatStore.getState().addMessage({ id: '1', role: 'user', content: 'Test' });
      useChatStore.getState().addMessage({ id: '2', role: 'assistant', content: 'Response' });
      
      useChatStore.getState().clearMessages();
      
      expect(useChatStore.getState().messages).toHaveLength(0);
    });
  });
});
