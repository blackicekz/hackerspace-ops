# Conversational event proposal ingestion

## Purpose

Interpret one authenticated, provider-neutral conversational input as a possible event proposal and
create an event only when the sender resolves to an authorized resident and the proposal is complete
and unambiguous. Telegram is the first planned transport, but this behavior contains no Telegram
types or policy.

This is a separate feature from `event-ingestion`: conversational input has identity, authorization,
classification, and incomplete-information outcomes. The existing event-ingestion feature remains
the lower-level behavior for creating a validated event.

## Terminology

- **Transport authentication**: adapter-specific verification that an external message and sender
  claim can be trusted.
- **External identity**: a provider-neutral claim containing an issuer and opaque subject supplied
  by an authenticated adapter; it is not a resident identity.
- **Resident identity**: the hackerspace identifier used by application policy and recorded as the
  event actor.
- **Conversational input**: authenticated text, external identity claim if available, and an opaque
  source reference. It contains no transport SDK object.
- **Event proposal**: application-level structured candidate data, currently a title and
  timezone-aware start time. It is not a domain entity and is not persisted by this feature.
- **Ready proposal**: a proposal whose required values are present and unambiguous.
- **Source reference**: a non-secret, opaque string created by the input adapter that can trace the
  source message without retaining a vendor object.

## Inputs

The proposed `IngestConversationalEventProposal` use case receives a `ConversationalInput` with:

- message text;
- an optional `ExternalIdentity(issuer, subject)` claim;
- a non-blank `source_reference`.

The issuer and subject are opaque strings, not Telegram identity types. A Telegram adapter will
authenticate an update, extract text, translate its sender into this value, and construct a stable
source reference before calling the application. An input whose sender cannot be claimed carries no
external identity. Transport exceptions and malformed updates are handled by that adapter and never
enter the application.

## End-to-end conceptual flow

```text
Telegram update (future)
  -> Telegram adapter authenticates update and translates SDK values
  -> ConversationalInput(external identity claim, text, source reference)
  -> IngestConversationalEventProposal
  -> ResidentIdentityResolver
  -> EventProposalAuthorization (application policy)
       -> EventProposalPermissionFacts (port)
  -> EventProposalExtractor
  -> irrelevant | incomplete | ambiguous | ready
  -> ready only: CreateEvent(CreateEventCommand)
  -> Event -> EventRepository
```

Authorization precedes extraction. This avoids spending extraction capacity on unauthorized input
and ensures no extraction implementation becomes an authorization gate.

## Responsibilities

| Concern | Owner | Responsibility |
| --- | --- | --- |
| Telegram transport handling | Telegram input adapter (future) | Verify and translate updates; contain SDK objects and exceptions. |
| External identity | Input adapter | Emit an authenticated provider-neutral issuer/subject claim, or no claim. |
| Resident identity resolution | Application port; adapter implementation | Map an external claim to a resident identity without treating transport IDs as resident IDs. |
| Permission facts | Application port; adapter implementation | Report configured event-proposal permission facts without deciding application policy. |
| Authorization | Application policy | Decide whether the resolved resident may propose an event, identically for every transport. |
| Event information extraction | Application port; adapter implementation | Classify text and produce irrelevant, incomplete, ambiguous, or ready structured data. |
| Incomplete/ambiguous handling | Application use case | Return the explicit outcome and do not create an event or invent values. |
| Event creation | Existing `CreateEvent` use case | Validate and store an event only from a ready, authorized proposal. |
| Provenance | Input adapter, application flow, existing domain field | Create, preserve, and store the opaque source reference without vendor objects. |

## Proposed application ports

These contracts are owned by the application package and are not implemented in this stage:

### `ResidentIdentityResolver`

- **Called by:** `IngestConversationalEventProposal`.
- **Implemented by:** an adapter backed initially by configuration or an in-memory test double;
  production identity persistence is deferred.
- **Contract:** resolve `ExternalIdentity` to `ResidentIdentity | None`.
- **Why needed now:** transport identity and resident identity are explicitly different, and mapping
  must be shared rather than duplicated by each conversational adapter.

### `EventProposalPermissionFacts`

- **Called by:** the application-layer `EventProposalAuthorization` policy after identity
  resolution.
- **Implemented by:** an adapter backed by configuration or persistence, plus test doubles.
- **Contract:** answer `has_event_proposal_permission(resident_identity) -> bool` as a configured
  fact; it does not decide whether the use case proceeds.
- **Why needed now:** authorization depends on configured resident permissions, but those facts must
  be replaceable without moving hackerspace policy into an adapter. It is deliberately narrower
  than a generic RBAC or authorization service.

`EventProposalAuthorization` is an application-layer policy, not a port. It owns the decision “may
this resident propose an event?” by interpreting the permission fact for this operation. The
ingestion use case calls this policy and proceeds only when it permits the action. Adapters cannot
authorize the operation.

### `EventProposalExtractor`

- **Called by:** `IngestConversationalEventProposal` after authorization.
- **Implemented by:** a deterministic parser adapter initially, an LLM-backed adapter later, or a
  composite adapter; no implementation is selected in this stage.
- **Contract:** extract one `ProposalExtractionResult` from message text.
- **Why needed now:** unstructured text must be classified before safe event creation, while the
  application must control result semantics independently of parsing or AI technology.

Extraction is split across layers: the application owns required outcomes and structured proposal
data; an adapter owns the parsing mechanism. Treating extraction wholly as input-transport logic
would duplicate it across transports, while putting parsing in the domain would couple business
rules to text or AI concerns.

## Proposed application data and results

The next implementation stage may introduce these provider-neutral immutable values; names can be
adjusted without changing the specified behavior:

- `ExternalIdentity(issuer: str, subject: str)`;
- `ConversationalInput(text: str, external_identity: ExternalIdentity | None,
  source_reference: str)`;
- `EventProposal(title: str, starts_at: datetime)` as an application value, not a domain entity;
- `ProposalExtractionResult`, one of:
  - `Irrelevant`;
  - `Incomplete(missing_fields)`;
  - `Ambiguous(ambiguous_fields)`;
  - `Ready(proposal)`;
- `ConversationalIngestionResult`, one of:
  - `UnidentifiedSender`;
  - `UnauthorizedResident`;
  - `IrrelevantMessage`;
  - `IncompleteProposal(missing_fields)`;
  - `AmbiguousProposal(ambiguous_fields)`;
  - `EventCreated(event_id)`.

Only field names required to explain an incomplete or ambiguous result are returned. Follow-up
questions and conversation state are deferred.

## Behavior

1. If the input has no external identity claim, return `UnidentifiedSender`; do not resolve,
   authorize, extract, or create.
2. Resolve the external identity. If it maps to no resident, return `UnidentifiedSender`; do not
   authorize, extract, or create.
3. Ask the authorization policy whether the resident may propose events. If not, return
   `UnauthorizedResident`; do not extract or create.
4. Extract proposal information from the text.
5. Map irrelevant, incomplete, and ambiguous extraction results to their corresponding ingestion
   results without invoking `CreateEvent`.
6. For `Ready(EventProposal)`, invoke `CreateEvent` exactly once with the proposal title and start
   time, the resolved resident identity as `actor_id`, and the unchanged source reference. Return
   `EventCreated` with its event identifier.

## Invariants

- Telegram and other SDK types, exceptions, and transport identity types never enter domain or
  application code.
- External identity is never used directly as resident identity.
- `EventProposalAuthorization` in the application layer owns the operation-specific authorization
  decision. Facts adapters only report configured permission facts.
- Missing or ambiguous event information is never invented.
- `CreateEvent` is invoked only for a ready proposal from an identified, authorized resident.
- Every created event retains the resolved resident identity and original opaque source reference.
- No conversational outcome creates a new domain type.
- Different transport adapters feed the same provider-neutral application use case without changing
  domain types or authorization policy.
- Core application and domain modules have no Telegram or extraction-provider SDK imports.

## Acceptance criteria

1. Given conversational input with no external identity claim, ingestion returns
   `UnidentifiedSender`, invokes neither extraction nor `CreateEvent`, and stores no event.
2. Given an external identity that resolves to no resident, ingestion returns `UnidentifiedSender`,
   invokes neither authorization, extraction, nor `CreateEvent`, and stores no event.
3. Given a resolved resident who may not propose events, ingestion returns `UnauthorizedResident`,
   does not invoke extraction or `CreateEvent`, and stores no event.
4. Given an authorized resident and extraction classified as irrelevant, ingestion returns
   `IrrelevantMessage`, does not invoke `CreateEvent`, and stores no event.
5. Given an authorized resident and extraction missing required fields, ingestion returns
   `IncompleteProposal` identifying those fields, does not invoke `CreateEvent`, and stores no
   event.
6. Given an authorized resident and extraction with ambiguous fields, ingestion returns
   `AmbiguousProposal` identifying those fields, does not invoke `CreateEvent`, and stores no event.
7. Given an authorized resident and a ready proposal, ingestion invokes `CreateEvent` exactly once
   and returns `EventCreated` containing the created event identifier.
8. The event created from a ready proposal retains the extracted title and timezone-aware start
   time, the resolved resident identity as actor, and the input source reference unchanged.

## Failure/result cases

| Situation | Observable result | Event created? |
| --- | --- | --- |
| Sender claim absent or not mapped | `UnidentifiedSender` | No |
| Resident identified but not permitted | `UnauthorizedResident` | No |
| Message not about an event | `IrrelevantMessage` | No |
| Required event value missing | `IncompleteProposal(missing_fields)` | No |
| Event value has multiple unsafe interpretations | `AmbiguousProposal(ambiguous_fields)` | No |
| Authorized and complete proposal | `EventCreated(event_id)` | Yes |

Failures from identity, authorization, or extraction adapters that indicate operational outages are
not converted into the semantic results above; error propagation, retry, and observability policy
will be specified with the runtime. No outcome silently creates or guesses event information.

## Design answers

### At what exact point is `CreateEvent` invoked?

After external identity resolves to a resident, authorization permits that resident to propose
events, and extraction returns `Ready` with all required values unambiguous. The ingestion use case
then invokes `CreateEvent` exactly once. No other outcome invokes it.

### What prevents Telegram-specific authorization policy from leaking into the adapter?

The application implements `EventProposalAuthorization` and evaluates it using only
`ResidentIdentity` plus facts read through `EventProposalPermissionFacts`. Telegram authentication
ends at producing an external identity claim. A Telegram adapter neither implements the policy nor
decides whether the operation proceeds; every transport reaches the same application use case and
policy.

### Where can an LLM be inserted later without changing the domain?

An LLM-backed adapter can implement `EventProposalExtractor`. It translates provider output into the
application-owned extraction results and proposal value. Prompting, provider SDKs, and failures stay
in that adapter/infrastructure; the domain and ingestion policy remain unchanged.

## Scope exclusions

This stage adds no production code, tests, dependencies, Telegram SDK, polling/webhooks, bot runtime,
LLM integration, prompts, conversation persistence, production identity database, RBAC framework,
publishing integration, calendar synchronization, Instagram support, or deployment. Follow-up
questions, retries, operational error handling, and multi-message proposal assembly are also
deferred until separately specified.
