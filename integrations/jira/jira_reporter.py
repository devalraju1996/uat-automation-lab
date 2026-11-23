"""Post UAT results to Jira: comment on the ticket under test, and raise a
Bug for each failure. Runs in dry-run mode unless JIRA_* env vars are set.

Env: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT, JIRA_ISSUE (story key)
Usage: python -m integrations.jira.jira_reporter
"""

import json
import os
from pathlib import Path

import requests

URL, EMAIL, TOKEN = os.getenv("JIRA_URL"), os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")
PROJECT, ISSUE = os.getenv("JIRA_PROJECT", "UAT"), os.getenv("JIRA_ISSUE")
DRY_RUN = not (URL and EMAIL and TOKEN)


def _adf(text: str) -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
    }


def _post(path: str, payload: dict):
    if DRY_RUN:
        print(f"[dry-run] POST {path}\n{json.dumps(payload, indent=2)[:400]}")
        return {"key": "DRY-1"}
    r = requests.post(f"{URL}/rest/api/3/{path}", json=payload, auth=(EMAIL, TOKEN), timeout=30)
    r.raise_for_status()
    return r.json() if r.content else {}


def main():
    failures_file = Path("artifacts/failures.json")
    failures = json.loads(failures_file.read_text()) if failures_file.exists() else []
    run_url = os.getenv("RUN_URL", "local run")
    summary = f"UAT run {'PASSED' if not failures else f'FAILED ({len(failures)} failures)'} - {run_url}"
    if ISSUE:
        _post(f"issue/{ISSUE}/comment", {"body": _adf(summary)})
    for f in failures:
        bug = _post(
            "issue",
            {
                "fields": {
                    "project": {"key": PROJECT},
                    "issuetype": {"name": "Bug"},
                    "summary": f"[UAT] {f['test'].split('::')[-1]} failed",
                    "description": _adf(f"{f['message']}\n\nRun: {run_url}"),
                    "labels": ["uat-automation"],
                }
            },
        )
        print(f"Raised {bug.get('key')} for {f['test']}")
    print(summary)


if __name__ == "__main__":
    main()
