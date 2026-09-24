# Calendar management: open questions and temporary decisions

This note records unresolved points from GitHub Issue #2 and the temporary choices used while the
permission boundary is implemented. It is intentionally separate from the permission feature so
that the calendar CRUD contract can be finalized in a later Issue.

## Questions requiring a product decision

1. Is “cancel” a soft state in the internal event record, a Google Calendar deletion, or both?
2. Does an edit require a new approval after an event has already been published?
3. Can the author approve their own event, or must approval always come from a different resident?
4. Does one approval mean any one calendar approver, or is a quorum required?
5. What exact Google Calendar is managed, and which service account or OAuth principal owns it?
6. What is the authoritative timezone for date-only and recurring event inputs?
7. Which recurrence forms are supported, and how are exceptions, end dates, and time zones expressed?
8. How are concurrent edit, approve, cancel, and retry actions resolved?
9. What should residents see after a Google Calendar timeout or a partial success?
10. Should a failed publication be retried automatically, manually, or both?
11. Are events created as private, shared, or public Google Calendar entries?
12. What fields are required: description, location, organizer, link, attachments, and reminders?
13. Should an existing event be located by an internal event ID, Google event ID, or both?
14. Is “one or more messages” a single proposal assembled from a conversation, or several proposals?
15. Is cover generation part of this Issue, and what are its input, approval, storage, and failure
    rules?

## Gaps and problems in Issue #2

- The acceptance criteria only cover review and successful creation; they do not cover update,
  cancellation/deletion, rejection, invalid data, retries, or provider failures.
- “Delete” and “cancel” are used as if interchangeable, but they have different audit and user
  expectations.
- The event model lacks an explicit end time, timezone policy, description, location, recurrence,
  provider ID, lifecycle state, and version/concurrency marker.
- “Any resident” conflicts with the current transport design, which requires a mapped resident
  identity and a separate operation-specific authorization decision.
- The Issue does not define how an approval is bound to a particular proposal or how stale Telegram
  button presses are rejected.
- The Telegram comment defines button presentation but not callback identity, deduplication,
  locking, or what happens when two people press buttons concurrently.
- The Google Calendar account, calendar ID, OAuth/service-account model, scopes, and secret storage
  are unspecified.
- Repeating and multi-day events are mentioned but their semantics are not testable.
- Future Telegram, Instagram, website, and media publishing are useful context but should be
  separate capabilities and should not enlarge the first calendar CRUD slice.

## Temporary decisions for unattended progress

- The three permission stores are interchangeable alternatives, not a synchronized three-way
  replica. Infrastructure selects exactly one source per deployment.
- `resident_id` is the only authorization key; Telegram numeric IDs are resolved before policy.
- This step implements read-only permission facts. Permission administration remains operator-owned
  until its workflow and audit requirements are specified.
- Calendar cancellation will be treated as a domain lifecycle decision, not silently implemented as
  physical Google deletion.
- Calendar CRUD will not be implemented from Issue #2 alone. The next implementation Issue must
  first define typed event fields, lifecycle/result variants, provider identity, idempotency,
  concurrency, and failure behavior.
