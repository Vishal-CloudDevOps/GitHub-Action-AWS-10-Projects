# Project 07 — Lambda Serverless API (AWS SAM)

![CI](https://img.shields.io/github/actions/workflow/status/YOUR_ORG/github-actions-aws-cicd-learning/07-lambda-serverless.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange?logo=aws-lambda)
![SAM](https://img.shields.io/badge/AWS-SAM-orange?logo=amazon-aws)

> **Level:** ⭐⭐⭐⭐ Intermediate-Advanced
> **Concepts:** SAM validate/build/deploy · Lambda packaging · API Gateway stages · Smoke tests · Job outputs

---

## 📖 What This Project Does

A Python Lambda function exposed via API Gateway, deployed with **AWS SAM**. The pipeline validates the SAM template, builds a Lambda deployment package, and deploys to **dev** (on `develop` branch) or **production** (on `main` branch) with a live smoke test after each deploy.

---

## 🏗️ Architecture

```
Push to develop / main
        │
        ▼
┌─────────────────────────────────────────────┐
│          Lambda CI/CD Pipeline               │
│                                             │
│  Secret Scan                                │
│       │                                     │
│  ┌────┴──────┐  ┌──────────────┐           │
│  │   Test    │  │ SAM Validate │           │
│  │ pytest+   │  │ (template    │           │
│  │ bandit    │  │  syntax)     │           │
│  └────┬──────┘  └──────┬───────┘           │
│       └────────┬────────┘                   │
│                ▼                            │
│          SAM Build                          │
│          (zip code + deps)                  │
│                │                            │
│      ┌─────────┴──────────┐                 │
│      ▼                    ▼                 │
│  Deploy Dev           Deploy Prod           │
│  (develop branch)     (main branch)         │
│      │                    │                 │
│  Smoke Test           Smoke Test            │
│  /health              /health (3 retries)   │
└─────────────────────────────────────────────┘
        │
        ▼
API Gateway → Lambda Function
https://{id}.execute-api.us-east-1.amazonaws.com/{stage}
  GET  /
  GET  /health
  GET  /api/greet?name=Alice
  POST /api/calculate
```

---

## 🎯 Learning Objectives

- [ ] What AWS SAM is and how it extends CloudFormation
- [ ] How `sam validate` catches template errors before deploy
- [ ] What `sam build --use-container` does (Amazon Linux compatible build)
- [ ] How `sam deploy` creates/updates a CloudFormation stack
- [ ] How `--no-confirm-changeset` enables non-interactive CI deploys
- [ ] How to read stack outputs from CloudFormation in a workflow
- [ ] Why smoke tests after deploy catch runtime issues CI can't catch
- [ ] How job `outputs:` pass the API URL between jobs

---

## 📁 Folder Structure

```
project-07-lambda-serverless/
├── src/
│   └── handler.py                  # Lambda handler (all routes)
├── tests/
│   └── test_handler.py             # pytest (positive + negative)
├── sam-template/
│   └── template.yaml               # SAM / CloudFormation template
├── iam/
│   └── lambda-deploy-policy.json   # IAM permissions for GitHub Actions
├── .github/
│   └── workflows/
│       └── 07-lambda-serverless.yml
├── requirements.txt                # Production Lambda deps
├── requirements-dev.txt            # Dev + test deps
├── pyproject.toml                  # pytest + coverage config
└── README.md
```

---

## 🚀 Local Development

```bash
cd project-07-lambda-serverless

# Set up virtual environment
python -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
PYTHONPATH=. pytest tests/ -v

# Test handler locally (invoke directly)
python -c "
from src.handler import lambda_handler
import json
event = {'httpMethod': 'GET', 'path': '/health', 'queryStringParameters': None, 'body': None, 'headers': {}}
from unittest.mock import MagicMock
ctx = MagicMock(); ctx.aws_request_id = 'local'
result = lambda_handler(event, ctx)
print(json.loads(result['body']))
"

# Lint
flake8 src/ tests/ --max-line-length=120
black --check src/ tests/
```

### Test with SAM Local (requires Docker)

```bash
# Install SAM CLI
pip install aws-sam-cli

# Start local API (mimics API Gateway)
sam local start-api --template sam-template/template.yaml

# In another terminal:
curl http://localhost:3000/health
curl "http://localhost:3000/api/greet?name=Alice"
curl -X POST http://localhost:3000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 4, "operation": "divide"}'
```

---

## ☁️ AWS Setup

### Step 1: Create SAM Artifacts S3 Bucket

```bash
# SAM uploads your Lambda code to S3 before deploying
aws s3api create-bucket \
  --bucket your-sam-artifacts-bucket \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket your-sam-artifacts-bucket \
  --versioning-configuration Status=Enabled
```

### Step 2: Create IAM Role for GitHub Actions

```bash
# Reuse the OIDC provider from Project 03
aws iam create-role \
  --role-name GitHubActionsLambdaRole \
  --assume-role-policy-document file://iam/oidc-trust-policy.json

aws iam put-role-policy \
  --role-name GitHubActionsLambdaRole \
  --policy-name LambdaDeployPolicy \
  --policy-document file://iam/lambda-deploy-policy.json
```

### Step 3: First Manual Deploy (bootstraps the stack)

```bash
# Configure AWS CLI
aws configure

sam build --template sam-template/template.yaml --use-container

sam deploy --guided
# Follow the prompts — this creates samconfig.toml for future deploys
```

---

## 🔑 GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |

Update `SAM_S3_BUCKET` in the workflow file with your bucket name.

---

## ⚙️ CI/CD Workflow Explained

### SAM Build with Container

```yaml
sam build \
  --template template.yaml \
  --use-container \   # Build inside Amazon Linux Docker container
  --parallel          # Build functions in parallel
```

`--use-container` ensures native C extensions (like `cryptography`) compile for Lambda's Amazon Linux 2023 environment, not your CI runner's Ubuntu.

### Smoke Test with Retry

```bash
for i in 1 2 3; do
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")
  if [ "$HTTP_STATUS" = "200" ]; then exit 0; fi
  sleep 10
done
```

Lambda has cold start latency — the retry loop handles the first invocation taking longer than expected.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `sam validate` fails | Check YAML indentation in `template.yaml` |
| `sam build` fails | Ensure Docker is running (needed for `--use-container`) |
| CloudFormation ROLLBACK | Check CloudWatch logs for Lambda errors during deployment |
| Smoke test 503 | Lambda cold start — increase retry sleep to 15s |
| `CAPABILITY_IAM` error | Add `--capabilities CAPABILITY_IAM` to `sam deploy` |
| Stack already exists | Use `--no-fail-on-empty-changeset` flag |

---

## 💰 AWS Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| Lambda (1M requests/month) | Free (within free tier) |
| API Gateway (1M requests) | ~$3.50 |
| CloudWatch Logs (1GB) | ~$0.50 |
| S3 artifacts bucket | ~$0.01 |
| **Total** | **~$4.01/month** |

> Lambda has a **permanent free tier** of 1M requests/month — this project is essentially free for learning.

---

## 🧹 Cleanup

```bash
# Delete SAM stacks (removes Lambda + API Gateway)
sam delete --stack-name project-07-lambda-dev --no-prompts
sam delete --stack-name project-07-lambda-production --no-prompts

# Delete artifacts bucket
aws s3 rm s3://your-sam-artifacts-bucket --recursive
aws s3api delete-bucket --bucket your-sam-artifacts-bucket
```

---

## 📚 Next Steps

➡️ **Project 08** — Multi-environment pipeline with dev/staging/prod, manual approval gates, and reusable workflows.
