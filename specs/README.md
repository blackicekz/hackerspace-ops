# Specifications

Specifications are executable design inputs, not retrospective documentation. For each change,
write observable acceptance criteria first, encode them in `tests/acceptance`, and only then change
implementation. Architecture decisions with long-lived consequences belong in
`architecture/adr/`.

Every feature specification should state its purpose, terminology, inputs, behavior, invariants,
concrete acceptance criteria, relevant failures, and — for any feature that adds or changes a use
case — its **tool exposure**: the tool name, when a caller (human transport or AI assistant)
should invoke it, its side effects, whether it is idempotent, and every result variant. Tests
should cite or clearly correspond to the acceptance criteria. A behavior change is incomplete
until its specification and tests agree.

Feature work normally starts from a GitHub Issue; the mapping from an Issue to a specification is
in [`docs/workflows/triage-issue.md`](../docs/workflows/triage-issue.md).

## Language

Specifications, architecture documents, code, tests, and development documentation are written in
English. Issue templates and the bot's replies to residents are in the residents' language
(currently Russian). Triage translates an Issue's wording into the specification's English terms
and keeps the Issue as the record of the original request.

## Glossary

Terms below are used with exactly these meanings across `specs/`, `docs/`, and code.

- **Resident**: a member of the hackerspace community, identified inside the bot by a
  `ResidentIdentity`. Residents are the bot's users and the actors recorded on domain objects.
- **Operator**: the person who runs the deployment and manages its configuration and secrets.
- **Bot** (Hackerspace Ops): this system — deterministic capabilities implemented as application
  use cases, reachable through transports.
- **Capability / use case**: one operation the bot performs, defined by a typed command and a
  typed result union in `src/application`. Every capability is also a tool.
- **Tool**: a capability as seen by a caller through a transport: a name, a description, a command
  schema, and result variants. The capability catalogue lists them.
- **Transport**: an adapter that authenticates external input, translates it into provider-neutral
  application values, invokes a use case, and presents its result. Telegram commands and the
  assistant tool interface are both transports.
- **Assistant** (AI assistant): an LLM-based agent that helps residents with hackerspace
  operations by calling the bot's tools on their behalf. It is a caller of the bot, not part of
  it ([ADR 0007](architecture/adr/0007-use-cases-as-tool-surface.md)).
- **Coding agent**: an AI agent that develops this repository — writes specifications, tests, and
  code under the same process as a human contributor
  ([`docs/development/`](../docs/development/README.md)). Unrelated to the assistant above.
- **Contributor**: a human developer or a coding agent making a change to this repository.
