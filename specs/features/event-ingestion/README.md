# Event ingestion: create an event

## Purpose

Turn a normalized instruction from an already-authorized resident into a valid stored event.
Transport authentication, identity resolution, authorization, and conversational extraction happen
before this lower-level slice and are out of scope here.

## Terminology

- **Instruction**: provider-neutral event data produced by an authenticated input adapter.
- **Actor**: the provider-neutral identity of the authorized resident responsible for the
  instruction.
- **Source reference**: opaque provenance that lets an adapter trace the instruction.
- **Event**: the domain entity created from a valid instruction.

## Inputs

The application command receives a title, timezone-aware start time, actor identifier, and source
reference. It receives no Telegram message or vendor SDK type.

## Behavior

The use case obtains an identifier through a port, constructs a domain event, stores it through a
repository port, and returns its identifier. Domain validation happens before storage.

## Invariants

- Title, actor identifier, and source reference are non-blank.
- Start time has an explicit UTC offset.
- An event is stored only after all invariants hold.

## Acceptance criteria

1. Given an authorized actor, title, timezone-aware start time, and source reference, creating an
   event stores it and returns the generated event identifier.
2. The stored event retains its title, start time, actor, and source reference.
3. A blank title is rejected and nothing is stored.
4. A start time without timezone information is rejected and nothing is stored.
5. A blank actor identifier is rejected and nothing is stored.
6. A blank source reference is rejected and nothing is stored.
7. A message adapter translates a normalized authorized-user instruction into the same use case;
   vendor-specific Telegram objects never enter the application or domain layers.

## Failure cases

A blank title, actor identifier, or source reference, or a start time without timezone information,
raises `ValueError`. The repository remains unchanged. Authentication, identity resolution, and
authorization failures are intentionally outside this use case: its caller invokes it only after
those checks succeed.
