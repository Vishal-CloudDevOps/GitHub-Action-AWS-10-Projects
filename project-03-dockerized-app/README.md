# Project 03 — Dockerized Application → ECR

![CI](https://img.shields.io/github/actions/workflow/status/YOUR_ORG/github-actions-aws-cicd-learning/03-dockerized-app.yml?label=CI)
![Docker](https://img.shields.io/badge/Docker-multi--stage-blue?logo=docker)
![AWS ECR](https://img.shields.io/badge/AWS-ECR-orange?logo=amazon-aws)

> **Level:** ⭐⭐⭐ Intermediate  
> **Concepts:** Multi-stage Docker builds · Trivy scanning · ECR push · OIDC auth · Image tagging

---

## 📖 What This Project Does

Builds a multi-stage Docker image, scans it for CVEs with **Trivy**, and pushes it to **Amazon ECR**. Demonstrates both OIDC (recommended) and Access Key authentication methods for AWS.

---

## 🏗️ Architecture

```
Developer Push
      │
      ▼
┌────────────────────────────────────────────────────────┐
│                  Docker CI Pipeline                     │
│                                                        │
│  Secret Scan → Unit Tests                              │
│                    │                                   │
│                    ▼                                   │
│           Docker Build (multi-stage)                   │
│           ┌─────────────────────────┐                  │
│           │ Stage 1: builder        │                  │
│           │ Stage 2: tester (tests) │                  │
│           │ Stage 3: production     │                  │
│           └─────────────────────────┘                  │
│                    │                                   │
│                    ▼                                   │
│           Trivy CVE Scan                               │
│           (fail on CRITICAL/HIGH)                      │
│                    │                                   │
│                    ▼                                   │
│           Push to Amazon ECR                           │
│           (main branch only)                           │
└────────────────────────────────────────────────────────┘
                     │
                     ▼
             ECR Repository
    (YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/
              project-03-dockerized-app)
```

---

## 🎯 Learning Objectives

- [ ] How multi-stage Docker builds reduce image size
- [ ] Why tests run in a Docker stage before producing the final image
- [ ] How Trivy scans container images for CVEs
- [ ] How SARIF format uploads scan results to GitHub Security tab
- [ ] How to authenticate to AWS with OIDC (no stored credentials)
- [ ] How `docker/metadata-action` generates semantic image tags
- [ ] Why `push: false` + `load: true` is used for scanning before pushing

---

## 📁 Folder Structure

```
project-03-dockerized-app/
├── src/
│   └── app.js
├── tests/
│   └── app.test.js
├── iam/
│   ├── oidc-trust-policy.json      # IAM OIDC trust policy
│   └── ecr-permissions-policy.json # IAM ECR permissions
├── .github/
│   └── workflows/
│       └── 03-dockerized-app.yml
├── Dockerfile                      # Multi-stage build
├── docker-compose.yml              # Local development
├── .dockerignore
├── package.json
└── README.md
```

---

## 🚀 Local Development

```bash
cd project-03-dockerized-app

# Run with Node.js
npm install && npm start
# → http://localhost:8080

# Run with Docker (single command)
docker build -t project03:local .
docker run -p 8080:8080 project03:local

# Run with Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down

# Manual Trivy scan locally
trivy image project03:local
```

---

## ☁️ AWS Setup

### Step 1: Create ECR Repository

```bash
aws ecr create-repository \
  --repository-name project-03-dockerized-app \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true
```

### Step 2: Set Up OIDC Provider (one-time per AWS account)

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### Step 3: Create IAM Role for GitHub Actions

```bash
# 1. Edit iam/oidc-trust-policy.json — replace YOUR_ACCOUNT_ID and YOUR_ORG
# 2. Create the role:
aws iam create-role \
  --role-name GitHubActionsECRRole \
  --assume-role-policy-document file://iam/oidc-trust-policy.json

# 3. Attach the ECR permissions:
aws iam put-role-policy \
  --role-name GitHubActionsECRRole \
  --policy-name ECRPushPolicy \
  --policy-document file://iam/ecr-permissions-policy.json

# 4. Get the role ARN:
aws iam get-role --role-name GitHubActionsECRRole --query 'Role.Arn' --output text
```

---

## 🔑 GitHub Secrets Required

Go to **Settings → Secrets and Variables → Actions**:

| Secret | Description |
|--------|-------------|
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |

That's all for OIDC! The role ARN is constructed dynamically in the workflow.

### Alternative: Access Key Method

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key ID |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret access key |

---

## 🔐 OIDC vs Access Keys — Why OIDC is Better

| | OIDC | Access Keys |
|--|------|-------------|
| Credential lifetime | Minutes (ephemeral) | Months/years (long-lived) |
| Rotation needed | Never | Regularly |
| If leaked | Expired immediately | Active until rotated |
| GitHub storage | No keys stored | Keys in GitHub Secrets |
| Audit trail | Per-run session names | Shared key identity |

**Bottom line:** OIDC credentials are automatically generated and expire after each workflow run. If intercepted, they're useless. Access keys are permanent until manually rotated.

---

## 🔒 Trivy Scan Results

View scan results in:
- **GitHub → Security → Code Scanning** (SARIF upload)
- **GitHub Actions → Run → Logs** (terminal output)

To view locally:
```bash
trivy image --severity CRITICAL,HIGH project03:local
```

---

## 💰 AWS Cost Estimate

| Resource | Cost |
|----------|------|
| ECR storage (1 image ~50MB) | ~$0.005/month |
| ECR data transfer (within region) | Free |
| **Total** | **~$0.01/month** |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| ECR auth fails | Verify OIDC provider exists; check role ARN in workflow |
| Trivy finds CVEs | Update base image (`node:20-alpine`) or wait for patch |
| `load: true` fails on PRs | Expected — ECR login skipped on PRs, so full tag won't exist |
| Build cache miss | First run always builds from scratch; cache populates after |

---

## 🧹 Cleanup

```bash
# Delete ECR images
aws ecr batch-delete-image \
  --repository-name project-03-dockerized-app \
  --image-ids imageTag=latest

# Delete ECR repository
aws ecr delete-repository \
  --repository-name project-03-dockerized-app \
  --force
```

---

## 📚 Next Steps

➡️ **Project 04** — Build a React app and deploy static files to S3 with CloudFront CDN.
