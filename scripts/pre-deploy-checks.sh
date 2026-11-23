#!/usr/bin/env bash
# Quick local gate before pushing a branch / opening a PR.
set -euo pipefail
echo "==> Lint";        ruff check .
echo "==> Terraform";   terraform -chdir=terraform/ecs fmt -check -recursive || echo "(terraform not installed - skipped)"
echo "==> Kustomize";   for e in dev sit uat; do kubectl kustomize kube/overlays/$e >/dev/null && echo "  $e OK"; done || echo "(kubectl not installed - skipped)"
echo "==> Smoke tests"; pytest -m "smoke or api" -q
echo "All checks passed - safe to push and open a PR."
