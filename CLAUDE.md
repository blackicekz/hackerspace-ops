# Claude Code development instructions

## Project development model

This repository uses an agent-neutral development process. This file is only a Claude Code
adapter; canonical product and development knowledge lives in repository documentation. The
general agent adapter is [`AGENTS.md`](AGENTS.md); everything there applies here.

Hackerspace Ops is an operations bot whose capabilities are deterministic use cases callable by
residents (Telegram) and by an AI assistant (tool interface) under one authorization policy. That
assistant is a user of the bot; you are a developer of it. See
[ADR 0007](specs/architecture/adr/0007-use-cases-as-tool-surface.md).

## Canonical sources

- Product behaviour and acceptance criteria: [`specs/README.md`](specs/README.md) and
  [`specs/features/`](specs/features/).
- Architecture constraints and decisions: [`specs/architecture/system.md`](specs/architecture/system.md),
  [`specs/architecture/boundaries.md`](specs/architecture/boundaries.md), and
  [`specs/architecture/adr/`](specs/architecture/adr/).
- Development policy: [`docs/development/README.md`](docs/development/README.md),
  [`definition-of-done.md`](docs/development/definition-of-done.md),
  [`contribution-norms.md`](docs/development/contribution-norms.md),
  [`issue-lifecycle.md`](docs/development/issue-lifecycle.md), and
  [`adr-process.md`](docs/development/adr-process.md).
- Development workflows: [`docs/workflows/`](docs/workflows/); for implementation tasks, follow
  [`implement-feature.md`](docs/workflows/implement-feature.md); for triage,
  [`triage-issue.md`](docs/workflows/triage-issue.md).

## Where work comes from

A GitHub Issue labelled `ready` with no assignee. Claim it, branch as
`issue-<number>-<short-slug>`, and follow the implement-feature workflow. Do not apply `ready`,
merge, push to `master`, run `deploy`, or touch `.env`.

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

Open a Pull Request from [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)
with `Closes #<number>`; its sections are the completion report (specifications changed,
acceptance criteria implemented or affected, production code changed, tests added or changed, the
canonical verification result, intentionally deferred work). State that the change was authored
by a coding agent, move the Issue to `in-review`, and stop.
