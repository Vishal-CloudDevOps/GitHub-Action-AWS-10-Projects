# Project 08 — Multi-Environment Pipeline

![CI](https://img.shields.io/github/actions/workflow/status/YOUR_ORG/github-actions-aws-cicd-learning/08-multi-environment.yml)
![Environments](https://img.shields.io/badge/Environments-dev%20%7C%20staging%20%7C%20prod-blue)

> **Level:** ⭐⭐⭐⭐⭐ Advanced
> **Concepts:** Reusable workflows · Environment protection rules · Branch-based routing · Approval gates · Promotion flow

---

## 📖 What This Project Does

A Node.js app deployed through a **three-stage promotion pipeline**: dev → staging → production. Each environment uses its own configuration, secrets, and protection rules. Production always requires manual approval. Deploy logic is extracted into a **reusable workflow** to eliminate duplication.

---

## 🏗️ Architecture

```
Branch Strategy:
  feature/* ──▶ develop ──▶ release/* ──▶ main
                   │              │           │
                   ▼              ▼           ▼
                  Dev          Staging    Production
              (auto-deploy)  (auto-deploy) (approval
                                           required)

Pipeline Flow:

  Push to develop:
  CI → Deploy Dev → Deploy Staging

  Push to release/*:
  CI → Deploy Staging (skip dev)

  Push to main:
  CI → (staging must pass) → ⏸️ Approval → Deploy Production

  Manual dispatch:
  CI → Deploy to [dev | staging | production] directly

Environment Protection Rules:
  dev:        No approval needed
  staging:    No approval needed
  production: Required reviewer(s) — pipeline pauses until approved
```

---

## 🎯 Learning Objectives

- [ ] How `workflow_call` creates reusable workflows
- [ ] How to pass `inputs` and `secrets` to a reusable workflow
- [ ] How `outputs` from a reusable workflow flow back to the caller
- [ ] How GitHub **environment protection rules** create approval gates
- [ ] How `always()` combined with result checks enables conditional promotion
- [ ] How `concurrency` prevents overlapping deploys per environment
- [ ] How environment-specific secrets are isolated in GitHub Settings
- [ ] How branch names route code to the correct environment

---

## 📁 Folder Structure

```
project-08-multi-environment/
├── src/
│   └── app.js                       # Express app
├── config/
│   ├── dev/app-config.json          # Dev settings
│   ├── staging/app-config.json      # Staging settings
│   └── prod/app-config.json         # Production settings
├── .github/
│   └── workflows/
│       ├── 08-multi-environment.yml # Main pipeline (caller)
│       └── 08-deploy-env.yml        # Reusable deploy workflow
├── package.json
└── README.md
```

---

## ⚙️ Setting Up Environments in GitHub

### Step 1: Create Environments

Go to **Settings → Environments → New environment** and create:

1. **`dev`** — No protection rules
2. **`staging`** — No protection rules (or add a reviewer)
3. **`production`** — Add required reviewers

### Step 2: Add Environment-Specific Secrets

For each environment, add secrets under **Settings → Environments → [env name] → Secrets**:

| Environment | Secret | Value |
|-------------|--------|-------|
| All | `AWS_ACCOUNT_ID` | Your AWS account ID |

### Step 3: Add Environment Variables (optional)

Under **Settings → Environments → [env name] → Variables**:

| Environment | Variable | Value |
|-------------|----------|-------|
| dev | `API_URL` | https://dev.your-app.example.com |
| staging | `API_URL` | https://staging.your-app.example.com |
| production | `API_URL` | https://your-app.example.com |

---

## 🌿 Branch → Environment Mapping

| Branch | Deploy Target | Approval |
|--------|--------------|----------|
| `develop` | dev → staging | None |
| `release/*` | staging | None |
| `main` | production | ✅ Required |
| Manual dispatch | Any | None (unless env has rules) |

---

## 🔁 Reusable Workflow Pattern

The deploy logic lives in `08-deploy-env.yml` and is called like a function:

```yaml
deploy-staging:
  uses: ./.github/workflows/08-deploy-env.yml
  with:
    environment: staging
    aws_region: us-east-1
    app_version: ${{ github.sha }}
  secrets:
    AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
```

**Benefits:**
- Single source of truth for deploy logic
- Changes to deploy process only need updating in one place
- Each environment call gets its own isolated job with correct secrets

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| Production job skipped | Check `needs.deploy-staging.result == 'success'` condition |
| Reusable workflow not found | Ensure path `./.github/workflows/08-deploy-env.yml` is correct |
| Environment secrets not available | Verify secret is added under the environment, not just the repo |
| Approval notification not sent | Check you've added reviewers under the environment settings |
| Concurrent deploy blocked | Normal — `concurrency` prevents overlapping; previous run must complete |

---

## 💰 AWS Cost

This project's cost depends on which deployment target you use (S3/ECS/Lambda — see Projects 04–07). The pipeline structure itself is free.

---

## 📚 Next Steps

➡️ **Project 09** — Kubernetes deployment to EKS with Helm charts and kubectl.
