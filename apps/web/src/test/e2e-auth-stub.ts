/**
 * E2E stub for aws-amplify/auth — scaffold-ai doesn't use Cognito auth
 * directly, but this stub is required by PROJECT_STANDARDS Section 8.
 */
export async function fetchAuthSession() {
  return {
    credentials: {
      accessKeyId: 'AKIAIOSFODNN7EXAMPLE',
      secretAccessKey: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
      sessionToken: 'mock-session-token',
      expiration: new Date(Date.now() + 3600_000),
    },
    tokens: undefined,
    identityId: 'us-east-1:mock-identity',
  }
}

export function getCurrentUser() {
  return Promise.resolve({ userId: 'e2e-user-1', username: 'e2e@test.com' })
}

export function signOut() {
  return Promise.resolve()
}
