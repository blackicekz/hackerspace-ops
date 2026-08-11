# ADR 0003: Specifications drive observable behavior

Status: accepted

Feature work starts by defining observable behavior and acceptance criteria in `specs/`. Acceptance
tests are derived from those criteria before production code changes. This keeps intent reviewable
by residents who do not need to understand every implementation detail and prevents documentation
from becoming an afterthought. The tradeoff is a small documentation cost for each behavior change.
