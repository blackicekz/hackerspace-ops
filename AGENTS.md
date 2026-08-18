# Development agent instructions

This repository uses an agent-neutral development process. This file is a navigation and
interaction adapter for coding agents, not a source of product behaviour or development policy.

## Sources of truth

- Product behaviour and acceptance criteria: [`specs/README.md`](specs/README.md) and
  [`specs/features/`](specs/features/).
- Architecture constraints and decisions: [`specs/architecture/system.md`](specs/architecture/system.md),
  [`specs/architecture/boundaries.md`](specs/architecture/boundaries.md), and
  [`specs/architecture/adr/`](specs/architecture/adr/).
- Development policy and Definition of Done: [`docs/development/`](docs/development/README.md).
- Reusable development workflows: [`docs/workflows/`](docs/workflows/implement-feature.md).

## Before making changes

Identify and read the relevant specification, then read the architecture constraints for the
affected boundaries. Follow the appropriate repository workflow. Treat specifications and neutral
documentation as canonical; never infer product behaviour from this file.

## Verification

Before completing work, run the canonical verification command documented in
[`docs/development/README.md`](docs/development/README.md#canonical-verification-command):

```sh
docker compose run --rm app check
```

## Completion reporting

Before finishing, report specifications changed, acceptance criteria implemented or affected,
production code changed, tests added or changed, the canonical verification result, and any
intentionally deferred work.
