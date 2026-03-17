#!/bin/bash
# deploy-frontend.sh — build frontend and deploy to CloudFront
# Usage: ./deploy-frontend.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Getting deployment info from CloudFormation..."
HOSTING_BUCKET=$(aws cloudformation describe-stacks --stack-name ScaffoldAI-Database \
  --query "Stacks[0].Outputs[?OutputKey=='HostingBucketName'].OutputValue" --output text)
DISTRIBUTION_DOMAIN=$(aws cloudformation describe-stacks --stack-name ScaffoldAI-Database \
  --query "Stacks[0].Outputs[?OutputKey=='DistributionDomain'].OutputValue" --output text)
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?DomainName=='${DISTRIBUTION_DOMAIN}'].Id" --output text)

if [ -z "$HOSTING_BUCKET" ] || [ "$HOSTING_BUCKET" = "None" ]; then
  echo "ScaffoldAI-Database stack not found. Deploy infra first: cd apps/infra && npx cdk deploy --all"
  exit 1
fi

echo "Populating frontend env vars from CloudFormation outputs..."
extract_output() {
  local stack="$1" key="$2"
  aws cloudformation describe-stacks --stack-name "$stack" \
    --query "Stacks[0].Outputs[?OutputKey=='${key}'].OutputValue" --output text
}

export VITE_AWS_REGION="${AWS_REGION:-us-east-1}"
export VITE_USER_POOL_ID=$(extract_output "ScaffoldAI-Database" "UserPoolId")
export VITE_USER_POOL_CLIENT_ID=$(extract_output "ScaffoldAI-Database" "UserPoolClientId")
export VITE_IDENTITY_POOL_ID=$(extract_output "ScaffoldAI-Database" "IdentityPoolId")
export VITE_WORKFLOW_ARN=$(extract_output "ScaffoldAI-Workflow" "WorkflowArn")
export VITE_GET_EXECUTION_FN="scaffold-ai-get_execution"

# Backend URL: Step Functions workflow is invoked directly via SDK, no API Gateway
export VITE_BACKEND_URL=""

# Project Planner AI CloudFront URL for "Refine in Planner" button
PLANNER_DOMAIN=$(aws cloudformation describe-stacks --stack-name ProjectPlanner-Database \
  --query "Stacks[0].Outputs[?OutputKey=='DistributionDomain'].OutputValue" --output text 2>/dev/null || true)
if [ -n "$PLANNER_DOMAIN" ] && [ "$PLANNER_DOMAIN" != "None" ]; then
  export VITE_PLANNER_URL="https://${PLANNER_DOMAIN}"
  echo "  Planner URL: $VITE_PLANNER_URL"
fi

echo "  User Pool: $VITE_USER_POOL_ID"
echo "  Client ID: $VITE_USER_POOL_CLIENT_ID"
echo "  Identity Pool: $VITE_IDENTITY_POOL_ID"
echo "  Workflow ARN: $VITE_WORKFLOW_ARN"

echo "Building frontend..."
cd "$SCRIPT_DIR/apps/web"

# Remove .env.local to prevent stale values from overriding CloudFormation outputs
rm -f .env.local

# pnpm monorepo: install from root; npm: install in apps/web
if [ -f "$SCRIPT_DIR/pnpm-lock.yaml" ]; then
  cd "$SCRIPT_DIR" && pnpm install --frozen-lockfile --quiet
  cd "$SCRIPT_DIR/apps/web"
else
  npm ci --quiet
fi
npm run build

echo "Uploading to S3: $HOSTING_BUCKET"
aws s3 sync dist s3://$HOSTING_BUCKET --delete

echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*" > /dev/null

echo "Deployment complete!"
echo "https://$DISTRIBUTION_DOMAIN"
