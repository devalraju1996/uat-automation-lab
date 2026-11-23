.PHONY: install run test smoke regression lint analyze jira k8s-dev

install:      ## install deps + browser
	pip install -r requirements.txt && playwright install chromium
run:          ## run the app locally on :8000
	uvicorn app.main:app --reload
test:         ## all tests (app auto-starts)
	pytest
smoke:
	pytest -m "smoke or api"
regression:
	pytest -m regression
lint:
	ruff check . && ruff format --check .
analyze:      ## AI failure analysis of last run
	python -m ai_analysis.analyze_failures
jira:         ## post results to Jira (dry-run without JIRA_* vars)
	python -m integrations.jira.jira_reporter
k8s-dev:      ## deploy to local k8s (kind/minikube)
	kubectl apply -k kube/overlays/dev
