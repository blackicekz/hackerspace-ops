# System architecture

## Context

Hackerspace Ops turns trusted event information into coordinated publishing actions. Initially it
models event creation only. Future use cases will publish upcoming events to a GitHub Pages site and
Telegram, publish past-event media, create Instagram reels, and synchronize calendars.

The domain contains stable community concepts. Application use cases coordinate domain objects via
ports. Input and output adapters translate protocols and vendor APIs. Infrastructure is the
composition root and owns configuration. Transport adapters authenticate external messages and
translate transport identities into provider-neutral identity claims. Application use cases own
operation-specific authorization decisions so the same policy applies to every transport. When a
decision needs configured facts, an application-owned port supplies only those facts; its adapter
does not own or interpret authorization policy.

## Ports and adapters

Input adapters translate authenticated external input into provider-neutral application commands.
Output ports are narrow interfaces owned by the application layer; adapters implement persistence
or platform behavior. The first slice has repository and identifier-generator ports plus an
in-memory output adapter and a normalized-message input adapter.

Conversational input is not itself an event-creation command. The conversational-ingestion use case
resolves an external identity to a resident, authorizes that resident, and uses an extraction port
to classify or structure the message. Only a complete, unambiguous proposal reaches the existing
event-creation use case. Identity mappings, permission facts, and extraction implementations are
replaceable adapters behind application-owned ports. The authorization policy itself remains in the
application layer.

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

Clean Architecture, specification-driven delivery, the Docker-owned toolchain, and the separation
of transport authentication from application authorization are recorded in `adr/`. Production
persistence, deployment, concrete identity storage, and platform choices remain deferred until
their features require them.
