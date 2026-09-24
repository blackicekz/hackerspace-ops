# Calendar approval permissions

## Purpose

Provide one application-owned permission fact for residents who may approve calendar changes. The
fact can be read from Google Sheets, PostgreSQL, or SQLite through interchangeable adapters.

This feature does not yet publish, update, or delete calendar events. It prepares the authorization
boundary required by those later use cases.

## Terminology

- **Resident ID**: the stable provider-neutral `ResidentIdentity.value` used by application code.
- **Calendar approver**: a resident whose ID is present in the configured permission source.
- **Permission source**: exactly one configured backend selected by infrastructure at runtime.

## Storage decision

The three backends are alternative implementations of the same read contract. The application does
not write the same permission row to all three stores, and it does not merge conflicting answers.
Infrastructure selects one source for a deployment. This avoids an undefined multi-master
consistency model and lets the source migrate later without changing authorization policy.

Each backend stores one stable `resident_id` per calendar approver:

```text
resident_id
resident-42
resident-91
```

Google Sheets uses a `resident_id` header in the first column. PostgreSQL and SQLite use:

```sql
CREATE TABLE calendar_approvers (
    resident_id TEXT PRIMARY KEY
);
```

The adapters only provide permission facts. They do not decide policy, resolve Telegram IDs, or
expose a permission-management tool.

## Behavior

1. Given a `ResidentIdentity`, the configured source reports whether its value is an approver.
2. Google Sheets rows are validated before their IDs are used; blank and duplicate IDs are errors.
3. SQL adapters use parameterized queries and the same table/column contract.
4. A source failure raises an operational `PermissionSourceError`; it is not converted into an
   approval. Callers must fail closed for privileged operations.
5. An empty valid source means that no resident may approve calendar changes.
6. The application policy delegates the decision to the permission facts and remains independent
   of all storage providers.

## Acceptance criteria

1. A resident ID present in a valid Google Sheet first column is recognized as a calendar approver.
2. A resident ID absent from a valid Google Sheet is not recognized as a calendar approver.
3. Blank or duplicate Google Sheet resident IDs are rejected as invalid permission data.
4. The Google Sheets adapter requests only the configured spreadsheet and range through its narrow
   reader boundary; Google credential construction remains outside application code.
5. SQLite recognizes rows in `calendar_approvers` using a parameterized lookup.
6. PostgreSQL recognizes rows in `calendar_approvers` using a parameterized lookup and closes its
   cursor after the operation.
7. A failed external permission read raises an operational source error and cannot grant access.
8. The application authorization policy produces the same decision regardless of which adapter
   supplies the permission fact.
9. No calendar event is created, changed, deleted, or published by this feature.

## Tool exposure

This feature adds no use case and no assistant tool. The permission policy is an internal
application service used by the future calendar approval use cases.

## Deferred work

- Permission-entry administration and audit history.
- Google credential construction, token rotation, and infrastructure wiring.
- Selection/configuration of the active backend in deployment settings.
- Calendar event creation, update, cancellation/deletion, and approval workflow.
