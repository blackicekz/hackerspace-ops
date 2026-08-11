# Hackerspace Ops

Hackerspace Ops is an open-source, modular operations agent for community hackerspaces. Its planned
capabilities are publishing event announcements and past-event articles/photos to a GitHub Pages
site, producing Instagram reels, managing calendar events, and posting upcoming events to Telegram.
Events may originate in the hackerspace Telegram chat or from direct instructions by authorized bot
users.

The first intentionally small vertical slice accepts an already-authenticated event instruction,
validates it in the domain, and stores it through an application port. It does **not** connect to an
external service yet.

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

## Adding a capability

1. Add a feature directory and acceptance criteria under `specs/features/`.
2. Add an acceptance test before production code.
3. Put business concepts in `src/domain` and orchestration plus ports in `src/application`.
4. Implement external details in `src/adapters`; wire deployable configuration in
   `src/infrastructure`.
5. Run `docker compose run --rm app check` and update architecture decisions when introducing a
   lasting tradeoff.
