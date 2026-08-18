# Implement a feature or change

This is the reusable procedure for making a change to this repository under
[Spec-Driven Development](../../specs/architecture/adr/0003-spec-driven-development.md).

1. **Identify the relevant specification.** Find the feature specification in
   [`specs/features/`](../../specs/features/) that covers the behaviour being changed, or
   determine that a new one is needed.
2. **Read architecture constraints relevant to the change.** Review
   [`specs/architecture/system.md`](../../specs/architecture/system.md) and
   [`specs/architecture/boundaries.md`](../../specs/architecture/boundaries.md) for the layers and
   ports the change touches.
3. **Determine whether observable behaviour must change.** Distinguish a behaviour change from an
   internal-only change; only the former requires updating a specification.
4. **Update the specification and acceptance criteria first when behaviour changes.** Acceptance
   criteria must be explicit and testable before implementation begins, per
   [`specs/README.md`](../../specs/README.md).
5. **Add or update tests corresponding to the acceptance criteria.** Tests should cite or clearly
   correspond to the criteria they verify.
6. **Implement the smallest coherent change** that satisfies the specification and respects
   [Clean Architecture dependency rules](../../specs/architecture/boundaries.md).
7. **Run the canonical repository verification command** (see
   [`docs/development/README.md`](../development/README.md#canonical-verification-command)).
8. **Review the diff against the specification and the
   [Definition of Done](../development/definition-of-done.md).**
9. **Update documentation or write an ADR only when required** — see
   [`docs/development/adr-process.md`](../development/adr-process.md) for when a decision needs an
   ADR.

This procedure describes the change itself, not how any particular development harness reports
progress or completion to its user.
