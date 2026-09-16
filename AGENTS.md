# Development agent instructions

This repository uses an agent-neutral development process. This file is a navigation and
interaction adapter for coding agents, not a source of product behaviour or development policy.
Every rule referenced here lives in a canonical document; if this file and a canonical document
disagree, the canonical document wins.

## What this project is

Hackerspace Ops is an operations bot for a community hackerspace. Its capabilities are
deterministic use cases in `src/application`, callable by residents through transports (Telegram)
and by an AI assistant through a tool interface, under one authorization policy. The assistant is
a caller of the bot, not part of it. Do not confuse that assistant (a *user* of the bot) with
yourself (a *developer* of the bot). See
[ADR 0007](specs/architecture/adr/0007-use-cases-as-tool-surface.md) and the
[glossary](specs/README.md#glossary).

## Sources of truth

- Product behaviour and acceptance criteria: [`specs/README.md`](specs/README.md) and
  [`specs/features/`](specs/features/).
- Architecture constraints and decisions: [`specs/architecture/system.md`](specs/architecture/system.md),
  [`specs/architecture/boundaries.md`](specs/architecture/boundaries.md), and
  [`specs/architecture/adr/`](specs/architecture/adr/).
- Development policy and Definition of Done: [`docs/development/`](docs/development/README.md).
- Issue states, labels, and boundaries for agents:
  [`docs/development/issue-lifecycle.md`](docs/development/issue-lifecycle.md).
- Reusable development workflows: [`docs/workflows/`](docs/workflows/implement-feature.md).

## Where work comes from

Work starts from a GitHub Issue labelled `ready` with no assignee. Claim it, branch as
`issue-<number>-<short-slug>`, and follow
[`docs/workflows/implement-feature.md`](docs/workflows/implement-feature.md). If you are asked to
triage rather than implement, follow [`docs/workflows/triage-issue.md`](docs/workflows/triage-issue.md)
and post the result as an Issue comment; only a maintainer applies `ready`.

## Before making changes

Identify and read the relevant specification, then read the architecture constraints for the
affected boundaries. Follow the appropriate repository workflow. Treat specifications and neutral
documentation as canonical; never infer product behaviour from this file. Do not implement
deferred functionality unless the Issue asks for it and the Definition of Done scope rules allow
it.

## Verification

Before completing work, run the canonical verification command documented in
[`docs/development/README.md`](docs/development/README.md#canonical-verification-command):

```sh
docker compose run --rm app check
```

## Completion reporting

Open a Pull Request from [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)
with `Closes #<number>`. Its sections are the completion report: specifications changed,
acceptance criteria implemented or affected, production code changed, tests added or changed, the
canonical verification result, and any intentionally deferred work. State in the description that
the change was authored by a coding agent. Move the Issue to `in-review` and stop.

## What an agent does not do

Apply the `ready` label, merge, push to `master`, close Issues by hand, run the `deploy` workflow,
or read or modify the operator's `.env`. If an Issue cannot be satisfied within its specification
and scope, comment what is missing, apply `blocked`, and stop.
