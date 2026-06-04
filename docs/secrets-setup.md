# GitHub Secrets & Variables Setup Guide

A reference for all secrets and variables needed across the 10 projects.

---

## Types of GitHub Secrets

| Type | Scope | Use Case |
|------|-------|----------|
| **Repository secret** | All workflows in repo | AWS_ACCOUNT_ID, Slack webhook |
| **Environment secret** | Workflows targeting that environment | Environment-specific API keys |
| **Repository variable** | All workflows (not sensitive) | AWS_REGION, ECR repo name |
| **Environment variable** | That environment only | Non-sensitive env config |

---

## Adding a Secret

```
GitHub → Your Repo → Settings → Secrets and Variables → Actions → New repository secret
```

---

## Master Secrets Reference

### Secrets Needed Across All AWS Projects

| Secret Name | Where to Set | Value |
|-------------|-------------|-------|
| `AWS_ACCOUNT_ID` | Repository | Your 12-digit AWS account ID |

### Project-Specific Secrets

| Project | Secret | Description |
|---------|--------|-------------|
| 03, 06, 09, 10 | `AWS_ACCOUNT_ID` | ECR push |
| 04 | `AWS_ACCOUNT_ID` | S3 + CloudFront deploy |
| 05 | `AWS_ACCOUNT_ID`, `TF_STATE_BUCKET`, `TF_LOCK_TABLE` | Terraform remote state |
| 07 | `AWS_ACCOUNT_ID` | SAM Lambda deploy |
| 08 | `AWS_ACCOUNT_ID` | Multi-environment |
| 10 | `AWS_ACCOUNT_ID`, `SLACK_WEBHOOK_URL` | Enterprise pipeline |

---

## Access Key Method (Alternative to OIDC)

Only use this if OIDC is not available:

```
IAM → Users → Create user (no console access)
     → Attach policies directly → choose minimum required policy
     → Security credentials → Create access key → Application running outside AWS
     → Copy Access Key ID and Secret Access Key
```

Add to GitHub Secrets:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | IAM user access key ID |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret access key |
| `AWS_REGION` | e.g. `us-east-1` |

Workflow usage:

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ${{ secrets.AWS_REGION }}
```

> ⚠️ Rotate access keys every 90 days. Prefer OIDC — see `docs/oidc-setup.md`.

---

## Environment-Specific Secrets

For Project 08 (multi-environment), add secrets per environment:

```
Settings → Environments → [dev / staging / production] → Add secret
```

Each environment can have different values for the same secret name, allowing environment-scoped credentials.
