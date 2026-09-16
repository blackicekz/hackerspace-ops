# ADR 0007: Application use cases are the tool surface; an AI assistant is a caller

Status: accepted

## Decision

Hackerspace Ops is a set of operational capabilities implemented as deterministic code in the
application layer. Those capabilities have two kinds of callers, and both are first-class:

- **Residents**, through human transports such as Telegram commands.
- **An AI assistant**, through a tool interface that exposes the same use cases as callable tools.

The assistant is a *caller* of the bot, in the same position as a human transport. It is not the
core of the bot, and the bot does not depend on it. The bot must remain fully operable without any
assistant, and every capability the assistant can invoke must also be reachable by a human through
some transport.

## Consequences for every use case

1. A use case is defined by a typed command and a typed result union (as
   `IngestConversationalEventProposal` already is). It has no side channels: everything an
   assistant or a human needs to decide what to do next is in the result value.
2. The use case's specification and docstring describe it well enough that an assistant can
   choose and call it correctly: purpose, when to call it, inputs, every result variant, side
   effects, and whether it is idempotent. This is part of the Definition of Done, not
   documentation polish.
3. Result variants are semantic (`IncompleteProposal(missing_fields)`), never presentation text.
   Wording belongs to the transport that presents the result, human or assistant.

## Authorization: the assistant acts on behalf of a resident

The assistant has no permissions of its own. Every tool call carries the external identity of the
resident on whose behalf it is made, exactly as a Telegram update carries its sender. The tool
adapter is a transport in the sense of [ADR 0004](0004-transport-authentication-and-application-authorization.md):
it authenticates the assistant session and the delegated resident claim, emits an
`ExternalIdentity` with its own issuer, and stops there. Identity resolution and the
operation-specific authorization decision stay in the application layer and are identical for
every caller. An assistant therefore can never do what the initiating resident could not do
themselves, and audit trails (`created_by`, `source_reference`) name the resident, never the
assistant.

Autonomous assistant work with no initiating resident is not covered by this decision. If it is
ever needed, it requires a separate ADR that defines a service principal and its permission facts.

## Where language understanding lives

Understanding free-form text, deciding which capability applies, asking the resident follow-up
questions, and assembling a complete request from a conversation are the assistant's job, outside
the bot. Inside the bot, an LLM may appear only as a replaceable adapter behind a narrow
application-owned port, as allowed by [ADR 0001](0001-clean-architecture.md), and only when a
specification calls for it. The existing `EventProposalExtractor` port is such a seam; the
explicit `/event` command syntax in `telegram-input` is the human tool that makes the runtime
usable with no LLM at all. Building a natural-language extractor inside the bot is not the
default direction of this project and is not planned.

## Capability catalogue

When the assistant tool interface is specified, the application layer will own a catalogue of its
use cases: name, description, command schema, and result variants. Tool adapters (and, later,
other transports) read the catalogue instead of knowing individual use cases. Adding a capability
then means adding a use case and its catalogue entry, never adding a handler to a specific
transport. The catalogue's shape is deferred to
[`specs/features/assistant-tool-interface/`](../../features/assistant-tool-interface/README.md).

## Rationale

The alternative — putting an LLM at the centre and letting it act directly on external platforms —
makes behaviour non-reproducible, untestable against acceptance criteria, and impossible to review
by residents who do not read prompts. Keeping capabilities as code keeps them verifiable by the
canonical check, replaceable independently of any AI vendor, and equally usable by residents who
prefer explicit commands. The cost is that each capability needs a human-facing transport as well
as a tool description; that cost is accepted.
