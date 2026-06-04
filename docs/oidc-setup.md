# AWS OIDC Setup Guide

This guide walks through configuring GitHub Actions OIDC authentication with AWS — the secure, keyless alternative to storing long-lived access keys in GitHub Secrets.

---

## Why OIDC?

| | OIDC | Access Keys |
|---|---|---|
| Credential lifetime | Minutes (per-run) | Months/years |
| Stored in GitHub | Nothing | Key ID + Secret |
| If intercepted | Already expired | Active until rotated |
| Rotation required | Never | Every 90 days (best practice) |
| Audit trail | Per-run session name | Shared key identity |

---

## One-Time Setup (Per AWS Account)

### Step 1: Create the OIDC Identity Provider

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# Confirm it was created
aws iam list-open-id-connect-providers
```

### Step 2: Create IAM Role with Trust Policy

Save this as `trust-policy.json` — replace `YOUR_ACCOUNT_ID` and `YOUR_ORG`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/github-actions-aws-cicd-learning:*"
        }
      }
    }
  ]
}
```

```bash
aws iam create-role \
  --role-name GitHubActionsRole \
  --assume-role-policy-document file://trust-policy.json

# Attach the appropriate permissions policy (from each project's iam/ directory)
aws iam put-role-policy \
  --role-name GitHubActionsRole \
  --policy-name ProjectPermissions \
  --policy-document file://permissions-policy.json
```

### Step 3: Configure the Workflow

```yaml
permissions:
  id-token: write   # Required for OIDC
  contents: read

steps:
  - name: Configure AWS credentials
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/GitHubActionsRole
      aws-region: us-east-1
      role-session-name: GitHubActions-${{ github.run_id }}
```

---

## Trust Policy Conditions Explained

### Restrict to a specific repository
```json
"StringEquals": {
  "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:ref:refs/heads/main"
}
```

### Allow any branch in a repo
```json
"StringLike": {
  "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:*"
}
```

### Allow any repo in an org
```json
"StringLike": {
  "token.actions.githubusercontent.com:sub": "repo:my-org/*"
}
```

> ⚠️ The more restrictive the condition, the better. Prefer locking to specific repos.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Could not assume role` | Trust policy mismatch | Check `sub` condition matches your org/repo exactly |
| `Not authorized to perform sts:AssumeRoleWithWebIdentity` | OIDC provider not created | Run Step 1 above |
| `id-token permission missing` | Missing workflow permission | Add `id-token: write` to permissions block |
| Works locally, fails in CI | Different identity | Ensure role trust policy allows GitHub's OIDC provider, not a user |
