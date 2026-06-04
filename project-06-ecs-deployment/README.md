# Project 06 — ECS Fargate Deployment

![CI](https://img.shields.io/github/actions/workflow/status/YOUR_ORG/github-actions-aws-cicd-learning/06-ecs-deployment.yml)
![Docker](https://img.shields.io/badge/Docker-Fargate-blue?logo=docker)
![AWS ECS](https://img.shields.io/badge/AWS-ECS%20Fargate-orange?logo=amazon-aws)

> **Level:** ⭐⭐⭐⭐ Intermediate-Advanced  
> **Concepts:** ECR push · ECS task definitions · Rolling deployments · Job outputs · Trivy scan gating

---

## 📖 What This Project Does

Builds a Docker image, scans it with Trivy (blocking on CRITICAL/HIGH CVEs), pushes to ECR, renders an ECS task definition with the new image URI, and deploys to **ECS Fargate** with a rolling update strategy.

---

## 🏗️ Architecture

```
Push to main
     │
     ▼
Test → Build Docker Image → Trivy Scan
                                 │
                         (fail on CVEs)
                                 │ pass
                                 ▼
                          Push to ECR
                          :sha-abc123
                          :latest
                                 │
                                 ▼
                    Render Task Definition
                    (inject new image URI)
                                 │
                                 ▼
                    ECS Rolling Deploy
                    ┌──────────────────────┐
                    │  ECS Cluster         │
                    │  ├── Task v1 (old)   │ ← stops
                    │  └── Task v2 (new)   │ ← starts
                    └──────────────────────┘
                    wait-for-service-stability: true
                                 │
                                 ▼
                    ALB → healthy tasks only
```

---

## 🎯 Learning Objectives

- [ ] How `job outputs` pass the image URI between build and deploy jobs
- [ ] How `amazon-ecs-render-task-definition` injects the new image
- [ ] How `amazon-ecs-deploy-task-definition` triggers a rolling update
- [ ] What `wait-for-service-stability: true` does
- [ ] Why Trivy must run BEFORE push (not after)
- [ ] How ECS rolling deployments maintain availability

---

## ☁️ AWS Setup

### Step 1: Create ECR Repository
```bash
aws ecr create-repository \
  --repository-name project-06-app \
  --region us-east-1
```

### Step 2: Create ECS Cluster
```bash
aws ecs create-cluster \
  --cluster-name project-06-cluster \
  --capacity-providers FARGATE
```

### Step 3: Create CloudWatch Log Group
```bash
aws logs create-log-group --log-group-name /ecs/project-06-app
```

### Step 4: Create ECS Task Execution Role
```bash
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

### Step 5: Register Initial Task Definition
```bash
# Replace YOUR_ACCOUNT_ID and IMAGE_URI_PLACEHOLDER with actual ECR image
aws ecs register-task-definition \
  --cli-input-json file://ecs/task-definition.json
```

### Step 6: Create ECS Service
```bash
aws ecs create-service \
  --cluster project-06-cluster \
  --service-name project-06-service \
  --task-definition project-06-app \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## 🔑 GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `AWS_ACCOUNT_ID` | 12-digit AWS account ID |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| Trivy fails the build | Update base image in Dockerfile or add `.trivyignore` for accepted risks |
| Task definition render fails | Check container name matches `CONTAINER_NAME` env var |
| Service doesn't stabilize | Check CloudWatch logs `/ecs/project-06-app`; check health check endpoint |
| OIDC auth fails | Ensure role has `iam:PassRole` for the execution role |

---

## 💰 AWS Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| ECS Fargate (2 tasks × 0.25 vCPU × 0.5GB × 720hrs) | ~$14.40 |
| ECR storage (1GB) | ~$0.10 |
| ALB | ~$16.20 |
| CloudWatch Logs | ~$0.50 |
| **Total** | **~$31.20/month** |

---

## 🧹 Cleanup

```bash
aws ecs update-service --cluster project-06-cluster --service project-06-service --desired-count 0
aws ecs delete-service --cluster project-06-cluster --service project-06-service --force
aws ecs delete-cluster --cluster project-06-cluster
aws ecr delete-repository --repository-name project-06-app --force
aws logs delete-log-group --log-group-name /ecs/project-06-app
```

---

## 📚 Next Steps

➡️ **Project 07** — Deploy a Python Lambda function with AWS SAM and API Gateway.
