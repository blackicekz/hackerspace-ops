# Contributor instructions

## Development environment

Docker is the only supported runtime and development environment. Do not require host-installed
Python, Make, pip, Poetry, or another project-specific package manager. Use these interfaces:

- `docker compose run --rm app shell` for an interactive shell.
- `docker compose run --rm app check` for every repository validation.

The scripts under `scripts/` are container entrypoints, not host tooling. Do not add a host-language
fallback. Pin tools in `Dockerfile` and run them through Compose inside the container.

## Delivery workflow

Use Spec-Driven Development in this order:

1. Write or amend the feature specification and acceptance criteria in `specs/`.
2. Add acceptance tests that express those criteria.
3. Implement the smallest change that satisfies them.
4. Run `docker compose run --rm app check`.

Preserve Clean Architecture: dependencies point inward. `domain` imports no project layer;
`application` may import `domain`; adapters may import application and domain; infrastructure may
compose all layers. External SDKs and APIs belong in adapters or infrastructure, behind application
ports. Tests are exempt from production dependency rules.

Keep changes small, readable to hackerspace residents, and free of secrets or personal data.
Read the relevant specifications before editing code, and update them whenever observable behavior
changes. Create an ADR for a significant, lasting architectural decision; do not create ADRs for
routine implementation details. Never couple domain or application code to an external API, SDK,
transport, database, Docker, or AI provider.

## Definition of Done

A task is complete only when:

1. The relevant specification reflects the implemented behavior.
2. Acceptance criteria are explicit and testable.
3. Acceptance tests cover changed observable behavior.
4. The implementation satisfies those tests.
5. Clean Architecture dependency rules remain satisfied.
6. `docker compose run --rm app check` passes.
7. Affected documentation is updated.
8. No secrets, caches, generated artifacts, or unrelated changes are included.
9. There are no known scope-critical TODOs.

Before finishing, report specifications changed, acceptance criteria implemented, production code
changed, tests added or changed, the canonical verification result, and intentionally deferred work.
Do not implement deferred functionality unless explicitly requested.
