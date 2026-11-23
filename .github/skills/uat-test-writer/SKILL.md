---
name: uat-test-writer
description: Conventions for adding a new UAT journey (feature + steps + page object + locators).
---
Checklist for a new journey:
- [ ] `tests/features/<journey>.feature` with tags
- [ ] `tests/locators/<journey>_locators.py` (data-testid selectors)
- [ ] `tests/pages/<journey>_page.py`
- [ ] `tests/steps/test_<journey>_steps.py` calling `scenarios("<journey>.feature")`
- [ ] `make test` green, then open PR to `develop`
