# Architecture Diagrams

ASCII diagrams for each project's CI/CD architecture.

---

## Repository-Level Workflow

```
Developer Workflow
─────────────────

feature/xxx ──▶ develop ──▶ release/1.x ──▶ main
                  │                            │
               Project                      Project
               01, 02                       08, 10
               (CI only)                  (full deploy)

                     ▼
              Pull Request
              ┌───────────────────────┐
              │  CI Pipeline          │
              │  - Lint               │
              │  - Test               │
              │  - Build (no push)    │
              │  - Plan (no apply)    │
              └───────────┬───────────┘
                          │ PR approved + merged
                          ▼
              ┌───────────────────────┐
              │  CD Pipeline          │
              │  - Build + push       │
              │  - Deploy to env      │
              │  - Smoke test         │
              └───────────────────────┘
```

---

## Project 01-02: Basic CI

```
Push/PR
  │
  ▼
┌─────────────────────────────────┐
│  ┌──────────┐  ┌──────────────┐ │
│  │ Secret   │  │  Dep Audit   │ │
│  │ Scan     │  │  (npm/pip)   │ │
│  └────┬─────┘  └──────────────┘ │
│       │                         │
│  ┌────▼──────────────────────┐  │
│  │  Lint (ESLint / flake8)   │  │
│  └────┬──────────────────────┘  │
│       │                         │
│  ┌────▼──────────────────────┐  │
│  │  Test Matrix               │  │
│  │  Node 18/20 or Py 3.11/12 │  │
│  └────┬──────────────────────┘  │
│       │                         │
│  ┌────▼──────────────────────┐  │
│  │  Summary + Artifacts      │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

---

## Project 03: Docker + ECR

```
Push
  │
  ├──▶ Secret Scan ──▶ Unit Tests
  │                        │
  │                        ▼
  │                 Docker Build (multi-stage)
  │                 ├─ builder  (npm ci)
  │                 ├─ tester   (npm test)
  │                 └─ production (non-root, no devDeps)
  │                        │
  │                        ▼
  │                 Trivy CVE Scan ──▶ SARIF → GitHub Security
  │                        │
  │                   PASS │ FAIL → ❌ Block push
  │                        ▼
  │                 Push to ECR
  │                 :sha-abc123
  │                 :latest
  └──────────────────────────────▶ Done
```

---

## Project 04: React → S3 + CloudFront

```
Push to main
     │
  Lint + Test (React)
     │
  Build (npm run build)
  ├─ inject REACT_APP_VERSION
  ├─ inject REACT_APP_ENV
  └─ create build/ directory
     │
  S3 Sync
  ├─ HTML files: Cache-Control: no-cache
  └─ JS/CSS files: Cache-Control: max-age=31536000
     │
  CloudFront Invalidation /*
     │
  ┌──────────────────┐
  │  CloudFront CDN   │ ◀── 200+ edge locations worldwide
  │  ├─ Cache hit     │
  └──────────────────┘
           │
        S3 Origin
        (static files)
```

---

## Project 05: Terraform

```
PR                        Push to main
│                              │
▼                              ▼
fmt → validate → plan     ⏸ Manual Approval
       │                       │
       │                       ▼
       └──▶ PR Comment    terraform apply
            (plan output)      │
                               ▼
                        AWS Resources:
                        ├─ VPC
                        ├─ Subnet
                        ├─ Security Group
                        └─ EC2 (nginx)

State: S3 bucket (versioned, encrypted)
Lock:  DynamoDB table (prevents concurrent apply)
```

---

## Project 06: ECS Fargate

```
Test → Build → Trivy → Push ECR
                              │
                              ▼
                    Render Task Definition
                    (new image URI injected)
                              │
                              ▼
                    ECS Rolling Deploy
                    ┌──────────────────────────┐
                    │  ECS Service              │
                    │  ┌───────────────────┐    │
                    │  │ Task v1 (old) ─── │───▶│ drained
                    │  └───────────────────┘    │
                    │  ┌───────────────────┐    │
                    │  │ Task v2 (new)     │    │ healthy
                    │  └───────────────────┘    │
                    └──────────────────────────┘
                              │
                    wait-for-service-stability
                              │
                    ALB → healthy tasks only
```

---

## Project 07: Lambda Serverless

```
Test → SAM Validate → SAM Build
             │              │
             └──────────────┘
                     │
                     ▼
              sam deploy
              │
              ├─▶ CloudFormation changeset
              ├─▶ Upload code to S3
              ├─▶ Create/Update Lambda function
              └─▶ Create/Update API Gateway
                         │
              ┌──────────▼──────────┐
              │    API Gateway       │
              │  GET  /              │
              │  GET  /health        │
              │  GET  /api/greet     │
              │  POST /api/calculate │
              └──────────┬──────────┘
                         │
                         ▼
                  Lambda Function
                  (Python 3.12)
```

---

## Project 08: Multi-Environment

```
Branch → Environment Routing:

  develop ──▶ dev ──▶ staging
  release/* ──────────▶ staging
  main ──────────────────────▶ ⏸ Approval ──▶ production

Reusable Workflow Pattern:

  main-pipeline.yml
  │
  ├─▶ calls: deploy-env.yml (with: environment=dev)
  ├─▶ calls: deploy-env.yml (with: environment=staging)
  └─▶ calls: deploy-env.yml (with: environment=production)
               │
               └─▶ load config/[env]/app-config.json
               └─▶ configure AWS
               └─▶ deploy
               └─▶ smoke test
```

---

## Project 09: Kubernetes EKS

```
Test → Helm Lint → Build → Trivy → Push ECR
                                        │
                                        ▼
                              aws eks update-kubeconfig
                                        │
                                        ▼
                              helm upgrade --install
                              --atomic (auto-rollback)
                                        │
                                        ▼
                    ┌─────────────────────────────────┐
                    │  EKS Cluster                     │
                    │  Namespace: project-09            │
                    │                                  │
                    │  Deployment (replicas: 2)        │
                    │  ├─ Pod 1 (node-1)               │
                    │  └─ Pod 2 (node-2)               │
                    │                                  │
                    │  HPA: 2-10 pods (CPU 70%)        │
                    │  Service: ClusterIP              │
                    └─────────────────────────────────┘
                                        │
                              kubectl rollout status
```

---

## Project 10: Enterprise Pipeline

```
Push to main
     │
     ▼
┌──────────────────────────────────────────────────────┐
│  PARALLEL SECURITY STAGE                              │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ Gitleaks    │ │ CodeQL       │ │ npm audit    │  │
│  └──────┬──────┘ └──────┬───────┘ └──────┬───────┘  │
└─────────┼───────────────┼────────────────┼───────────┘
          └───────────────┼────────────────┘
                          ▼
                   CI (Lint + Test)
                          │
                          ▼
               Docker Build → Trivy → SBOM (Syft) → ECR
                          │
                          ▼
                   Semantic Release
                   (commits → version → GitHub Release + SBOM)
                          │
               📢 Slack: "Deployment Starting"
                          │
                   ⏸ Manual Approval
                          │
                   Production Deploy ──▶ ✅ 📢 Slack Success
                          │
                    FAIL? └──▶ ⏪ Auto Rollback
                                    │
                               📢 Slack Rollback
                               🐛 Create GitHub Issue
```
