# UAT Automation Lab

A practice project for UAT test automation. It uses the same kinds of tools as an enterprise
Playwright/Python UAT framework. A small **Payments Portal** demo app is the application under test.

## Tools used

| Area | Tool | Where |
|---|---|---|
| Language | Python 3.12 | everywhere |
| UI automation | Playwright | `tests/pages`, `tests/locators` |
| Test runner | pytest, pytest-html | `pytest.ini` |
| BDD | pytest-bdd (Gherkin) | `tests/features`, `tests/steps` |
| API tests | requests | `tests/api` |
| App under test | FastAPI + Jinja2 | `app/` |
| AI agents | GitHub Copilot custom agents and skills | `.github/agents`, `.github/skills`, `.github/copilot-instructions.md` |
| AI failure analysis | Claude API (optional) + rule-based triage | `ai_analysis/` |
| Defect tracking | Jira REST API | `integrations/jira/` |
| Workflow orchestration | Temporal (POC) | `temporal_poc/` |
| Containers | Docker, docker-compose | `Dockerfile` |
| Kubernetes | Kustomize (dev / sit / uat overlays) | `kube/` |
| IaC | Terraform (ECS Fargate, ALB, ECR, IAM, Secrets Manager) | `terraform/ecs` |
| CI/CD | GitHub Actions (PR checks, UAT deploy, regression) | `.github/workflows` |
| Auth to AWS | GitHub OIDC (no stored AWS keys) | `terraform/ecs/iam.tf` |
| Lint | ruff | `ruff.toml` |

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
make install          # or: pip install -r requirements.txt && playwright install chromium
make test             # starts the app automatically and runs all tests
make run              # open http://127.0.0.1:8000  (login: uat_user / Passw0rd!)
```

Reports are written to `artifacts/`: `report.html`, `junit.xml`, and screenshots and traces of failed tests.
To open a trace, run `playwright show-trace artifacts/playwright/<test>/trace.zip`.

Run the tests against a deployed environment instead of the local app:
```bash
UAT_BASE_URL=http://<alb-dns> pytest -m regression
```

## Branching, pull requests and merges

```
feature/UAT-12-xyz ──PR──► develop ──PR (release)──► main ──auto──► deploy to UAT (ECS) ──► regression
```

| Event | Workflow | What runs |
|---|---|---|
| PR opened or updated (to `develop` or `main`) | `pr-checks.yml` | ruff lint, terraform validate, kustomize build, smoke + API tests, docker build |
| PR merged to `main` | `deploy-uat.yml` | build → push to ECR → deploy ECS → full regression |
| Weekdays 06:00 / manual | `uat-regression.yml` | full regression → AI analysis → Jira report |

### Daily flow (example ticket UAT-12)
```bash
git checkout develop && git pull
git checkout -b feature/UAT-12-payment-limit-tests
# ...write the feature, steps, page and locators...
./scripts/pre-deploy-checks.sh
git add . && git commit -m "UAT-12: add payment limit scenarios"
git push -u origin feature/UAT-12-payment-limit-tests
gh pr create --base develop --title "UAT-12: payment limit scenarios" --fill
# after review + green checks:
gh pr merge --squash --delete-branch
# release to UAT:
gh pr create --base main --head develop --title "Release to UAT"
gh pr merge --merge
```

## One-time setup

### 1. GitHub
1. Create the repo `uat-automation-lab`, then push `main` and `develop`.
2. **Settings → Branches → Add rule** for `main` and `develop`: require a pull request, at least 1 approval, and the status checks from **PR checks**. Block direct pushes.
3. **Settings → Environments → `uat`**: add yourself as a required reviewer, so each deploy needs manual approval.
4. **Secrets**: `AWS_DEPLOY_ROLE_ARN`, `UAT_USER`, `UAT_PASSWORD`, and optionally `ANTHROPIC_API_KEY`, `JIRA_EMAIL`, `JIRA_API_TOKEN`.
5. **Variables**: `UAT_BASE_URL`, and optionally `JIRA_URL`, `JIRA_PROJECT`.

### 2. AWS (Terraform)
```bash
cd terraform/ecs
terraform init && terraform apply
terraform output     # copy uat_base_url → UAT_BASE_URL var, github_deploy_role_arn → AWS_DEPLOY_ROLE_ARN secret
aws secretsmanager put-secret-value --secret-id payments-portal/uat/demo-password --secret-string 'Passw0rd!'
```
Then run **Deploy to UAT** manually once to push the first image.
When you finish practising, run `terraform destroy`, because the ALB and Fargate cost money.

### 3. Kubernetes (optional, local)
```bash
kind create cluster
docker build -t payments-portal:latest . && kind load docker-image payments-portal:latest
kubectl create ns payments-dev && kubectl apply -k kube/overlays/dev
kubectl -n payments-dev port-forward svc/payments-portal-dev 8000:80
```

### 4. Temporal POC (optional)
```bash
temporal server start-dev          # in a separate terminal
make run                           # in another terminal
python -m temporal_poc.workflow    # health → smoke → regression → AI analysis → Jira
```

## Copilot agents
In VS Code Copilot Chat (agent mode), pick:
- **uat-test-writer**: paste acceptance criteria and it writes the feature, steps, page object and locators.
- **failure-triage**: classifies a failed run and proposes fixes or Jira bugs.

## Practice tickets
1. UAT-1: Add an `@regression` scenario for logout.
2. UAT-2: Add a max payment limit (e.g. 10,000) to the app, plus UI and API tests for it.
3. UAT-3: Add a `sit` job to the deploy workflow that deploys `develop` to a second ECS service.
4. UAT-4: Run Playwright tests in parallel with `pytest-xdist`.
5. UAT-5: Send a Slack or Teams notification from `uat-regression.yml`.
6. UAT-6: Move Terraform state to S3 (uncomment the backend in `versions.tf`).
