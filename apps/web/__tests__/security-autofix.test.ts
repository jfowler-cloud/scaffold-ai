import { describe, it, expect } from 'vitest';
import { analyzeAndFix, getSecurityScore } from '../lib/security-autofix';

describe('security-autofix', () => {
  it('should return empty changes for empty graph', () => {
    const { changes } = analyzeAndFix({ nodes: [], edges: [] });
    expect(changes).toEqual([]);
  });

  it('should add auth node when API exists without auth', () => {
    const graph = {
      nodes: [{ id: 'api-1', data: { type: 'api', label: 'REST API' } }],
      edges: [],
    };
    const { updatedGraph, changes } = analyzeAndFix(graph);
    expect(changes.some(c => c.includes('Cognito'))).toBe(true);
    expect(updatedGraph.nodes.length).toBe(2);
    expect(updatedGraph.edges.length).toBe(1);
  });

  it('should not add auth when already present', () => {
    const graph = {
      nodes: [
        { id: 'api-1', data: { type: 'api', label: 'REST API' } },
        { id: 'auth-1', data: { type: 'auth', label: 'Cognito' } },
      ],
      edges: [],
    };
    const { changes } = analyzeAndFix(graph);
    expect(changes.some(c => c.includes('Cognito user pool'))).toBe(false);
  });

  it('should add KMS encryption to S3', () => {
    const graph = {
      nodes: [{ id: 's3-1', data: { type: 'storage', label: 'Bucket' } }],
      edges: [],
    };
    const { changes } = analyzeAndFix(graph);
    expect(changes.some(c => c.includes('KMS encryption'))).toBe(true);
    expect(changes.some(c => c.includes('Block Public Access'))).toBe(true);
  });

  it('should add PITR to DynamoDB', () => {
    const graph = {
      nodes: [{ id: 'db-1', data: { type: 'database', label: 'Table' } }],
      edges: [],
    };
    const { changes } = analyzeAndFix(graph);
    expect(changes.some(c => c.includes('Point-in-Time Recovery'))).toBe(true);
  });

  it('should add VPC to Lambda', () => {
    const graph = {
      nodes: [{ id: 'fn-1', data: { type: 'lambda', label: 'Handler' } }],
      edges: [],
    };
    const { changes } = analyzeAndFix(graph);
    expect(changes.some(c => c.includes('VPC configuration'))).toBe(true);
  });

  it('should add DLQ to queues', () => {
    const graph = {
      nodes: [{ id: 'q-1', data: { type: 'queue', label: 'SQS Queue' } }],
      edges: [],
    };
    const { changes } = analyzeAndFix(graph);
    expect(changes.some(c => c.includes('DLQ'))).toBe(true);
  });

  it('should resolve types from node id/label when data.type is missing', () => {
    const graph = {
      nodes: [{ id: 'my-lambda-fn', data: { label: 'Processor' } }],
      edges: [],
    };
    const { changes } = analyzeAndFix(graph);
    expect(changes.some(c => c.includes('VPC configuration'))).toBe(true);
  });

  it('should return perfect score when all security measures present', () => {
    const graph = {
      nodes: [
        { id: '1', data: { type: 'auth', config: { mfa: 'REQUIRED' } } },
        { id: '2', data: { type: 'storage', config: { encryption: 'KMS', block_public_access: true } } },
        { id: '3', data: { type: 'database', config: { encryption: 'KMS', pitr: true } } },
        { id: '4', data: { type: 'lambda', config: { vpc_enabled: true } } },
        { id: '5', data: { type: 'queue', config: { has_dlq: true } } },
        { id: '6', data: { type: 'api', config: { waf_enabled: true } } },
      ],
      edges: [],
    };
    const score = getSecurityScore(graph);
    expect(score.percentage).toBe(100);
  });

  it('should return zero score for empty graph', () => {
    const score = getSecurityScore({ nodes: [], edges: [] });
    expect(score.percentage).toBe(0);
  });

  it('should detect WAF on API Gateway', () => {
    const graph = {
      nodes: [{ id: 'api-1', data: { type: 'api', label: 'API Gateway' } }],
      edges: [],
    };
    const { changes } = analyzeAndFix(graph);
    expect(changes.some(c => c.includes('WAF'))).toBe(true);
  });

  it('should detect CloudFront security headers', () => {
    const graph = {
      nodes: [{ id: 'cdn-1', data: { type: 'cdn', label: 'CloudFront' } }],
      edges: [],
    };
    const { changes } = analyzeAndFix(graph);
    expect(changes.some(c => c.includes('security headers'))).toBe(true);
  });
});
