"""AI-assisted test failure analysis.

Reads artifacts/junit.xml, classifies each failure and writes
artifacts/failure_analysis.md. If ANTHROPIC_API_KEY is set it asks Claude
for a root-cause summary; otherwise it uses simple rule-based triage.

Usage: python -m ai_analysis.analyze_failures [path/to/junit.xml]
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

RULES = [
    ("waiting for locator", "Locator", "Locator not found - UI may have changed, update locators/."),
    ("TimeoutError", "Environment/Performance", "Page or element took too long - check UAT env health."),
    ("ConnectionError", "Environment", "UAT app unreachable - check deployment / network."),
    ("AssertionError", "Functional", "Behaviour differs from expected - possible real defect."),
]


def parse_failures(junit_path: Path) -> list[dict]:
    root = ET.parse(junit_path).getroot()
    failures = []
    for case in root.iter("testcase"):
        for tag in ("failure", "error"):
            node = case.find(tag)
            if node is not None:
                failures.append(
                    {
                        "test": f"{case.get('classname')}::{case.get('name')}",
                        "message": (node.get("message") or "")[:500],
                        "details": (node.text or "")[-1500:],
                    }
                )
    return failures


def rule_based(f: dict) -> dict:
    text = f["message"] + f["details"]
    for needle, category, hint in RULES:
        if needle in text:
            return {"category": category, "hint": hint}
    return {"category": "Unknown", "hint": "Needs manual triage."}


def ask_claude(failures: list[dict]) -> str | None:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key or not failures:
        return None
    prompt = (
        "You are a QA lead. For each failed UAT test below, give the likely root cause "
        "(test bug, environment, or product defect) and a next step. Be brief.\n\n" + json.dumps(failures, indent=2)
    )
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={
            "model": os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"),
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["content"][0]["text"]


def main() -> int:
    junit = Path(sys.argv[1] if len(sys.argv) > 1 else "artifacts/junit.xml")
    failures = parse_failures(junit)
    lines = ["# UAT failure analysis", "", f"Failures: **{len(failures)}**", ""]
    for f in failures:
        r = rule_based(f)
        lines += [
            f"## {f['test']}",
            f"- Category: **{r['category']}**",
            f"- Hint: {r['hint']}",
            f"- Message: `{f['message'][:200]}`",
            "",
        ]
    ai = ask_claude(failures)
    if ai:
        lines += ["## AI summary", "", ai]
    out = junit.parent / "failure_analysis.md"
    out.write_text("\n".join(lines))
    json.dump(failures, open(junit.parent / "failures.json", "w"), indent=2)
    print(f"Wrote {out} ({len(failures)} failures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
