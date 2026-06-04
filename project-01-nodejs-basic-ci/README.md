# Project 01 — Basic Node.js CI

![CI Status](https://img.shields.io/github/actions/workflow/status/YOUR_ORG/github-actions-aws-cicd-learning/01-nodejs-basic-ci.yml?label=CI&logo=github-actions)
![Node.js](https://img.shields.io/badge/Node.js-18%2B-green?logo=node.js)
![License](https://img.shields.io/badge/license-MIT-blue)

> **Learning Level:** ⭐ Beginner
> **Concepts:** Workflow triggers · Jobs & Steps · npm caching · Lint · Tests · Artifacts · Secret scanning

---

## 📖 What This Project Does

A simple Express REST API with a CI pipeline that runs on every push and pull request. It teaches you the **fundamental building blocks** of GitHub Actions: how workflows are structured, how to cache dependencies for speed, and how to run quality checks automatically.

---

## 🏗️ Architecture

```
Developer pushes code
        │
        ▼
┌─────────────────────────────────────────────────┐
│              GitHub Actions Pipeline             │
│                                                  │
│  ┌─────────────┐    ┌──────────┐                │
│  │ Secret Scan │    │  Audit   │                │
│  │ (Gitleaks)  │    │(npm audit│                │
│  └──────┬──────┘    └────┬─────┘                │
│         │               │                       │
│         ▼               │                       │
│  ┌──────────────┐        │                      │
│  │  Lint        │        │                      │
│  │  (ESLint)    │        │                      │
│  └──────┬───────┘        │                      │
│         ▼                │                      │
│  ┌──────────────────────────────────┐           │
│  │  Test (Jest) — Node 18 & 20 matrix│          │
│  └──────────────────────────────────┘           │
│         ▼                                       │
│  ┌──────────────┐                               │
│  │   Summary    │                               │
│  └──────────────┘                               │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Learning Objectives

After completing this project you will understand:

- [ ] How to write a GitHub Actions workflow YAML file
- [ ] The difference between `push`, `pull_request`, and `workflow_dispatch` triggers
- [ ] What `jobs`, `steps`, and `needs` do
- [ ] How to cache `node_modules` to speed up workflows
- [ ] How `matrix` strategy runs jobs in parallel on multiple versions
- [ ] How to upload test coverage as a build artifact
- [ ] Why `npm ci` is better than `npm install` in CI environments
- [ ] How to scan for accidentally committed secrets with Gitleaks

---

## 📁 Folder Structure

```
project-01-nodejs-basic-ci/
├── src/
│   └── app.js                          # Express application
├── tests/
│   └── app.test.js                     # Jest tests (positive + negative)
├── .github/
│   └── workflows/
│       └── 01-nodejs-basic-ci.yml      # GitHub Actions workflow
├── .eslintrc.js                        # ESLint configuration
├── package.json
└── README.md
```

---

## ✅ Prerequisites

- Node.js 18+
- npm 9+
- Git

---

## 🚀 Local Development

```bash
# 1. Navigate to project
cd project-01-nodejs-basic-ci

# 2. Install dependencies
npm install

# 3. Run the app locally
npm start
# → http://localhost:3000

# 4. Run tests
npm test

# 5. Run linter
npm run lint

# 6. Check for vulnerabilities
npm audit
```

### API Endpoints

| Method | Path            | Description         |
|--------|-----------------|---------------------|
| GET    | `/`             | Welcome message     |
| GET    | `/health`       | Health check        |
| POST   | `/api/add`      | Add two numbers     |
| POST   | `/api/multiply` | Multiply two numbers|

**Example:**
```bash
curl -X POST http://localhost:3000/api/add \
  -H "Content-Type: application/json" \
  -d '{"a": 5, "b": 3}'
# {"result": 8}
```

---

## ⚙️ CI/CD Workflow Explained

### Triggers

```yaml
on:
  push:
    branches: [main, develop]   # Runs on every push to main/develop
  pull_request:
    branches: [main]            # Runs on every PR to main
  workflow_dispatch:            # Allows manual trigger from GitHub UI
```

### Job Flow

```
secret-scan ──┬──▶ lint ──▶ test (matrix: Node 18 & 20) ──▶ summary
              │
              └──▶ dependency-audit ──────────────────────────────────▶ summary
```

### Dependency Caching

```yaml
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
    cache-dependency-path: package-lock.json
```

This caches `~/.npm` keyed by the hash of `package-lock.json`.
**Without cache:** ~45 seconds. **With cache:** ~5 seconds.

### Matrix Strategy

```yaml
strategy:
  matrix:
    node-version: ['18', '20']
```

Runs the test job **twice in parallel** — once for Node 18, once for Node 20. Ensures your code works on both versions.

---

## 🔐 Security Features

| Feature | Tool | What It Catches |
|---------|------|-----------------|
| Secret scanning | Gitleaks | API keys, passwords, tokens in commits |
| Dependency audit | npm audit | Known CVEs in npm packages |
| Code linting | ESLint | Code quality, potential bugs |

---

## 🔑 GitHub Secrets Required

This project has **no AWS deployments**, so no secrets are required beyond the automatic `GITHUB_TOKEN`.

| Secret | Required | Description |
|--------|----------|-------------|
| `GITHUB_TOKEN` | Auto | Provided by GitHub automatically |

---

## 📦 Build Artifacts

After each run, a **coverage report** is uploaded as an artifact:

1. Go to your Actions run
2. Scroll to **Artifacts**
3. Download `coverage-report-node20`
4. Open `coverage/lcov-report/index.html` in a browser

---

## 🐛 Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `npm ci` fails | `package-lock.json` missing | Run `npm install` locally and commit the lockfile |
| ESLint fails | Lint errors in code | Run `npm run lint:fix` locally |
| Tests fail | Code changes broke tests | Check test output; run `npm test` locally first |
| Cache not working | First run or lockfile changed | Normal — cache gets populated on first run |
| Gitleaks fails | Secret detected in commit | Remove the secret, rotate it, and use `git rebase` to purge from history |

---

## 💰 AWS Cost

**This project has no AWS resources.** Cost = $0.

---

## 📚 Next Steps

➡️ Move to **Project 02** to learn matrix builds with multiple Python versions and artifact uploading.
