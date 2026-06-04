# Project 09 — Kubernetes EKS Deployment (Helm)

![CI](https://img.shields.io/github/actions/workflow/status/YOUR_ORG/github-actions-aws-cicd-learning/09-kubernetes-eks.yml)
![Kubernetes](https://img.shields.io/badge/Kubernetes-EKS-blue?logo=kubernetes)
![Helm](https://img.shields.io/badge/Helm-3.14-blue?logo=helm)

> **Level:** ⭐⭐⭐⭐⭐ Advanced
> **Concepts:** EKS auth · Helm lint/deploy · kubectl rollout · HPA · Liveness/readiness probes · --atomic rollback

---

## 📖 What This Project Does

Deploys a Node.js app to **Amazon EKS** using **Helm**. The pipeline builds and scans a Docker image, pushes it to ECR, then uses `helm upgrade --install` with `--atomic` to deploy — automatically rolling back if the deployment fails.

---

## 🏗️ Architecture

```
Push to main
     │
     ▼
Test + Helm Lint
     │
     ▼
Build Docker → Trivy Scan → Push to ECR
     │
     ▼
aws eks update-kubeconfig (OIDC)
     │
     ▼
helm upgrade --install --atomic
     │
     ├── Creates/updates Deployment (2 replicas)
     ├── Creates/updates Service (ClusterIP)
     └── Creates/updates HPA (2-10 pods)
     │
     ▼
kubectl rollout status (wait for stability)
     │
     ▼
EKS Cluster:
  Namespace: project-09
  ├── Pod 1 (node-1)
  ├── Pod 2 (node-2)
  └── Service → ALB Ingress → Internet

Rolling Update Strategy:
  maxSurge: 1       (briefly run 3 pods during update)
  maxUnavailable: 0 (always have 2 healthy pods)
```

---

## 🎯 Learning Objectives

- [ ] How `aws eks update-kubeconfig` authenticates kubectl to EKS
- [ ] Why `helm upgrade --install` is idempotent (works for first deploy and updates)
- [ ] What `--atomic` does (auto-rollback on failure)
- [ ] Difference between liveness probe and readiness probe
- [ ] How HPA automatically scales pods based on CPU
- [ ] How `readOnlyRootFilesystem: true` hardens containers
- [ ] What the Downward API is (injecting pod metadata as env vars)
- [ ] How `helm template` lets you preview rendered manifests locally

---

## 📁 Folder Structure

```
project-09-kubernetes-eks/
├── src/
│   └── app.js
├── manifests/
│   ├── deployment.yaml             # Raw K8s deployment manifest
│   └── service.yaml                # Service + HPA
├── helm/
│   └── app/
│       ├── Chart.yaml
│       ├── values.yaml             # Default values
│       └── templates/
│           ├── deployment.yaml     # Helm template
│           └── service.yaml        # Service + HPA template
├── iam/
│   └── eks-deploy-policy.json
├── .github/
│   └── workflows/
│       └── 09-kubernetes-eks.yml
├── Dockerfile
└── README.md
```

---

## ☁️ AWS Setup

### Step 1: Create EKS Cluster (using eksctl)

```bash
# Install eksctl
curl --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" \
  | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster (takes ~15 minutes)
eksctl create cluster \
  --name project-09-cluster \
  --region us-east-1 \
  --nodegroup-name standard-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 4 \
  --managed
```

### Step 2: Create ECR Repository

```bash
aws ecr create-repository \
  --repository-name project-09-app \
  --region us-east-1
```

### Step 3: Grant GitHub Actions IAM Role access to EKS

EKS uses its own RBAC — the IAM role must be mapped to a Kubernetes ClusterRole:

```bash
# Get your current kubeconfig
aws eks update-kubeconfig --region us-east-1 --name project-09-cluster

# Edit the aws-auth configmap to add your GitHub Actions role
kubectl edit configmap aws-auth -n kube-system
```

Add this under `mapRoles`:

```yaml
- rolearn: arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActionsEKSRole
  username: github-actions
  groups:
    - system:masters    # Or create a more restrictive ClusterRole
```

### Step 4: Install metrics-server (for HPA)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

---

## 🔑 GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |

---

## 🏃 Local Helm Usage

```bash
# Install Helm
brew install helm    # Mac
choco install kubernetes-helm    # Windows

# Lint chart
helm lint helm/app

# Dry-run render (see what will be deployed)
helm template project-09 helm/app \
  --set image.tag=sha-test123 \
  --namespace project-09

# Deploy manually
helm upgrade --install project-09 helm/app \
  --namespace project-09 \
  --create-namespace \
  --set image.tag=latest
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `helm: command not found` | Install Helm via `azure/setup-helm@v4` action |
| OIDC auth OK but kubectl fails | Check aws-auth configmap has the GitHub Actions role |
| Pods in `CrashLoopBackOff` | `kubectl logs pod-name -n project-09` |
| HPA shows `<unknown>` | Install metrics-server on the cluster |
| `--atomic` rolls back | Check pod logs and events: `kubectl describe pod -n project-09` |
| Image pull error | Verify ECR region matches cluster region; check IAM role |

---

## 💰 AWS Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| EKS cluster (control plane) | $72.00 |
| EC2 nodes (2x t3.medium) | ~$60.74 |
| ECR storage (1GB) | ~$0.10 |
| ALB Ingress (optional) | ~$16.20 |
| **Total** | **~$149/month** |

> ⚠️ EKS is the most expensive project. Delete the cluster after learning!

---

## 🧹 Cleanup

```bash
# Uninstall Helm release
helm uninstall project-09 -n project-09

# Delete namespace
kubectl delete namespace project-09

# Delete EKS cluster (takes ~10 minutes)
eksctl delete cluster --name project-09-cluster --region us-east-1

# Delete ECR
aws ecr delete-repository --repository-name project-09-app --force
```

---

## 📚 Next Steps

➡️ **Project 10** — Enterprise pipeline: reusable workflows, composite actions, Slack notifications, SBOM, semantic versioning, and rollback strategy.
