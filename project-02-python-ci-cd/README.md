# Project 02 — Python CI/CD

![CI](https://img.shields.io/github/actions/workflow/status/YOUR_ORG/github-actions-aws-cicd-learning/02-python-ci-cd.yml?label=CI&logo=github-actions)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)

> **Level:** ⭐⭐ Beginner+  
> **Concepts:** Matrix builds · pip caching · flake8 · black · bandit SAST · pip-audit · Artifact upload

---

## 📖 What This Project Does

A Python Flask REST API with a CI pipeline that runs across **multiple Python versions simultaneously** using matrix builds. You'll learn how to enforce code quality with `flake8` and `black`, scan for security issues with `bandit`, and produce a deployable artifact.

---

## 🏗️ Architecture

```
Push / PR
    │
    ▼
┌───────────────────────────────────────────────────┐
│                Python CI Pipeline                  │
│                                                    │
│  ┌─────────┐   ┌──────────┐   ┌───────────────┐  │
│  │ Secret  │   │  SAST    │   │  Dep Audit    │  │
│  │  Scan   │   │ (bandit) │   │ (pip-audit)   │  │
│  └────┬────┘   └────┬─────┘   └──────┬────────┘  │
│       ▼             │                 │            │
│  ┌─────────────┐    │                 │            │
│  │ Lint        │    │                 │            │
│  │ flake8+black│    │                 │            │
│  └──────┬──────┘    │                 │            │
│         ▼           ▼                 │            │
│  ┌───────────────────────────┐        │            │
│  │ Test Matrix               │        │            │
│  │  ├── Python 3.11          │        │            │
│  │  └── Python 3.12          │        │            │
│  └───────────────────────────┘        │            │
│         ▼                             │            │
│  ┌──────────────┐                     │            │
│  │ Build (.tar) │◄────────────────────┘            │
│  └──────────────┘                                  │
└───────────────────────────────────────────────────┘
```

---

## 🎯 Learning Objectives

- [ ] How `matrix.python-version` runs jobs in parallel
- [ ] Difference between `fail-fast: true` vs `false`
- [ ] How `cache: 'pip'` works and what it caches
- [ ] How `flake8` checks style vs `black` checking format
- [ ] What SAST scanning with `bandit` detects
- [ ] Why `pip-audit` is important for supply chain security
- [ ] How to package a Python app as a deployable tar.gz artifact

---

## 📁 Folder Structure

```
project-02-python-ci-cd/
├── app/
│   └── main.py                     # Flask application
├── tests/
│   └── test_main.py                # pytest tests
├── .github/
│   └── workflows/
│       └── 02-python-ci-cd.yml
├── requirements.txt                # Production deps
├── requirements-dev.txt            # Dev + test deps
├── pyproject.toml                  # pytest + coverage config
└── README.md
```

---

## 🚀 Local Development

```bash
cd project-02-python-ci-cd

# Create virtual environment
python -m venv venv
source venv/bin/activate     # Linux/Mac
venv\Scripts\activate        # Windows

# Install dev dependencies
pip install -r requirements-dev.txt

# Run app
python app/main.py
# → http://localhost:5000

# Run tests
pytest tests/ -v

# Lint
flake8 app/ tests/

# Format check
black --check app/ tests/

# Auto-format
black app/ tests/

# Security scan
bandit -r app/ -ll

# Dependency audit
pip-audit -r requirements.txt
```

---

## 🔑 GitHub Secrets Required

| Secret | Required | Description |
|--------|----------|-------------|
| `GITHUB_TOKEN` | Auto | Provided by GitHub |

No AWS secrets needed for this project.

---

## ⚙️ CI/CD Workflow Explained

### Matrix Builds

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
  fail-fast: false
```

GitHub spins up **two parallel runners** — one for each version. If `fail-fast: true`, a failure in one version immediately cancels the other. With `false`, both complete regardless, giving you full picture of compatibility.

### pip Caching

```yaml
- uses: actions/setup-python@v5
  with:
    cache: 'pip'
    cache-dependency-path: requirements-dev.txt
```

Caches `~/.cache/pip` keyed by requirements file hash. Saves ~60 seconds on repeat runs.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `flake8` errors | Run `flake8 app/ tests/` locally and fix issues |
| `black` check fails | Run `black app/ tests/` to auto-format, then commit |
| `bandit` fails | Review flagged code — usually hardcoded strings or use of `subprocess` |
| `pytest` fails | Run `PYTHONPATH=. pytest tests/ -v` locally |
| Import errors in tests | Ensure `PYTHONPATH=.` is set |

---

## 💰 AWS Cost

**No AWS resources.** Cost = $0.

---

## 📚 Next Steps

➡️ **Project 03** — Docker builds, ECR push, and Trivy container scanning.
