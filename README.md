# GitHub Actions × AWS CI/CD Learning Repository

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?logo=amazon-aws&logoColor=white)
![Projects](https://img.shields.io/badge/Projects-10-blue)
![Level](https://img.shields.io/badge/Level-Beginner%20→%20Expert-green)

> **10 hands-on projects** that teach GitHub Actions and AWS deployment — from your first workflow trigger to a full enterprise CI/CD pipeline with security scanning, SBOM generation, semantic versioning, Slack notifications, and automatic rollback.

---

## 🗺️ Learning Path

```
⭐           ⭐⭐          ⭐⭐⭐         ⭐⭐⭐⭐        ⭐⭐⭐⭐⭐
│             │             │              │              │
01            02            03             05             09
Node.js CI    Python CI/CD  Docker+ECR    Terraform      Kubernetes EKS
              matrix builds Trivy scan    plan→apply     Helm deploy
                            │              │              │
                            04             06             10
                            React→S3+CF   ECS Fargate    Enterprise
                                          rolling deploy  Pipeline
                                                         │
                                          07             08
                                          Lambda SAM     Multi-Env
                                                         dev→stage→prod
```

---

## 📦 Projects

| # | Project | Key Concepts | AWS Services | Level |
|---|---------|-------------|--------------|-------|
| 01 | [Node.js Basic CI](project-01-nodejs-basic-ci/) | Triggers, jobs, caching, matrix | None | ⭐ |
| 02 | [Python CI/CD](project-02-python-ci-cd/) | Matrix builds, bandit SAST, pip-audit, artifacts | None | ⭐⭐ |
| 03 | [Dockerized App](project-03-dockerized-app/) | Multi-stage Docker, Trivy, ECR push, OIDC | ECR | ⭐⭐⭐ |
| 04 | [React → S3 + CloudFront](project-04-react-s3-cloudfront/) | Frontend CI, S3 sync, cache headers, CF invalidation | S3, CloudFront | ⭐⭐⭐ |
| 05 | [Terraform Infrastructure](project-05-terraform-infra/) | fmt/validate/plan/apply, remote state, approvals | VPC, EC2, S3, DynamoDB | ⭐⭐⭐⭐ |
| 06 | [ECS Fargate Deployment](project-06-ecs-deployment/) | Task definitions, rolling updates, service stability | ECS, ECR, ALB | ⭐⭐⭐⭐ |
| 07 | [Lambda Serverless](project-07-lambda-serverless/) | SAM validate/build/deploy, API Gateway, smoke tests | Lambda, API GW | ⭐⭐⭐⭐ |
| 08 | [Multi-Environment](project-08-multi-environment/) | Reusable workflows, approval gates, promotion flow | Any | ⭐⭐⭐⭐⭐ |
| 09 | [Kubernetes EKS](project-09-kubernetes-eks/) | Helm, kubectl, EKS auth, HPA, --atomic rollback | EKS, ECR | ⭐⭐⭐⭐⭐ |
| 10 | [Enterprise Pipeline](project-10-enterprise-pipeline/) | CodeQL, SBOM, semantic versioning, Slack, rollback | ECR | ⭐⭐⭐⭐⭐ |

---

## 🚀 Getting Started

### Prerequisites

- GitHub account
- AWS account ([free tier](https://aws.amazon.com/free/) works for most projects)
- Git installed locally
- Node.js 18+ (for local development)
- Python 3.11+ (for Project 02 and 07)
- Docker (for Projects 03, 06, 09, 10)
- AWS CLI v2 (`aws --version`)

### Step 1: Fork & Clone

```bash
# Fork this repo on GitHub, then:
git clone https://github.com/YOUR_ORG/github-actions-aws-cicd-learning.git
cd github-actions-aws-cicd-learning
```

### Step 2: Configure AWS

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Configure credentials
aws configure
```

### Step 3: Set Up OIDC (for AWS deployment projects)

See [docs/oidc-setup.md](docs/oidc-setup.md) for a step-by-step walkthrough.

### Step 4: Add GitHub Secrets

See [docs/secrets-setup.md](docs/secrets-setup.md) for the full secrets reference.

### Step 5: Start with Project 01

```bash
cd project-01-nodejs-basic-ci
npm install
npm test
```

Push a change and watch the workflow run in the **Actions** tab.

---

## 🔐 Security Architecture

Every project implements security at multiple layers:

```
Layer               Tool              Projects
─────────────────────────────────────────────────────
Secret scanning     Gitleaks          All
Dependency audit    npm audit         01, 03, 04, 08, 10
Dependency audit    pip-audit         02, 07
SAST code scan      bandit            02, 07
SAST code scan      CodeQL            10
Container scan      Trivy image       03, 06, 09, 10
Filesystem scan     Trivy fs          10
IaC scan            tfsec             05
SBOM generation     Syft (Anchore)    10
AWS auth            OIDC (keyless)    03–10
```

---

## 📁 Repository Structure

```
github-actions-aws-cicd-learning/
│
├── project-01-nodejs-basic-ci/         # ⭐ Beginner
├── project-02-python-ci-cd/            # ⭐⭐
├── project-03-dockerized-app/          # ⭐⭐⭐
├── project-04-react-s3-cloudfront/     # ⭐⭐⭐
├── project-05-terraform-infra/         # ⭐⭐⭐⭐
├── project-06-ecs-deployment/          # ⭐⭐⭐⭐
├── project-07-lambda-serverless/       # ⭐⭐⭐⭐
├── project-08-multi-environment/       # ⭐⭐⭐⭐⭐
├── project-09-kubernetes-eks/          # ⭐⭐⭐⭐⭐
├── project-10-enterprise-pipeline/     # ⭐⭐⭐⭐⭐
│
├── reusable-workflows/                 # Shared workflow templates
│   ├── nodejs-ci.yml
│   ├── docker-ecr.yml
│   └── terraform.yml
│
├── composite-actions/                  # Shared action building blocks
│   ├── setup-aws/action.yml
│   └── docker-build-push/action.yml
│
├── docs/
│   ├── oidc-setup.md                   # AWS OIDC configuration guide
│   ├── secrets-setup.md                # GitHub Secrets reference
│   ├── troubleshooting.md              # Common problems & fixes
│   └── aws-costs.md                    # Cost estimates per project
│
├── diagrams/
│   └── architecture-overview.md        # ASCII architecture diagrams
│
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## 🎓 GitHub Actions Concepts Covered

| Concept | First Seen In |
|---------|--------------|
| `on: push / pull_request` | Project 01 |
| `workflow_dispatch` with inputs | Project 01 |
| `on: schedule` | Project 01 workflow |
| Dependency caching | Project 01 |
| Matrix strategy | Project 01, 02 |
| Artifact upload/download | Project 02 |
| `concurrency` groups | Project 03 |
| OIDC authentication | Project 03 |
| `docker/build-push-action` | Project 03 |
| Environment protection rules | Project 05 |
| PR comments from workflow | Project 05 |
| Job `outputs:` | Project 06 |
| `workflow_call` (reusable) | Project 08 |
| Composite actions | Composite actions folder |
| `if: failure()` rollback | Project 10 |
| `github-script` action | Project 10 |
| SBOM generation | Project 10 |
| Semantic versioning | Project 10 |
| Slack notifications | Project 10 |

---

## 💰 Cost Overview

| Projects | Total Monthly Cost |
|----------|-------------------|
| 01–02 | $0.00 |
| 03–04 | ~$1.01 |
| 05–07 | ~$43.73 |
| 08 | Varies by deployment |
| 09 | ~$149.00 ⚠️ |
| 10 | ~$0.10 |

> See [docs/aws-costs.md](docs/aws-costs.md) for detailed breakdown and cost-saving tips.
> Always run cleanup commands from each README when done learning!

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new projects or improving existing ones.

---

## 📄 License

MIT — see [LICENSE](LICENSE).
