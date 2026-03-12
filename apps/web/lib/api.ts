/** AWS SDK calls via Cognito identity pool credentials. */
import { SFNClient, StartExecutionCommand } from '@aws-sdk/client-sfn'
import { LambdaClient, InvokeCommand } from '@aws-sdk/client-lambda'
import { fetchAuthSession } from 'aws-amplify/auth'
import { awsConfig, appConfig } from './amplify'

async function getClients() {
  const session = await fetchAuthSession()
  const config = { region: awsConfig.region, credentials: session.credentials }
  return {
    sfn: new SFNClient(config),
    lambda: new LambdaClient(config),
  }
}

export interface ChatResult {
  message?: string
  updated_graph?: { nodes?: any[]; edges?: any[] }
  generated_files?: any[]
  error?: string
}

/**
 * Start a chat workflow execution via Step Functions.
 * Returns the execution ARN.
 */
export async function startChatExecution(
  userInput: string,
  graphJson: any,
  iacFormat: string,
): Promise<string> {
  const { sfn } = await getClients()

  const payload = {
    user_input: userInput.replace('skip_security_check', '').trim(),
    graph_json: graphJson || { nodes: [], edges: [] },
    iac_format: iacFormat,
    skip_security: userInput.includes('skip_security_check'),
    generated_files: [],
    response: '',
    security_review: null,
  }

  const resp = await sfn.send(new StartExecutionCommand({
    stateMachineArn: appConfig.workflowArn,
    input: JSON.stringify(payload),
  }))

  return resp.executionArn!
}

/**
 * Poll execution status via the get_execution Lambda.
 */
export async function pollExecutionStatus(executionArn: string): Promise<{
  status: string
  message?: string
  updated_graph?: any
  generated_files?: any[]
  error?: string
}> {
  const { lambda } = await getClients()

  const resp = await lambda.send(new InvokeCommand({
    FunctionName: appConfig.getExecutionFnName,
    Payload: new TextEncoder().encode(JSON.stringify({ executionArn })),
  }))

  const raw = JSON.parse(new TextDecoder().decode(resp.Payload))
  const body = typeof raw.body === 'string' ? JSON.parse(raw.body) : raw
  return body
}

/**
 * Fire-and-poll: start execution then poll until terminal state.
 */
export async function sendChat(
  userInput: string,
  graphJson: any,
  iacFormat: string,
): Promise<ChatResult> {
  const executionArn = await startChatExecution(userInput, graphJson, iacFormat)

  const POLL_INTERVAL = 2000
  const MAX_POLLS = 90

  for (let i = 0; i < MAX_POLLS; i++) {
    const data = await pollExecutionStatus(executionArn)

    if (data.status === 'SUCCEEDED') {
      return {
        message: data.message,
        updated_graph: data.updated_graph,
        generated_files: data.generated_files,
      }
    }
    if (data.status === 'FAILED' || data.status === 'TIMED_OUT' || data.status === 'ABORTED') {
      throw new Error(data.error || `Workflow ${data.status.toLowerCase()}`)
    }

    await new Promise(resolve => setTimeout(resolve, POLL_INTERVAL))
  }
  throw new Error('Workflow timed out waiting for response')
}
