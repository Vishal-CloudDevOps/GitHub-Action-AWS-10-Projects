#!/usr/bin/env bash
# ============================================================
# rollback.sh — Enterprise Pipeline Rollback Script
# ============================================================
# Usage:
#   ./scripts/rollback.sh <environment> <previous-version>
#
# Example:
#   ./scripts/rollback.sh production v1.2.3
#
# What it does:
#   1. Validates inputs
#   2. Confirms the previous version image exists in ECR
#   3. Re-deploys the previous version
#   4. Runs health check
#   5. Sends Slack notification

set -euo pipefail

ENVIRONMENT="${1:-}"
PREVIOUS_VERSION="${2:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPOSITORY="${ECR_REPOSITORY:-project-10-app}"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"

# ── Validation ────────────────────────────────────────────────
if [[ -z "$ENVIRONMENT" || -z "$PREVIOUS_VERSION" ]]; then
  echo "❌ Usage: $0 <environment> <previous-version>"
  echo "   Example: $0 production v1.2.3"
  exit 1
fi

if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
  echo "❌ Invalid environment: $ENVIRONMENT (must be dev, staging, or production)"
  exit 1
fi

echo "🔄 Starting rollback..."
echo "   Environment:      $ENVIRONMENT"
echo "   Rolling back to:  $PREVIOUS_VERSION"
echo "   Region:           $AWS_REGION"

# ── Verify the target image exists in ECR ────────────────────
echo ""
echo "🔍 Verifying image exists in ECR..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

if aws ecr describe-images \
    --repository-name "$ECR_REPOSITORY" \
    --image-ids imageTag="$PREVIOUS_VERSION" \
    --region "$AWS_REGION" > /dev/null 2>&1; then
  echo "✅ Image found: ${ECR_URI}:${PREVIOUS_VERSION}"
else
  echo "❌ Image not found in ECR: ${ECR_URI}:${PREVIOUS_VERSION}"
  echo "   Cannot roll back to a version that doesn't exist in ECR."
  exit 1
fi

# ── Execute Rollback ──────────────────────────────────────────
echo ""
echo "🚀 Executing rollback deployment..."

# In a real pipeline, replace this with:
# - ECS: aws ecs update-service --force-new-deployment
# - Helm: helm rollback <release> <revision>
# - Lambda: aws lambda update-function-code --function-name ... --image-uri ...
echo "[Simulated] Deploying ${ECR_URI}:${PREVIOUS_VERSION} to $ENVIRONMENT"
echo "[Simulated] Waiting for deployment stability..."
sleep 2

# ── Health Check ──────────────────────────────────────────────
echo ""
echo "🔍 Running post-rollback health check..."
APP_URL="${APP_URL:-http://localhost:3000}"

for i in 1 2 3 4 5; do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${APP_URL}/health" 2>/dev/null || echo "000")
  if [[ "$HTTP_STATUS" == "200" ]]; then
    echo "✅ Health check passed (attempt $i)"
    HEALTH_OK=true
    break
  fi
  echo "⏳ Attempt $i: HTTP $HTTP_STATUS — retrying in 10s..."
  sleep 10
done

if [[ "${HEALTH_OK:-false}" != "true" ]]; then
  echo "❌ Health check failed after 5 attempts"
  # Notify Slack about failed rollback
  if [[ -n "$SLACK_WEBHOOK" ]]; then
    curl -s -X POST "$SLACK_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{\"text\":\"🚨 *CRITICAL: Rollback health check FAILED* in \`$ENVIRONMENT\` to version \`$PREVIOUS_VERSION\`\"}"
  fi
  exit 1
fi

# ── Slack Notification ────────────────────────────────────────
if [[ -n "$SLACK_WEBHOOK" ]]; then
  echo ""
  echo "📢 Sending Slack notification..."
  curl -s -X POST "$SLACK_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "{
      \"text\": \"🔄 *Rollback Complete*\",
      \"attachments\": [{
        \"color\": \"warning\",
        \"fields\": [
          {\"title\": \"Environment\", \"value\": \"$ENVIRONMENT\", \"short\": true},
          {\"title\": \"Rolled Back To\", \"value\": \"$PREVIOUS_VERSION\", \"short\": true},
          {\"title\": \"Status\", \"value\": \"✅ Healthy\", \"short\": true}
        ]
      }]
    }"
fi

echo ""
echo "✅ Rollback complete!"
echo "   Environment $ENVIRONMENT is now running version $PREVIOUS_VERSION"
