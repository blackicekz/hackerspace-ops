# Implement a feature or change

This is the reusable procedure for making a change to this repository under
[Spec-Driven Development](../../specs/architecture/adr/0003-spec-driven-development.md). It is the
same for a human developer and for a coding agent.

0. **Start from a `ready` Issue.** Work begins from a GitHub Issue that triage
   ([`triage-issue.md`](triage-issue.md)) has labelled `ready` and that nobody has claimed. Claim
   it and branch as described in
   [`docs/development/issue-lifecycle.md`](../development/issue-lifecycle.md). The Issue's triage
   comment names the specification(s) to change and the draft acceptance criteria.
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
5. **Define the capability as a tool.** If the change adds or alters a use case, state its tool
   exposure in the specification — tool name, when a caller should invoke it, side effects,
   idempotency, and every result variant — and keep the use case to a typed command and a typed
   result union ([ADR 0007](../../specs/architecture/adr/0007-use-cases-as-tool-surface.md)).
   Reply wording belongs to the transport, not the use case.
6. **Add or update tests corresponding to the acceptance criteria.** Tests should cite or clearly
   correspond to the criteria they verify.
7. **Implement the smallest coherent change** that satisfies the specification and respects
   [Clean Architecture dependency rules](../../specs/architecture/boundaries.md).
8. **Run the canonical repository verification command** (see
   [`docs/development/README.md`](../development/README.md#canonical-verification-command)).
9. **Review the diff against the specification and the
   [Definition of Done](../development/definition-of-done.md).**
10. **Update documentation or write an ADR only when required** — see
    [`docs/development/adr-process.md`](../development/adr-process.md) for when a decision needs
    an ADR.
11. **Open a Pull Request** from the template, with `Closes #<number>`; the template's sections
    are the completion report. Move the Issue to `in-review` and stop: merging and deployment are
    a maintainer's actions.

If at any step the Issue cannot be satisfied within its specification and scope, comment on the
Issue with what is missing, apply `blocked`, and stop rather than widening the change.
