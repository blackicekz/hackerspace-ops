# Telegram input and bot runtime

## Purpose

Provide one coherent deployable input slice: receive a deliberately narrow Telegram event command,
translate it into `ConversationalInput`, invoke the existing
`IngestConversationalEventProposal`, and present the result in Telegram. Telegram remains an adapter
concern; the application and domain are unchanged and callable by other transports.

The initial executable runtime uses an explicit command rather than pretending to understand free
form conversation:

```text
/event <RFC3339 timestamp with explicit UTC offset> | <title>
```

Example:

```text
/event 2026-09-04T19:00:00+05:00 | Open night
```

## Terminology

- **Transport authentication**: the bot authenticates to Telegram using its token over HTTPS and
  trusts sender/update metadata delivered under the Telegram Bot API contract. This does not
  establish hackerspace identity or permission.
- **Telegram sender identity**: the `User.id` carried by an authenticated Telegram update.
- **Eligible message**: a new human-authored `/event` text command in a private, group, or
  supergroup chat, with a sender.
- **Command extractor**: a deterministic adapter implementing the existing
  `EventProposalExtractor` contract for the explicit syntax above.
- **Presentation**: Telegram-specific reply wording for an application result.

## Inputs

The Telegram adapter accepts SDK update objects but allows none of them across the application
boundary. For each eligible command it supplies the command payload, sender identity, and provenance
as provider-neutral application values.

In a group, Telegram's `/event@bot_username` form is equivalent to `/event`. A reply containing the
command is processed as an independent command; replied-to content and prior messages are not read.

## SDK and dependency decision

Use `python-telegram-bot==22.8`, installed later without webhook extras. Pin the direct dependency to
the exact reviewed version in the Docker build input and upgrade it deliberately through canonical
verification.

The library is maintained and production/stable, fully asynchronous and typed, supports Python
3.13, provides polling and webhook lifecycles, and requires only `httpx` by default. Aiogram 3.30.0
is also maintained, typed, and capable, but its broader router, middleware, dependency-injection,
FSM, and Pydantic-oriented framework surface is unnecessary here. PyTelegramBotAPI supports both
synchronous and asynchronous styles but gives no compensating advantage for this typed async
runtime. Research and primary sources are recorded in ADR 0005.

No SDK or dependency is installed during this design stage.

## Runtime model

Use long polling with `allowed_updates=["message"]`. Polling needs outbound HTTPS only and works in
local Docker without a public endpoint, certificate, reverse proxy, or webhook secret. At startup,
remove any existing webhook without dropping pending updates because Telegram polling and webhooks
are mutually exclusive. Exactly one running process may poll a bot token.

A later webhook runner can deliver the same SDK message objects to the same Telegram handler. Only
infrastructure startup and webhook authentication change; translation, application contracts,
authorization, and domain behavior do not.

## Supported and ignored Telegram input

Process only new `message` updates satisfying every condition:

- chat type is private, group, or supergroup;
- sender exists and `sender.is_bot` is false;
- content is text;
- text is an `/event` command addressed to this bot.

Ignore without invoking application ingestion or replying:

- ordinary text and commands other than `/event`;
- edited messages, channel posts, and edited channel posts;
- messages authored by bots or lacking a sender;
- non-text content including photos, documents, voice, video, and stickers;
- service, callback-query, inline-query, reaction, membership, and business updates;
- chat types outside private, group, and supergroup.

Telegram group privacy mode remains enabled. This slice needs explicit commands, not blanket access
to hackerspace conversation. Conversation history and multi-message assembly remain deferred.

## Identity mapping

The exact translation is:

```text
Telegram message.from_user.id
  -> ExternalIdentity(
       issuer="telegram",
       subject=str(message.from_user.id),
     )
```

The decimal subject is opaque outside Telegram/configuration adapters. It is never a
`ResidentIdentity`. A configuration-backed `ResidentIdentityResolver` maps the complete
issuer/subject pair to a resident; an absent mapping yields the existing `UnidentifiedSender`.
Telegram handlers do not read this mapping.

## Provenance

Construct the exact source reference:

```text
telegram:chat:<decimal chat_id>:message:<decimal message_id>
```

Telegram message IDs are scoped to a chat, so the pair identifies the source message. The reference
contains no bot token, message text, username, or resident identity. Application/domain treat it as
opaque and preserve it unchanged; they never parse it.

## Explicit command extractor

Retain the deterministic `/event` syntax as the smallest honest bootstrap option. The extractor:

- implements the existing `EventProposalExtractor` port;
- accepts one RFC3339 timestamp with an explicit UTC offset, one `|`, and a non-blank title;
- returns application-owned `Ready(EventProposal)` for valid input;
- returns `Incomplete` when timestamp or title is absent;
- returns `Ambiguous` when the delimiter structure or timestamp has multiple/unsafe
  interpretations;
- does not parse natural-language dates or general prose.

This syntax exists only to make the first Telegram runtime executable without an LLM. A future
deterministic or LLM-backed extractor replaces this adapter without changing Telegram translation,
application policy, or domain code. The extractor is not implemented during this design stage.

## Behavior and result presentation

1. The handler filters eligible messages.
2. It extracts the command payload and constructs `ConversationalInput` with the external identity
   and source reference defined above.
3. It invokes the injected, fully composed `IngestConversationalEventProposal` exactly once.
4. It maps the application result to presentation without changing result semantics.

| Application result | Telegram behavior |
| --- | --- |
| `UnidentifiedSender` | Reply: `Your Telegram account is not linked to a hackerspace resident.` |
| `UnauthorizedResident` | Reply: `You are not allowed to propose hackerspace events.` |
| `IrrelevantMessage` | No reply. |
| `IncompleteProposal(fields)` | Reply: `Event proposal is incomplete: <sorted comma-separated fields>.` |
| `AmbiguousProposal(fields)` | Reply: `Event proposal is ambiguous: <sorted comma-separated fields>.` |
| `EventCreated(event_id)` | Reply: `Event created: <event_id>.` |

Reply wording and formatting belong to the Telegram adapter. Semantic failure results create no
event because the existing application flow reaches `CreateEvent` only for `Ready`.

## Responsibilities

### Telegram adapter

- Import SDK types and register the eligible command handler.
- Filter updates and extract command text, sender ID, chat ID, and message ID.
- Convert SDK-specific values to provider-neutral application values.
- Invoke the injected ingestion use case and render its result.
- Contain malformed updates, Telegram exceptions, and reply failures.

It does not resolve residents, read identity/permission configuration, decide authorization,
construct application policy, create events, or parse general natural language.

### Infrastructure and composition root

An infrastructure bootstrap module loads and validates configuration, then wires:

```text
configuration-backed ResidentIdentityResolver
configuration-backed EventProposalPermissionFacts
  -> EventProposalAuthorization
explicit-command EventProposalExtractor
identifier generator + EventRepository
  -> CreateEvent
  -> IngestConversationalEventProposal
  -> Telegram adapter
  -> python-telegram-bot Application.run_polling()
```

The Telegram adapter receives the fully composed use case. `src/__main__.py` remains a thin process
entrypoint delegating to the infrastructure bootstrap. Initial event storage may remain in-memory;
therefore restart persistence is explicitly not promised by this feature.

## Configuration

Read and validate these environment variables at startup:

| Variable | Required | Meaning |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Yes | Secret token issued by BotFather. |
| `HACKERSPACE_TELEGRAM_IDENTITIES_JSON` | Yes | JSON object mapping Telegram subject strings to resident ID strings. |
| `HACKERSPACE_EVENT_PROPOSERS_JSON` | Yes | JSON array of resident IDs with the event-proposal permission fact. |
| `HACKERSPACE_LOG_LEVEL` | No | Standard log level, default `INFO`. |

The identity resolver implements mapping only. The permission adapter reports membership in the
configured proposer list only. `EventProposalAuthorization` remains the sole owner of “may this
resident propose an event?” Replacing configuration with persistence later does not change these
application contracts.

Tokens, mappings, and permissions come from the operator environment or an explicitly supplied
uncommitted env file. A future `.env.example` is useful only with variable names and synthetic
placeholders; `.env` remains ignored. Missing/invalid configuration fails startup before Telegram
contact, names the invalid variable, and never prints its value.

## Docker runtime interface

The intended host interface is:

```text
docker compose up bot
docker compose run --rm app check
```

The future `bot` service uses the runtime image, runs `python -m src`, receives environment variables
externally, exposes no inbound port, and has no host source bind mount. The existing `app` service
retains development/check behavior. No Docker or Compose file changes occur in this design stage.

Compose forwards stop signals. The process relies on the SDK polling lifecycle so SIGINT/SIGTERM
stops fetching, completes SDK shutdown, closes the client, and exits within the Compose stop grace
period without starting another application invocation.

## Operational failures

- **Telegram network/API interruption:** rely on SDK polling reconnection for transient failures and
  log a sanitized warning. Persistent startup/authentication errors terminate the process.
- **Malformed eligible-looking update:** log a sanitized warning, do not call the application, and
  continue polling. Unsupported updates are silently ignored.
- **Application dependency exception:** treat it as operational, not semantic. Log without content,
  reply `The request could not be processed.` when possible, and remain available for later updates.
- **Reply failure:** log a sanitized warning and never re-invoke application ingestion, avoiding
  duplicate event creation.
- **Shutdown:** use SDK-native graceful polling shutdown; no additional worker/retry system.

Durable retries, deduplication, metrics, tracing, and an observability platform are deferred.

## Logging and privacy

Use standard-library logging. Logs may include application result class, Telegram update ID, chat
type, exception class, and a one-way digest of the source reference. Never log bot tokens,
configuration values, raw user/chat IDs, resident IDs, complete source references, usernames,
display names, or message/command text. Stack traces for operational failures must not attach
request or configuration values.

## Invariants and architecture constraints

- Telegram SDK imports/objects stop in adapter/infrastructure code.
- Application/domain receive only existing provider-neutral values and primitives.
- Telegram user identity, resident identity, and permission remain distinct.
- Configuration adapters provide mappings and facts; they never authorize.
- Telegram reply text is absent from application/domain.
- Handlers receive a fully composed use case and contain no composition root.
- A second transport supplies the same `ConversationalInput` and consumes the same application
  results with its own authentication, provenance, filtering, and presentation. Application/domain
  code remains unchanged.

## Acceptance criteria

1. Given a new human-authored `/event` text command in a private, group, or supergroup chat, the
   adapter invokes ingestion exactly once with the payload, `ExternalIdentity("telegram",
   str(sender_id))`, and `telegram:chat:<chat_id>:message:<message_id>`.
2. `/event@the_bot` in a group is handled equivalently, while ordinary text, other commands, edited
   messages, channel posts, bot-authored or senderless messages, unsupported chats, and non-text
   content neither invoke ingestion nor receive a reply.
3. An unmapped Telegram identity receives the unidentified reply and creates no event; a mapped
   resident identity—not the Telegram subject—is supplied as the event actor when creation succeeds.
4. A mapped resident without the permission fact receives the unauthorized reply; extraction is not
   invoked and no event is created.
5. A valid explicit payload produces `Ready` through the configured extractor; for a permitted
   resident it creates one event, replies `Event created: <event_id>.`, and preserves the exact
   source reference on the event.
6. A command missing timestamp or title produces `IncompleteProposal`, replies with stable sorted
   missing field names, and creates no event.
7. A structurally or temporally ambiguous command produces `AmbiguousProposal`, replies with stable
   sorted ambiguous field names, and creates no event.
8. `IrrelevantMessage` produces no Telegram reply and no event.
9. An application exception sends the generic operational-failure reply when possible, does not
   present semantic success, and does not prevent a later eligible message from being processed.
10. A reply-send failure never causes ingestion to run a second time.
11. Missing or invalid required environment configuration terminates startup before polling and
    reports variable names without values; the token and personal mappings are never committed or
    logged.
12. SIGTERM stops polling and the process exits cleanly without beginning another ingestion call.

## Design answers

### How can a second transport be added later without modifying application/domain code?

Its adapter authenticates that protocol, constructs existing `ConversationalInput`, invokes the same
composed use case, and presents existing results. A distinct `ExternalIdentity.issuer` selects its
mapping; shared authorization remains application-owned.

### Where does Telegram-specific code stop?

At the call to `IngestConversationalEventProposal.execute`. Updates, SDK IDs/types, filters,
exceptions, polling, and replies remain in adapter/infrastructure code.

### How is authorization prevented from leaking into Telegram handlers or configuration?

Infrastructure injects `EventProposalAuthorization`. Telegram-backed configuration adapters expose
mapping and permission facts through existing ports only. Handlers never inspect either
configuration and cannot decide permission.

### How can the runtime function while natural-language extraction is deferred?

Use the narrow explicit-command extractor implementing `EventProposalExtractor`. It makes the bot
honestly executable without an LLM. Future deterministic or LLM extractors replace that adapter
without changing Telegram translation, application policy, or domain code.

## Scope exclusions

This stage adds no production code, tests, dependencies, SDK installation, token use, running bot,
Docker changes, extractor implementation, natural-language/LLM integration, conversation history,
multi-message assembly, database, RBAC, publishing, calendar, Instagram, or deployment
infrastructure.
