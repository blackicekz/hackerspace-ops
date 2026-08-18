# Claude Code development instructions

## Project development model

This repository uses an agent-neutral development process. This file is only a Claude Code
adapter; canonical product and development knowledge lives in repository documentation.

## Canonical sources

- Product behaviour and acceptance criteria: [`specs/README.md`](specs/README.md) and
  [`specs/features/`](specs/features/).
- Architecture constraints and decisions: [`specs/architecture/system.md`](specs/architecture/system.md),
  [`specs/architecture/boundaries.md`](specs/architecture/boundaries.md), and
  [`specs/architecture/adr/`](specs/architecture/adr/).
- Development policy: [`docs/development/README.md`](docs/development/README.md),
  [`definition-of-done.md`](docs/development/definition-of-done.md),
  [`contribution-norms.md`](docs/development/contribution-norms.md), and
  [`adr-process.md`](docs/development/adr-process.md).
- Development workflows: [`docs/workflows/`](docs/workflows/); for implementation tasks, follow
  [`implement-feature.md`](docs/workflows/implement-feature.md).

## Before making changes

Identify and read the relevant specification, then read the architecture constraints for the
affected boundaries and use the appropriate repository workflow. Treat neutral repository
documentation as canonical; do not infer product behaviour from this file. Do not implement
deferred functionality unless requested and allowed by the Definition of Done scope rules.

## Verification

Before declaring work complete, run the canonical verification command documented in
[`docs/development/README.md`](docs/development/README.md#canonical-verification-command):

```sh
docker compose run --rm app check
```

## Completion reporting

In the final report, state specifications changed, acceptance criteria implemented or affected,
production code changed, tests added or changed, the canonical verification result, and any
intentionally deferred work.
