# Definition of Done

This document defines when a change to this repository is complete. It applies uniformly to any
contributor — a human developer or a coding agent — and to any change, regardless of which tool
produced it.

A change is complete only when all of the following hold:

1. The relevant specification in [`specs/`](../../specs/README.md) reflects the implemented
   behaviour.
2. Acceptance criteria are explicit and testable.
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

How a specific development harness communicates the completion of a change to its user or
operator — what it reports, in what format, at what point — is not a Definition-of-Done rule. That
is harness-specific and is documented where that harness's instructions live (currently
`AGENTS.md`).
