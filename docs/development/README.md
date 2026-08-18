# Development documentation

This directory documents engineering and development policy: rules about how work in this
repository is done, independent of what the product does or which tool performs the work.

## Where things live

- [`specs/`](../../specs/README.md) is the source of truth for **required product behaviour** —
  what the system must do, expressed as specifications and acceptance criteria.
- [`specs/architecture/`](../../specs/architecture/system.md) is the source of truth for
  **architecture constraints and decisions** — Clean Architecture boundaries, dependency rules,
  and Architecture Decision Records (ADRs).
- `docs/development/` (this directory) is the source of truth for **engineering/development
  policy** — what makes a change complete, contribution norms, and when a decision needs an ADR.
- [`docs/workflows/`](../workflows/implement-feature.md) is the source of truth for **reusable
  development procedures** — the concrete steps to follow for a recurring kind of task.

## Documents in this directory

- [Definition of Done](definition-of-done.md) — when a change is complete.
- [Contribution norms](contribution-norms.md) — expectations for the shape and content of changes.
- [ADR process](adr-process.md) — when a decision needs an Architecture Decision Record.

## Canonical verification command

The repository's toolchain is Docker-owned (see
[ADR 0002](../../specs/architecture/adr/0002-docker-toolchain.md)). The single canonical
verification command, which runs formatting, linting, strict type checks, architecture boundary
checks, and the test suite, is:

```sh
docker compose run --rm app check
```

Other documents in `docs/` refer back to this command rather than restating what it does.
