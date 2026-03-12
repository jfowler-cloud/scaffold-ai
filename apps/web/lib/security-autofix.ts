/** Client-side security auto-fix — no backend needed. */

const TYPE_HINTS: Record<string, string[]> = {
  queue: ['queue', 'sqs', 'fifo'],
  dlq: ['dlq', 'dead-letter', 'deadletter', 'dead_letter'],
  storage: ['bucket', 's3', 'storage'],
  database: ['db', 'database', 'dynamo', 'table', 'rds', 'aurora'],
  lambda: ['lambda', 'function', 'fn', 'handler', 'processor', 'detector', 'athena'],
  api: ['api', 'gateway', 'apigw', 'rest', 'http'],
  auth: ['auth', 'cognito', 'identity', 'login'],
  cdn: ['cdn', 'cloudfront', 'distribution'],
  sns: ['sns', 'topic', 'notification', 'alert'],
  events: ['eventbridge', 'event-bus', 'events', 'eventbus'],
  glue: ['glue', 'catalog', 'etl', 'crawler'],
  stream: ['kinesis', 'stream', 'firehose'],
}

const KNOWN_TYPES = new Set([
  'queue', 'storage', 'database', 'lambda', 'api', 'auth',
  'cdn', 'sns', 'events', 'glue', 'stream', 'notification', 'frontend',
])

function resolveType(node: any): string {
  const dataType = node.data?.type ?? ''
  if (KNOWN_TYPES.has(dataType)) return dataType

  const combined = `${(node.id ?? '').toLowerCase()} ${(node.data?.label ?? '').toLowerCase()}`

  if (TYPE_HINTS.lambda.some(k => combined.includes(k))) return 'lambda'
  if (TYPE_HINTS.dlq.some(k => combined.includes(k))) return 'queue'

  for (const [t, keywords] of Object.entries(TYPE_HINTS)) {
    if (t === 'lambda' || t === 'dlq') continue
    if (keywords.some(k => combined.includes(k))) return t
  }
  return dataType || 'unknown'
}

export function analyzeAndFix(graph: any): { updatedGraph: any; changes: string[] } {
  const nodes = [...(graph.nodes ?? [])].map((n: any) => ({
    ...n,
    data: { ...n.data, config: { ...n.data?.config } },
  }))
  const edges = [...(graph.edges ?? [])]
  const changes: string[] = []

  if (!nodes.length) return { updatedGraph: graph, changes }

  const hasAuth = nodes.some(n => resolveType(n) === 'auth')
  const hasApi = nodes.some(n => resolveType(n) === 'api')

  if (hasApi && !hasAuth) {
    const authNode = {
      id: `auth-${nodes.length + 1}`,
      type: 'auth',
      position: { x: 50, y: 50 },
      data: {
        type: 'auth',
        label: 'Cognito Auth',
        config: { mfa: 'OPTIONAL', password_policy: 'STRONG' },
      },
    }
    const apiNodes = nodes.filter(n => resolveType(n) === 'api')
    for (const api of apiNodes) {
      edges.push({ id: `e-${authNode.id}-${api.id}`, source: authNode.id, target: api.id, label: 'authenticates' })
    }
    nodes.push(authNode)
    changes.push('Added Cognito user pool for API authentication')
  }

  for (const node of nodes) {
    const t = resolveType(node)
    const config = node.data.config
    const label = node.data?.label ?? node.id ?? 'unknown'

    if (t === 'storage') {
      if (!config.encryption || config.encryption === 'AES256' || config.encryption === 'SSE-S3') {
        config.encryption = 'KMS'; config.kms_key_rotation = true
        changes.push(`Upgraded S3 '${label}' to KMS encryption with key rotation`)
      }
      if (!config.block_public_access) { config.block_public_access = true; changes.push(`Enabled Block Public Access on S3 '${label}'`) }
      if (!config.versioning) { config.versioning = true; changes.push(`Enabled versioning on S3 '${label}'`) }
      if (!config.https_only) { config.https_only = true; changes.push(`Enforced HTTPS-only access on S3 '${label}'`) }
    } else if (t === 'database') {
      if (!config.encryption) { config.encryption = 'KMS'; config.kms_encryption = true; changes.push(`Enabled KMS encryption for DynamoDB '${label}'`) }
      if (!config.pitr) { config.pitr = true; changes.push(`Enabled Point-in-Time Recovery for DynamoDB '${label}'`) }
    } else if (t === 'lambda') {
      if (!config.vpc_enabled) { config.vpc_enabled = true; config.vpc_subnets = 'private'; changes.push(`Added VPC configuration for Lambda '${label}'`) }
      if (!config.tracing) { config.tracing = 'Active'; changes.push(`Enabled X-Ray tracing for Lambda '${label}'`) }
    } else if (t === 'api') {
      if (!config.cors_origins || config.cors_origins === '*' || config.cors_origins === 'ALL_ORIGINS') { config.cors_origins = 'cloudfront-only'; changes.push(`Restricted CORS to CloudFront domain on API Gateway '${label}'`) }
      if (!config.waf_enabled) { config.waf_enabled = true; changes.push(`Attached WAF WebACL to API Gateway '${label}'`) }
      if (!config.throttling) { config.throttling = true; changes.push(`Enabled throttling on API Gateway '${label}'`) }
      if (!config.access_logging) { config.access_logging = true; changes.push(`Enabled access logging on API Gateway '${label}'`) }
    } else if (t === 'queue') {
      if (!config.has_dlq) { config.has_dlq = true; changes.push(`Enabled DLQ for queue '${label}'`) }
      if (!config.encryption) { config.encryption = 'KMS'; changes.push(`Enabled KMS encryption for SQS queue '${label}'`) }
    } else if (t === 'sns') {
      if (!config.encryption) { config.encryption = 'KMS'; changes.push(`Enabled KMS encryption for SNS topic '${label}'`) }
      if (!config.access_policy) { config.access_policy = 'restricted'; changes.push(`Added restricted access policy for SNS topic '${label}'`) }
    } else if (t === 'cdn') {
      if (!config.security_headers) { config.security_headers = true; config.security_headers_policy = 'CORS-and-SecurityHeadersPolicy'; changes.push(`Added security headers to CloudFront '${label}'`) }
      if (!config.waf_enabled) { config.waf_enabled = true; changes.push(`Attached WAF to CloudFront '${label}'`) }
    } else if (t === 'auth') {
      if (config.mfa !== 'REQUIRED') { config.mfa = 'REQUIRED'; config.advanced_security = 'ENFORCED'; changes.push(`Enforced MFA and advanced security on Cognito '${label}'`) }
    } else if (t === 'glue') {
      if (!config.encryption) { config.encryption = true; changes.push(`Enabled encryption for Glue Data Catalog '${label}'`) }
      if (!config.access_control) { config.access_control = 'restricted'; changes.push(`Added resource-based access policy for Glue '${label}'`) }
    } else if (t === 'events') {
      if (!config.resource_policy) { config.resource_policy = 'restricted'; changes.push(`Added resource policy for EventBridge '${label}'`) }
    }
  }

  return { updatedGraph: { nodes, edges }, changes }
}

export function getSecurityScore(graph: any): { score: number; maxScore: number; percentage: number } {
  const nodes = graph.nodes ?? []
  if (!nodes.length) return { score: 0, maxScore: 0, percentage: 0 }

  let score = 0
  let maxScore = 0

  const count = (type: string) => nodes.filter((n: any) => resolveType(n) === type)
  const ratio = (list: any[], check: (n: any) => boolean) => list.length ? list.filter(check).length / list.length : 1

  // Auth (20)
  maxScore += 20
  if (!count('api').length || count('auth').length) score += 20

  // KMS encryption (20)
  maxScore += 20
  score += Math.floor(ratio(
    [...count('storage'), ...count('database')],
    n => ['KMS', true].includes(n.data?.config?.encryption),
  ) * 20)

  // Block public access S3 (15)
  maxScore += 15
  score += Math.floor(ratio(count('storage'), n => n.data?.config?.block_public_access) * 15)

  // Lambda VPC (15)
  maxScore += 15
  score += Math.floor(ratio(count('lambda'), n => n.data?.config?.vpc_enabled) * 15)

  // DLQ on queues (10)
  maxScore += 10
  score += Math.floor(ratio(count('queue'), n => n.data?.config?.has_dlq) * 10)

  // WAF on API (10)
  maxScore += 10
  score += Math.floor(ratio(count('api'), n => n.data?.config?.waf_enabled) * 10)

  // PITR on DB (10)
  maxScore += 10
  score += Math.floor(ratio(count('database'), n => n.data?.config?.pitr) * 10)

  return { score, maxScore, percentage: maxScore > 0 ? Math.floor((score / maxScore) * 100) : 0 }
}
