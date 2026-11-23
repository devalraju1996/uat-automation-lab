# Copilot instructions for uat-automation-lab

- Stack: Python 3.12, Playwright (sync API), pytest, pytest-bdd.
- UI tests follow Page Object Model:
  - selectors live ONLY in `tests/locators/*.py` (prefer `data-testid`)
  - page actions live in `tests/pages/*.py`
  - Gherkin in `tests/features/*.feature`, step code in `tests/steps/test_*_steps.py`
- Tag every scenario `@smoke` or `@regression`.
- Never hard-code credentials or URLs - use fixtures `credentials` and `app_url`.
- No `time.sleep`; use Playwright auto-wait / `expect`.
- Each new test must pass locally (`make test`) before opening a PR.
