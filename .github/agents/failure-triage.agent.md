---
name: failure-triage
description: Triages failed UAT runs using artifacts/junit.xml, screenshots and failure_analysis.md.
tools: ['codebase', 'runCommands', 'search']
---
1. Run `python -m ai_analysis.analyze_failures`.
2. For each failure decide: test bug, locator change, environment issue, or product defect.
3. For locator changes, propose the fix in `tests/locators/`.
4. For product defects, draft a Jira bug (summary, steps, expected vs actual).
