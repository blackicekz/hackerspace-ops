# System architecture

## Context

Hackerspace Ops turns trusted event information into coordinated publishing actions. Initially it
models event creation only. Future use cases will publish upcoming events to a GitHub Pages site and
Telegram, publish past-event media, create Instagram reels, and synchronize calendars.

The domain contains stable community concepts. Application use cases coordinate domain objects via
ports. Input and output adapters translate protocols and vendor APIs. Infrastructure is the
composition root and owns configuration. Authorization is an input-boundary concern: adapters must
authenticate callers before invoking an application command, while the command records the actor.

## Ports and adapters

Input adapters translate authenticated external input into provider-neutral application commands.
Output ports are narrow interfaces owned by the application layer; adapters implement persistence
or platform behavior. The first slice has repository and identifier-generator ports plus an
in-memory output adapter and a normalized-message input adapter.

Planned integrations are separate boundaries: website repository publishing, Telegram channel
publishing, calendar synchronization, completed-event content publishing, and Instagram media
publishing. A feature adds its port only when its use case is specified; there is no shared vendor
integration service.

## Extension mechanism

Add a use case and the smallest ports it needs in the application layer. Add protocol translation
or vendor implementations as adapters, then wire them with configuration in infrastructure. New
event sources use the same commands and domain model rather than introducing transport objects into
the core. AI capabilities follow the same rule if later specified; no AI provider is part of the
current design.

## Major decisions

Clean Architecture, specification-driven delivery, and the Docker-owned toolchain are recorded in
`adr/`. Production persistence, deployment, authentication policy, and concrete platform choices
remain deferred until their features require them.
