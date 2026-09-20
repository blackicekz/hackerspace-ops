# Implement an Issue

This is the agent-neutral procedure for the normal development cycle:

```text
GitHub Issue -> local branch -> implementation -> verification -> Pull Request
```

It applies to human contributors and coding agents, including Codex and Claude. Roles are logical
responsibilities in the current session, not independently running LLM agents. Select only the
responsibilities needed by the Issue; there is no mandatory `specification -> architecture ->
developer -> reviewer` pipeline.

## Procedure

0. **Read the Issue and repository instructions.** Read the referenced GitHub Issue, inspect the
   current branch and working-tree state, and read the relevant repository documentation before
   editing. Preserve unrelated contributor changes. Inspect recent Git history when it helps
   explain an existing convention.

1. **Determine the scope and responsibilities.** Decide whether the Issue needs specification,
   architecture, implementation, tests, documentation, review, or another repository-defined
   responsibility. A small documentation or internal-only change may need only implementation and
   verification; a new capability may need several responsibilities.

2. **Claim the Issue and create the branch.** Work only from a `ready` Issue with no assignee.
   Claim it according to [`issue-lifecycle.md`](../development/issue-lifecycle.md), then create
   or switch to `issue-<number>-<short-slug>` from `master`. Do not destroy unrelated work or
   edit `master` directly.

3. **Read the relevant specification and architecture.** Find the affected feature under
   [`specs/features/`](../../specs/features/) or determine whether a new feature specification is
   needed. Read [`system.md`](../../specs/architecture/system.md),
   [`boundaries.md`](../../specs/architecture/boundaries.md), and relevant ADRs for touched
   boundaries.

4. **Decide whether specification artifacts are required.** GitHub Issues are the intake and
   record the original request; `feature_request.yml` and `bug_report.yml` are Issue templates,
   not specifications. Update or add a specification when observable behaviour, acceptance
   criteria, or a capability changes. For an internal-only or documentation-only change, do not
   manufacture a specification. A changed or new use case must also state its tool exposure as
   required by ADR 0007. Do not require `spec.md` mechanically when the repository does not use it.

5. **Update tests and implementation.** When behaviour changes, make acceptance criteria explicit
   and testable, update acceptance tests, and implement the smallest coherent change. Keep
   external APIs, SDKs, transports, and AI providers behind the repository's defined boundaries.
   Update documentation or add an ADR only when the change requires it.

6. **Run the canonical verification.** Run exactly:

   ```sh
   docker compose run --rm app check
   ```

   Fix failures caused by the Issue and repeat the check. Report unrelated pre-existing failures
   instead of broadening scope.

7. **Review and publish the branch.** Review the diff against the Issue, specification, and
   Definition of Done. Commit only related changes, then push the task branch when authenticated
   GitHub access is available.

8. **Create the Pull Request and stop.** Use [`.github/PULL_REQUEST_TEMPLATE.md`](../../.github/PULL_REQUEST_TEMPLATE.md),
   include `Closes #<number>`, record the final canonical verification result and deferred work,
   state that the change was authored by a coding agent when applicable, and move the Issue to
   `in-review`. Pull Request creation ends this normal cycle. Do not merge or deploy.

If the Issue cannot be completed within its approved scope, comment the missing decision or work,
apply `blocked` according to the lifecycle, and stop. Do not widen the Issue to make it fit.

## Failure boundary

Deterministic CI may report failures after the Pull Request is created. The repository does not
wake an LLM, monitor CI for repair, retry integration tests through an LLM, or require an external
orchestration service or paid API. A contributor explicitly starts a new session with the failure
information or a new Issue.
