# System architecture

## Context

Hackerspace Ops turns trusted event information into coordinated publishing actions. Initially it
models event creation only. Future use cases will publish upcoming events to a GitHub Pages site and
Telegram, publish past-event media, create Instagram reels, and synchronize calendars.

Every capability is deterministic code in the application layer with two kinds of callers
([ADR 0007](adr/0007-use-cases-as-tool-surface.md)):

```text
resident  --Telegram command-->  transport adapter --\
                                                      +--> use case --> ports --> adapters
assistant --tool call---------->  tool adapter     --/    (one authorization policy)
```

An AI assistant is a caller of the bot, never its core: it invokes the same use cases, through the
same authorization policy, on behalf of a resident. The bot is fully operable without an
assistant, and everything an assistant can do, a resident can do through some human transport.

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

The first concrete input transport is designed as a Telegram adapter. Infrastructure composes the
Telegram SDK, configuration-backed identity and permission-fact adapters, an explicitly configured
extractor, the application policies and use cases, and persistence adapters. Transport handlers
receive the fully composed `IngestConversationalEventProposal`; they do not construct authorization
policy or interpret permission configuration.

Planned integrations are separate boundaries: website repository publishing, Telegram channel
publishing, calendar synchronization, completed-event content publishing, Instagram media
publishing, and the assistant tool interface. A feature adds its port only when its use case is
specified; there is no shared vendor integration service.

## Extension mechanism

Add a use case and the smallest ports it needs in the application layer. Add protocol translation
or vendor implementations as adapters, then wire them with configuration in infrastructure. New
event sources use the same commands and domain model rather than introducing transport objects into
the core.

A use case is also a tool. It has a typed command, a typed result union, and a description an
assistant can act on; its specification states its tool exposure (see
[`specs/README.md`](../README.md)). Once the assistant tool interface is specified, use cases are
registered in an application-owned capability catalogue that tool adapters read; adding a
capability means adding a use case and its catalogue entry, not a handler in a particular
transport. An LLM may appear inside the bot only as a replaceable adapter behind a narrow
application-owned port when a specification calls for it; natural-language understanding is
otherwise the assistant's job outside the bot (ADR 0007).

Changing Telegram update delivery from polling to webhook, or adding another transport, replaces
adapter/infrastructure wiring only. Both continue to emit `ConversationalInput` and consume
application result types; domain and application behavior do not change.

## Major decisions

Clean Architecture, specification-driven delivery, the Docker-owned toolchain, the separation of
transport authentication from application authorization, the initial Telegram runtime choice, the
self-hosted CD deployment, and the position of an AI assistant as a caller of the use-case tool
surface are recorded in `adr/`. Production persistence and concrete identity storage remain
deferred until their features require them.
