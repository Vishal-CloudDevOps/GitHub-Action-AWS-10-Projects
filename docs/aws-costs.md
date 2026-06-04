# AWS Cost Reference

Estimated monthly costs for each project. All estimates assume **us-east-1**, low traffic, and non-production usage patterns.

---

## Cost Summary Table

| Project | AWS Services | Est. Monthly Cost |
|---------|-------------|-------------------|
| 01 | None | **$0.00** |
| 02 | None | **$0.00** |
| 03 | ECR | **~$0.01** |
| 04 | S3 + CloudFront | **~$1.00** |
| 05 | EC2 t3.micro + S3 + DynamoDB | **~$8.52** |
| 06 | ECS Fargate + ECR + ALB + CloudWatch | **~$31.20** |
| 07 | Lambda + API Gateway + S3 + CloudWatch | **~$4.01** |
| 08 | Depends on deployment target | **Varies** |
| 09 | EKS + EC2 nodes + ECR | **~$149.00** |
| 10 | ECR (pipeline only) | **~$0.10** |

---

## Breakdown By Project

### Project 03 — ECR Only
- ECR storage: $0.10/GB/month
- ~50MB image = ~$0.005/month

### Project 04 — S3 + CloudFront
- S3 storage (5GB): $0.115/month
- CloudFront (10GB transfer, 100k requests): ~$0.85/month
- **Total: ~$1.00/month**

### Project 05 — EC2 + Terraform State
- EC2 t3.micro (24/7): $8.47/month
- S3 state bucket: ~$0.01/month
- DynamoDB (on-demand, minimal): ~$0.01/month
- **Total: ~$8.52/month**
- 💡 Use `terraform destroy` after each session — cost drops to ~$0.02/month

### Project 06 — ECS Fargate
- ECS Fargate (2 tasks × 0.25 vCPU × 0.5GB × 720h): ~$14.40/month
- ALB: ~$16.20/month
- ECR: ~$0.10/month
- CloudWatch Logs: ~$0.50/month
- **Total: ~$31.20/month**
- 💡 Scale desired count to 0 when not testing: `aws ecs update-service --desired-count 0`

### Project 07 — Lambda + API Gateway
- Lambda: Free tier covers 1M requests/month (permanent)
- API Gateway: $3.50 per million requests (~$0.35 for 100k)
- CloudWatch Logs: ~$0.50/month
- S3 artifacts: ~$0.01/month
- **Total: ~$4.01/month** (essentially free under free tier)

### Project 09 — EKS (Most Expensive)
- EKS cluster (control plane): $72.00/month — **charged even when idle**
- EC2 t3.medium × 2: $60.74/month
- ECR: ~$0.10/month
- **Total: ~$149/month**
- ⚠️ **Delete the cluster immediately after learning!**
  ```bash
  eksctl delete cluster --name project-09-cluster --region us-east-1
  ```

---

## Cost-Saving Tips

1. **Use AWS Free Tier** — New accounts get 12 months of free tier for EC2, S3, Lambda, etc.

2. **Destroy when done** — Run cleanup commands in each README after completing each project.

3. **Set billing alerts**
   ```bash
   aws budgets create-budget \
     --account-id YOUR_ACCOUNT_ID \
     --budget '{"BudgetName":"LearningBudget","BudgetLimit":{"Amount":"10","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}' \
     --notifications-with-subscribers '[{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN","Threshold":80},"Subscribers":[{"SubscriptionType":"EMAIL","Address":"your@email.com"}]}]'
   ```

4. **Use t3.micro/t2.micro** — Free tier eligible for EC2. Projects default to t3.micro.

5. **Schedule stop/start** — Use AWS Instance Scheduler for EC2 instances used only during business hours.

6. **Spot instances** — For EKS learning nodes, use Spot instances for ~70% savings.
