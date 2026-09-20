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
  development procedures** — the concrete steps to follow for triaging and implementing an Issue.
- GitHub Issues are the **single intake** for feature requests and bug reports; the
  [issue lifecycle](issue-lifecycle.md) connects them to the procedures above.

The process is the same for every contributor — a human developer, a human using an AI tool, or a
coding agent. `AGENTS.md` and `CLAUDE.md` at the repository root are navigation adapters for
coding agents and carry no rules of their own.

## Documents in this directory

- [Definition of Done](definition-of-done.md) — when a change is complete.
- [Contribution norms](contribution-norms.md) — expectations for the shape and content of changes,
  including review and accountability for agent-authored work.
- [Issue lifecycle](issue-lifecycle.md) — states, labels, who triages, who implements, who merges
  and deploys.
- [ADR process](adr-process.md) — when a decision needs an Architecture Decision Record.

## Canonical verification command

The repository's toolchain is Docker-owned (see
[ADR 0002](../../specs/architecture/adr/0002-docker-toolchain.md)). The single canonical
verification command, which runs formatting, linting, strict type checks, architecture boundary
checks, and the test suite, is:

```sh
docker compose run --rm app check
```

This command is the single quality gate for the repository: developers, coding agents, and CI
all run it, and none of them substitute a different check list.

Other documents in `docs/` refer back to this command rather than restating what it does.

## Agent-neutral operating model

The supported development cycle is:

```text
GitHub Issue -> local branch -> implementation -> verification -> Pull Request
```

The same cycle applies to human contributors and to coding agents, including Codex and Claude.
Roles such as specification, architecture, implementation, testing, documentation, and review are
responsibilities within the contributor's current session. The contributor selects only the
responsibilities needed by the Issue; the repository does not require a fixed role pipeline or
independently running LLM agents.

The cycle ends when the Pull Request is created. Deterministic CI may report later failures, but
the repository does not wake an LLM, run an external orchestrator, or repair post-PR failures
automatically. A contributor starts a new session from the failure information or a new Issue.
The repository requires no paid orchestration service or provider API key beyond a contributor's
existing coding-agent subscription.
