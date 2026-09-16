# Definition of Done

This document defines when a change to this repository is complete. It applies uniformly to any
contributor — a human developer or a coding agent — and to any change, regardless of which tool
produced it.

A change is complete only when all of the following hold:

1. The relevant specification in [`specs/`](../../specs/README.md) reflects the implemented
   behaviour.
2. Acceptance criteria are explicit and testable, and a use case that was added or changed has
   its tool exposure stated in the specification
   ([ADR 0007](../../specs/architecture/adr/0007-use-cases-as-tool-surface.md)).
3. Acceptance tests cover the changed observable behaviour.
4. The implementation satisfies those tests.
5. [Clean Architecture dependency rules](../../specs/architecture/boundaries.md) remain satisfied.
6. The [canonical repository verification command](README.md#canonical-verification-command)
   passes.
7. Affected documentation is updated.
8. No secrets, caches, generated artifacts, or unrelated changes are included.
9. There are no known scope-critical TODOs.

## Scope discipline

Deferred functionality — behaviour intentionally left unimplemented for a later change — is not
implemented as part of an unrelated change unless it was explicitly requested. Scope creep beyond
what a specification calls for is not "done," even if the added code is correct.

## Out of scope for this document

How a change is reported is not a Definition-of-Done rule. The report's format is the Pull
Request template (`.github/PULL_REQUEST_TEMPLATE.md`), the same for every contributor; how a
specific development harness surfaces it to its own user is harness-specific and documented where
that harness's instructions live (currently `AGENTS.md` and `CLAUDE.md`).
