#!/bin/bash
# deploy.sh — deploy scaffold-ai to AWS
# Usage: ./deploy.sh [testing|optimized|premium]
#
# Frontend: S3 + CloudFront (apps/infra — CDK)
# Backend:  Step Functions + Lambda (apps/infra — CDK)

set -e

TIER=${1:-testing}

case $TIER in
  testing|optimized|premium)
    echo "🚀 Deploying scaffold-ai to $TIER..."
    ;;
  *)
    echo "Usage: ./deploy.sh [testing|optimized|premium]"
    exit 1
    ;;
esac

# Deploy CDK stacks
cd apps/infra
DEPLOYMENT_TIER=$TIER npx cdk deploy --all --require-approval never
cd ../..

# Build and deploy frontend
cd apps/web
npm run build
echo "Frontend built. Upload dist/ to S3 or use CDK S3 deployment construct."
