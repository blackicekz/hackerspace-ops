# Hackerspace Ops

Hackerspace Ops is an open-source operations bot for community hackerspaces. Its planned
capabilities are publishing event announcements and past-event articles/photos to a GitHub Pages
site, producing Instagram reels, managing calendar events, and posting upcoming events to Telegram.
Events may originate in the hackerspace Telegram chat or from direct instructions by authorized
residents.

Every capability is deterministic code inside the bot, and each one has two kinds of callers:
residents, through human transports such as Telegram commands, and an AI assistant, which calls the
same capabilities as tools on a resident's behalf. The assistant helps with day-to-day operations;
it is a caller of the bot, not its core, and the bot works without it. See
[ADR 0007](specs/architecture/adr/0007-use-cases-as-tool-surface.md).

The first intentionally small vertical slice accepts an already-authenticated event instruction,
validates it in the domain, and stores it through an application port. It does **not** connect to an
external service yet.

## Requesting features and reporting bugs

Feature requests and bug reports go to this repository's GitHub Issues, using the issue templates.
Issues are the single intake: describe the problem and the observable result you expect; you do
not need to propose an implementation. Do not put tokens, passwords, or personal data into an
Issue.

An Issue is triaged into a specification with testable acceptance criteria, implemented by a
contributor — a human developer with or without AI help, or a coding agent running in a loop —
reviewed by a human, merged, and deployed. The states, labels, and who does what are in
[`docs/development/issue-lifecycle.md`](docs/development/issue-lifecycle.md).

## Development

Docker is the sole host prerequisite. Python, Make, pip, and project package managers are neither
required nor used on the host.

```sh
docker compose build
docker compose run --rm app check
docker compose run --rm app test
docker compose run --rm app shell
```

The `check` command is canonical: it runs formatting verification, linting, strict type checks,
architecture boundary checks, and all test suites inside Docker. Compose mounts the checkout for a
fast development loop. Run `docker compose build --no-cache` when validating toolchain changes.

The development process is agent-neutral: the same specifications, Definition of Done, and
canonical check apply to human developers and to coding agents. Humans start with
[`CONTRIBUTING.md`](CONTRIBUTING.md); coding agents start with [`AGENTS.md`](AGENTS.md) (or the
[`CLAUDE.md`](CLAUDE.md) adapter). Both lead to the same canonical documents under `docs/` and
`specs/`.

## Running the bot

Copy `.env.example` to `.env`, fill in real values, and never commit `.env`:

```sh
docker compose up -d bot
```

The current bot is a minimal deployment bootstrap that only answers `/start` and `/help` in one
configured test group; see [`specs/features/bot-bootstrap/`](specs/features/bot-bootstrap/README.md).

## Architecture

Dependencies point inward:

```text
infrastructure -> adapters -> application -> domain
```

Application ports describe required external behavior. As capabilities are specified, independently
replaceable adapters will implement ports for platforms such as Telegram, GitHub, calendars, and
Instagram. The current in-memory adapter implements event storage for the first slice. See
`specs/architecture/` for the complete rules.
Infrastructure wires concrete adapters, configuration, and the deployable process together.

Callers sit on the outside of that picture: Telegram commands and the assistant tool interface are
both transports that authenticate a resident, invoke a use case, and present its result. Use cases
carry typed commands and typed result unions so that the same capability serves both. Terms such as
resident, transport, tool, assistant, and coding agent are defined in the
[glossary](specs/README.md#glossary).

## Adding a capability

1. Start from a `ready` Issue (see the [issue lifecycle](docs/development/issue-lifecycle.md)).
2. Add a feature directory and acceptance criteria under `specs/features/`, including the
   capability's tool exposure.
3. Add an acceptance test before production code.
4. Put business concepts in `src/domain` and orchestration plus ports in `src/application`.
5. Implement external details in `src/adapters`; wire deployable configuration in
   `src/infrastructure`.
6. Run `docker compose run --rm app check` and update architecture decisions when introducing a
   lasting tradeoff.

The full procedure is [`docs/workflows/implement-feature.md`](docs/workflows/implement-feature.md).
