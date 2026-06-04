# Project 04 — React App → S3 + CloudFront

![CI](https://img.shields.io/github/actions/workflow/status/YOUR_ORG/github-actions-aws-cicd-learning/04-react-s3-cloudfront.yml)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![AWS S3](https://img.shields.io/badge/AWS-S3-orange?logo=amazon-s3)
![CloudFront](https://img.shields.io/badge/AWS-CloudFront-orange?logo=amazon-cloudfront)

> **Level:** ⭐⭐⭐ Intermediate  
> **Concepts:** Frontend CI · React build · S3 sync · CloudFront invalidation · Cache headers · OIDC

---

## 📖 What This Project Does

Builds a React SPA, runs lint + tests, produces an optimized production build, syncs it to an **S3 bucket**, and invalidates the **CloudFront** CDN cache so users immediately see the new version.

---

## 🏗️ Architecture

```
Developer Push (main)
        │
        ▼
  ┌─────────────────────────────────┐
  │   React CI/CD Pipeline          │
  │                                 │
  │  Secret Scan                    │
  │       │                         │
  │  Lint + Test (Jest)             │
  │       │                         │
  │  Build (npm run build)          │
  │  ├─ inject REACT_APP_VERSION    │
  │  ├─ inject REACT_APP_ENV        │
  │  └─ upload build artifact       │
  │       │                         │
  │  Deploy (main only)             │
  │  ├─ aws s3 sync ./build/        │
  │  └─ CloudFront invalidation     │
  └─────────────────────────────────┘
          │
          ▼
  S3 Bucket (static hosting)
          │
          ▼
  CloudFront Distribution
  https://xxx.cloudfront.net
```

---

## 🎯 Learning Objectives

- [ ] How `REACT_APP_*` env vars are injected at build time
- [ ] Why you separate build and deploy into different jobs
- [ ] How `aws s3 sync --delete` deploys static files
- [ ] Why HTML files use `no-cache` but JS/CSS use `max-age=31536000`
- [ ] What CloudFront invalidation does and why it's needed
- [ ] How to use environment protection rules for production deployments

---

## ☁️ AWS Setup

### Step 1: Create S3 Bucket
```bash
# Create bucket (use a globally unique name)
aws s3api create-bucket \
  --bucket your-react-app-bucket-name \
  --region us-east-1

# Enable static website hosting
aws s3 website s3://your-react-app-bucket-name/ \
  --index-document index.html \
  --error-document index.html

# Block public access (CloudFront uses OAC instead)
aws s3api put-public-access-block \
  --bucket your-react-app-bucket-name \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### Step 2: Create CloudFront Distribution
Use AWS Console:
1. CloudFront → Create Distribution
2. Origin: Select your S3 bucket
3. Enable Origin Access Control (OAC)
4. Default root object: `index.html`
5. Custom error page: 404 → `/index.html` (for SPA routing)
6. Copy the Distribution ID

### Step 3: Create IAM Role (OIDC)
```bash
# Trust policy same as Project 03 — reuse the OIDC provider
aws iam create-role \
  --role-name GitHubActionsS3Role \
  --assume-role-policy-document file://oidc-trust-policy.json

aws iam put-role-policy \
  --role-name GitHubActionsS3Role \
  --policy-name S3CloudFrontPolicy \
  --policy-document file://iam/s3-cloudfront-policy.json
```

---

## 🔑 GitHub Secrets & Variables

| Name | Type | Value |
|------|------|-------|
| `AWS_ACCOUNT_ID` | Secret | Your 12-digit AWS account ID |

Update these in the workflow file directly (or as repo variables):
- `S3_BUCKET` — your S3 bucket name
- `CLOUDFRONT_DISTRIBUTION_ID` — your CloudFront distribution ID

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| S3 403 Forbidden | Check IAM role permissions and bucket policy |
| CloudFront shows old version | Check invalidation completed; verify `--delete` flag in sync |
| React app routing broken | Ensure CloudFront error page points to `/index.html` |
| OIDC auth fails | Verify OIDC provider matches exactly (including thumbprint) |

---

## 💰 AWS Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| S3 (5GB storage) | ~$0.12 |
| S3 (GET requests ~10k) | ~$0.004 |
| CloudFront (10GB transfer) | ~$0.85 |
| CloudFront invalidations (first 1000/month) | Free |
| **Total** | **~$1.00/month** |

---

## 🧹 Cleanup

```bash
# Empty and delete S3 bucket
aws s3 rm s3://your-react-app-bucket-name --recursive
aws s3api delete-bucket --bucket your-react-app-bucket-name

# Disable CloudFront distribution (must disable before delete)
aws cloudfront update-distribution --id YOUR_ID --if-match $(aws cloudfront get-distribution --id YOUR_ID --query 'ETag' --output text) \
  --distribution-config "$(aws cloudfront get-distribution-config --id YOUR_ID --query 'DistributionConfig' | jq '.Enabled=false')"
```

---

## 📚 Next Steps

➡️ **Project 05** — Terraform infrastructure as code with remote S3 backend and manual approval gates..
