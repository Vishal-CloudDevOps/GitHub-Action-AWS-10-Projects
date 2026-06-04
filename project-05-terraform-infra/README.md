# Project 05 — Terraform Infrastructure CI/CD

![Terraform](https://img.shields.io/badge/Terraform-1.7-purple?logo=terraform)
![AWS](https://img.shields.io/badge/AWS-VPC%20%2B%20EC2-orange?logo=amazon-aws)

> **Level:** ⭐⭐⭐⭐ Intermediate-Advanced  
> **Concepts:** Terraform fmt/validate/plan/apply · Remote S3 backend · DynamoDB locking · Manual approval gates · PR plan comments

---

## 📖 What This Project Does

Provisions AWS infrastructure (VPC + EC2) using Terraform, managed via a GitHub Actions pipeline with a mandatory **manual approval gate** before `apply`. The Terraform plan output is automatically posted as a PR comment for reviewers.

---

## 🏗️ Architecture

```
Pull Request
     │
     ▼
fmt → validate → security scan → plan (post to PR comment)
                                        │
                              ┌─── PR Reviewer sees plan ───┐
                              │                             │
                              ▼                             │
                       Merge to main                        │
                              │                             │
                              ▼                             │
                    ⏸️ Manual Approval Gate                  │
                    (GitHub Environment Protection)         │
                              │                             │
                              ▼                             │
                        terraform apply ◄──────────────────┘
                              │
                              ▼
                    AWS Resources Created:
                    ├── VPC (10.0.0.0/16)
                    ├── Public Subnet
                    ├── Internet Gateway
                    ├── Security Group (HTTP/HTTPS)
                    └── EC2 t3.micro (nginx)
```

---

## 🎯 Learning Objectives

- [ ] The Terraform CI/CD flow: fmt → validate → plan → apply
- [ ] Why `terraform fmt -check` is run (not auto-format) in CI
- [ ] How `terraform init -backend=false` enables validation without credentials
- [ ] How plan output gets posted to PR comments via `github-script`
- [ ] How `environment` protection rules create approval gates
- [ ] Why applying the same plan file is important (no drift between plan and apply)
- [ ] How S3 backend + DynamoDB prevents state corruption

---

## ☁️ AWS Setup — State Backend

```bash
# 1. Create S3 bucket for Terraform state
aws s3api create-bucket \
  --bucket your-terraform-state-bucket \
  --region us-east-1

# Enable versioning (important — allows rollback of state)
aws s3api put-bucket-versioning \
  --bucket your-terraform-state-bucket \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket your-terraform-state-bucket \
  --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# 2. Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

---

## 🔑 GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `AWS_ACCOUNT_ID` | 12-digit AWS account ID |
| `TF_STATE_BUCKET` | S3 bucket name for Terraform state |
| `TF_LOCK_TABLE` | DynamoDB table name for state locking |

---

## ⚙️ Setting Up Manual Approval

1. Go to **Settings → Environments → New Environment** → name it `production`
2. Check **Required reviewers** → add yourself or your team
3. Click **Save protection rules**

The `tf-apply` job will pause and send a notification to reviewers. They click **Approve** in the GitHub UI to proceed.

---

## 🏃 Running Locally

```bash
cd project-05-terraform-infra/terraform

# Configure AWS CLI
aws configure

# Initialize with local backend (for testing)
terraform init -backend=false

# Format files
terraform fmt -recursive

# Validate
terraform validate

# Plan (with local state)
terraform plan -var="environment=dev"

# Apply
terraform apply -var="environment=dev"

# Destroy
terraform destroy -var="environment=dev"
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| State lock conflict | `terraform force-unlock LOCK_ID` |
| fmt check fails | Run `terraform fmt -recursive` locally and commit |
| OIDC auth fails | Check DynamoDB + S3 permissions in IAM policy |
| Plan/apply mismatch | Don't manually edit tfplan file between jobs |

---

## 💰 AWS Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| EC2 t3.micro (24/7) | ~$8.50 |
| S3 state bucket | ~$0.01 |
| DynamoDB (on-demand) | ~$0.01 |
| **Total** | **~$8.52/month** |

> ⚠️ **Destroy after learning** to avoid charges: `terraform destroy`

---

## 🧹 Cleanup

```bash
terraform destroy -var="environment=dev" -auto-approve

# Delete state backend
aws s3 rm s3://your-terraform-state-bucket --recursive
aws s3api delete-bucket --bucket your-terraform-state-bucket
aws dynamodb delete-table --table-name terraform-state-lock
```

---

## 📚 Next Steps

➡️ **Project 06** — Deploy a Dockerized app to ECS Fargate with rolling deployments.
