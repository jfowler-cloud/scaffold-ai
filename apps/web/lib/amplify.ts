/** Amplify + AWS SDK configuration from VITE_* environment variables. */
import { Amplify } from 'aws-amplify'

export const awsConfig = {
  region: import.meta.env.VITE_AWS_REGION || 'us-east-1',
  userPoolId: import.meta.env.VITE_USER_POOL_ID || '',
  userPoolClientId: import.meta.env.VITE_USER_POOL_CLIENT_ID || '',
  identityPoolId: import.meta.env.VITE_IDENTITY_POOL_ID || '',
}

export const appConfig = {
  workflowArn: import.meta.env.VITE_WORKFLOW_ARN || '',
  getExecutionFnName: import.meta.env.VITE_GET_EXECUTION_FN || 'scaffold-ai-get_execution',
}

export function configureAmplify() {
  if (!awsConfig.userPoolId) return
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: awsConfig.userPoolId,
        userPoolClientId: awsConfig.userPoolClientId,
        identityPoolId: awsConfig.identityPoolId,
      },
    },
  })
}
