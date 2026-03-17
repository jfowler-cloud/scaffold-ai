import { Page } from '@playwright/test'

/** Stub Cognito / auth calls so they don't fail. */
export async function mockAuth(page: Page) {
  await page.route('**/cognito-idp.*.amazonaws.com/**', async route => {
    await route.fulfill({ status: 200, body: '{}' })
  })
  await page.route('**/cognito-identity.*.amazonaws.com/**', async route => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify({
        IdentityId: 'us-east-1:mock-identity',
        Credentials: {
          AccessKeyId: 'AKIAIOSFODNN7EXAMPLE',
          SecretKey: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
          SessionToken: 'mock-session-token',
          Expiration: new Date(Date.now() + 3600000).toISOString(),
        },
      }),
    })
  })
}

/** Stub all Step Functions / Lambda calls. */
export async function mockAWS(page: Page) {
  await page.route('**/states.*.amazonaws.com/**', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/x-amz-json-1.0',
      body: JSON.stringify({ executionArn: 'arn:aws:states:us-east-1:123456789012:execution:mock' }),
    })
  })
  await page.route('**/lambda.*.amazonaws.com/**', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ statusCode: 200 }),
    })
  })
}
