# When to write an ADR

An Architecture Decision Record (ADR) is created for a decision that is:

- significant,
- lasting, and
- architectural.

An ADR is not created for a routine implementation detail.

## Minimal criterion

Does this decision materially affect architecture, boundaries, dependencies, or a long-lived
runtime/toolchain strategy or engineering constraint?

- If yes, the decision is an ADR candidate.
- If the decision is a local implementation detail and easily reversible, an ADR is usually not
  needed.

## Where ADRs live

Existing ADRs are numbered sequentially in
[`specs/architecture/adr/`](../../specs/architecture/adr/). Follow the existing numbering and the
existing shape (status, then the decision and its rationale) already used by
[ADR 0001](../../specs/architecture/adr/0001-clean-architecture.md) through
[ADR 0004](../../specs/architecture/adr/0004-transport-authentication-and-application-authorization.md).

This document does not define a new ADR template or approval process beyond the existing
directory convention.
