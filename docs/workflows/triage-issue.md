# Triage an Issue into a specification

This is the reusable procedure for turning a filed Issue into work that
[`implement-feature.md`](implement-feature.md) can start from. It is performed by a maintainer;
a coding agent may draft steps 1–5 as an Issue comment for a maintainer to confirm. States and
labels are defined in [`issue-lifecycle.md`](../development/issue-lifecycle.md).

1. **Check for duplicates and scope.** Search open and closed Issues. If the request duplicates
   one, close it with a link. If it bundles several independent changes, split it and link the
   parts.
2. **Locate the affected specification.** Find the feature under `specs/features/` whose
   behaviour the Issue changes, or decide that a new feature directory is needed. A bug report
   maps to the specification whose acceptance criteria it violates; if no criterion covers the
   reported behaviour, the fix includes adding one.
3. **Translate the Issue into specification terms.** Issue templates are written for residents,
   in their language; specifications are in English and use the
   [glossary](../../specs/README.md#glossary). Map the template fields:

   | Issue field (feature) | Specification section |
   | --- | --- |
   | Проблема / Желаемый результат | Purpose |
   | Сценарий использования | Behavior |
   | Критерии готовности | Acceptance criteria (numbered, one observable outcome each) |
   | Ограничения и важные условия | Invariants; Failure cases |
   | Примеры и материалы | Inputs; examples inside Behavior |

   | Issue field (bug) | Specification section |
   | --- | --- |
   | Что произошло / Что должно было произойти | The violated or missing acceptance criterion |
   | Как воспроизвести | The acceptance test's arrange/act steps |
   | Ограничения, контекст | Invariants; Failure cases |

   Keep the Issue as the record of the original request; do not rewrite it.
4. **Make the acceptance criteria testable.** Each criterion must be checkable by an acceptance
   test without reading the implementation. If that is not possible from what the reporter wrote,
   ask a specific question on the Issue and apply `needs-info`.
5. **Decide the tool exposure.** If the Issue adds or changes a capability, note the tool name,
   when a caller should invoke it, side effects, idempotency, and result variants
   ([ADR 0007](../../specs/architecture/adr/0007-use-cases-as-tool-surface.md)). If the request
   is only about how a result is worded in Telegram, it is a presentation change in the adapter,
   not a new capability.
6. **Check for architectural impact.** If the change needs a new port, a new transport, a new
   external dependency, or a change to a boundary, it needs an ADR
  ([`adr-process.md`](../development/adr-process.md)); record that in the Issue and apply
   `blocked` until the ADR exists, or make the ADR part of the Issue's scope explicitly.
7. **Write the outcome on the Issue.** Add a comment listing: the specification path(s) to
   change, the draft acceptance criteria in English, the tool exposure, out-of-scope items, and
   any ADR needed. Apply `ready` (maintainer only) or the appropriate other label.
