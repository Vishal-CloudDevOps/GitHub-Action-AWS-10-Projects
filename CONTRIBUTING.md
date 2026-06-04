# Contributing

Thank you for improving this learning repository!

---

## Adding a New Project

1. Create a new directory: `project-XX-short-name/`
2. Follow the existing structure:
   ```
   project-XX/
   ├── src/                   # Application source code
   ├── tests/                 # Test suite (positive + negative)
   ├── iam/                   # IAM policy JSONs
   ├── .github/workflows/     # GitHub Actions workflow
   ├── .eslintrc.js           # (if Node.js)
   ├── README.md              # Full setup guide (see template below)
   └── package.json / requirements.txt
   ```
3. Every README must include all sections listed in the README template
4. All workflows must have inline comments explaining each concept
5. Every test file must include both positive (✅) and negative (❌) tests

---

## README Template

Each project README must contain:

- [ ] Badges (CI status, language version, AWS services)
- [ ] Project overview (what it does in 2-3 sentences)
- [ ] Architecture diagram (ASCII)
- [ ] Learning objectives (checkboxes)
- [ ] Folder structure
- [ ] Local development instructions
- [ ] AWS setup steps with CLI commands
- [ ] GitHub Secrets table
- [ ] CI/CD workflow explained section
- [ ] Troubleshooting table
- [ ] AWS cost estimate
- [ ] Cleanup commands
- [ ] Next steps link

---

## Code Standards

- **Node.js:** ESLint + `eslint:recommended`; `prefer-const`, `eqeqeq`, `curly`
- **Python:** flake8 (max-line=100) + black + bandit
- **YAML:** 2-space indent; every step must have a `name:`
- **Terraform:** `terraform fmt` before committing; all variables must have `description`
- **Dockerfile:** Multi-stage; non-root user; HEALTHCHECK included
- **Commit messages:** Conventional Commits format (`feat:`, `fix:`, `docs:`, `chore:`)

---

## Submitting a PR

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/improve-project-03`
3. Make changes with conventional commit messages
4. Open a PR targeting `main`
5. Ensure all CI checks pass
6. One reviewer required for merge

---

## Reporting Issues

Use GitHub Issues with one of these labels:
- `bug` — Something broken in existing project
- `enhancement` — Improvement to existing project
- `new-project` — Proposal for an additional project
- `documentation` — README / docs improvement
