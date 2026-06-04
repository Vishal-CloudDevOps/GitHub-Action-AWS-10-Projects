# Troubleshooting Guide

Common issues across all 10 projects, with causes and fixes.

---

## GitHub Actions — General

| Problem | Cause | Fix |
|---------|-------|-----|
| Workflow not triggering | `paths:` filter doesn't match changed files | Push a change inside the project folder, or temporarily remove `paths:` filter |
| Job skipped with no reason | `if:` condition evaluated to false | Add `echo "${{ toJson(needs) }}"` step to debug needs context |
| `GITHUB_TOKEN: Resource not accessible` | Missing permission | Add the required permission under `permissions:` block |
| Cache always missed | `cache-dependency-path` file path wrong | Verify the path relative to repo root |
| Artifact upload fails | Path doesn't exist | Check that the previous step actually created files at that path |
| `cancel-in-progress` cancelled deploy | Concurrent run triggered | Set `cancel-in-progress: false` for deploy jobs |

---

## AWS Authentication

| Problem | Cause | Fix |
|---------|-------|-----|
| `Error: Credentials could not be loaded` | OIDC provider not set up | Follow `docs/oidc-setup.md` Step 1 |
| `Not authorized: sts:AssumeRoleWithWebIdentity` | Wrong account ID in role ARN | Verify `AWS_ACCOUNT_ID` secret value |
| `id-token permission denied` | Missing `id-token: write` permission | Add to workflow `permissions:` block |
| Trust policy condition mismatch | `sub` field doesn't match repo | Check org/repo name exact spelling in trust policy |
| Access key works locally but not CI | Different IAM identity | Ensure CI role has the same permissions as your local user |

---

## Docker / ECR

| Problem | Cause | Fix |
|---------|-------|-----|
| `no space left on device` | GitHub runner disk full | Use `docker system prune` step before build |
| `manifest unknown` | Wrong ECR region | Verify `AWS_REGION` matches ECR repository region |
| `denied: User is not authorized to perform: ecr:GetAuthorizationToken` | IAM role missing ECR auth permission | Add `ecr:GetAuthorizationToken` on `Resource: "*"` |
| Trivy fails with CVEs | Vulnerable base image | Update `FROM node:20-alpine` to latest patch, or add `.trivyignore` |
| Docker build cache miss | First run, or `Dockerfile` changed | Normal on first run — cache populates automatically |

---

## Terraform

| Problem | Cause | Fix |
|---------|-------|-----|
| `Error acquiring the state lock` | Concurrent apply, or previous apply crashed | Run `terraform force-unlock LOCK_ID` with the DynamoDB lock ID |
| `Backend config changed` | S3 bucket/key changed since last init | Run `terraform init -reconfigure` |
| `terraform fmt` fails CI | Unformatted files committed | Run `terraform fmt -recursive` locally and commit |
| Plan says "no changes" unexpectedly | State drifted (resource deleted manually) | Run `terraform refresh` to sync state |
| `Error: No valid credential sources` | OIDC role missing DynamoDB/S3 permissions | Check `iam/terraform-permissions.json` includes state backend permissions |

---

## ECS

| Problem | Cause | Fix |
|---------|-------|-----|
| Service not stabilizing | Container health check failing | Check CloudWatch Logs: `/ecs/project-06-app` |
| `CannotPullContainerError` | ECS task execution role can't pull from ECR | Attach `AmazonECSTaskExecutionRolePolicy` to execution role |
| Task keeps stopping | Container exits with non-zero code | `kubectl logs` / CloudWatch logs for error details |
| `ROLLBACK_COMPLETE` stack | CloudFormation deploy failed | Check stack events in AWS Console for root cause |

---

## Lambda / SAM

| Problem | Cause | Fix |
|---------|-------|-----|
| `sam build` fails | Docker not running (for `--use-container`) | Start Docker Desktop, or remove `--use-container` flag |
| Cold start timeout in smoke test | Lambda warming up | Increase retry sleep from 10s to 20s |
| `CAPABILITY_IAM` error | SAM creates IAM roles | Add `--capabilities CAPABILITY_IAM` to `sam deploy` |
| Stack in `UPDATE_ROLLBACK_FAILED` | Failed update left stack broken | Manually fix via CloudFormation console "Continue Update Rollback" |

---

## Kubernetes / EKS

| Problem | Cause | Fix |
|---------|-------|-----|
| `Unauthorized` from kubectl | GitHub Actions role not in aws-auth configmap | Edit `aws-auth` configmap to add the IAM role |
| HPA shows `<unknown>` metrics | metrics-server not installed | `kubectl apply -f https://...metrics-server.../components.yaml` |
| Pod stuck in `ImagePullBackOff` | ECR credentials not accessible from EKS node | Attach ECR pull policy to EKS node role |
| `helm` upgrade leaves pods in bad state | `--atomic` not used | Add `--atomic` flag to auto-rollback on failure |
| Deployment stuck | Readiness probe too strict | Increase `initialDelaySeconds` in readiness probe |

---

## Semantic Release / Project 10

| Problem | Cause | Fix |
|---------|-------|-----|
| No release created | Commit messages don't follow Conventional Commits | Use `feat:`, `fix:`, `BREAKING CHANGE:` prefixes |
| `GITHUB_TOKEN: Permission denied` to push | Missing `contents: write` permission | Add `contents: write` to workflow permissions |
| Release created but wrong version | Squash merge loses commit history | Use merge commits or rebase merge instead of squash |
| Slack notification not sent | Invalid webhook URL | Verify `SLACK_WEBHOOK_URL` secret; test webhook with curl |
