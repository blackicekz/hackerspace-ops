# Issue lifecycle

GitHub Issues are the single intake for feature requests and bug reports. This document defines
the states an Issue passes through, the labels that represent them, and who moves an Issue from
one state to the next. It applies identically whether the contributor is a human developer, a
human working with an AI tool, or a coding agent running in a loop.

## States and labels

| State | Label | Meaning |
| --- | --- | --- |
| New | `needs-triage` | Filed through a template; not yet reviewed. Applied automatically or at first look. |
| Needs input | `needs-info` | Triage could not produce testable acceptance criteria; a question is open to the reporter. |
| Ready | `ready` | Has explicit, testable acceptance criteria and a bounded scope; a maintainer has approved it for implementation. **Only `ready` Issues are picked up for implementation.** |
| In progress | `in-progress` | Claimed by a contributor (assignee set); a branch exists. |
| In review | `in-review` | A Pull Request referencing the Issue is open and passes the canonical check. |
| Blocked | `blocked` | Waiting on a decision, an ADR, or another Issue; the blocker is named in a comment. |
| Done | *(closed)* | The Pull Request is merged; the Issue closes via `Closes #<n>`. Deployment is tracked separately (see below). |

`feature` and `bug` (set by the templates) describe the kind of Issue and stay throughout. Exactly
one state label is present at a time.

## Who does what

**Reporters** (residents, operators, anyone) file Issues through the templates and answer
`needs-info` questions. They are not expected to know the codebase.

**Maintainers** (humans with write access) triage: they read the Issue, follow
[`docs/workflows/triage-issue.md`](../workflows/triage-issue.md), and move it to `ready`,
`needs-info`, or close it with a reason. A coding agent may draft the triage — proposed acceptance
criteria, scope, affected specifications — as a comment, but only a maintainer applies the `ready`
label. Maintainers also review Pull Requests, merge, and run the `deploy` workflow.

**Contributors** (human developers or coding agents) implement `ready` Issues by following
[`docs/workflows/implement-feature.md`](../workflows/implement-feature.md).

## Claiming and reporting work

1. Pick an Issue that is `ready` and has no assignee.
2. Claim it: set yourself as assignee (or, for an agent without that permission, comment
   `Claiming this issue.`) and replace `ready` with `in-progress`. Never work on an Issue someone
   else has claimed.
3. Branch from `master` as `issue-<number>-<short-slug>`.
4. Open a Pull Request whose description follows
   [`.github/PULL_REQUEST_TEMPLATE.md`](../../.github/PULL_REQUEST_TEMPLATE.md) and contains
   `Closes #<number>`. Replace `in-progress` with `in-review`.
5. Respond to review on the same branch. When the PR is merged the Issue closes automatically.

The Pull Request description is where the completion report required by `AGENTS.md` goes. It is
the same report for a human and for an agent.

## Boundaries for coding agents in a loop

An agent running unattended may do everything a contributor does *up to* opening a Pull Request
and responding to review. It does not apply `ready`, merge, close Issues by hand, edit `master`
directly, run the `deploy` workflow, or touch the operator's `.env`. A human review of every
agent-authored Pull Request is required before merge; see
[`contribution-norms.md`](contribution-norms.md#review-and-accountability).

If an agent cannot satisfy a `ready` Issue within its specification — the criteria turn out to be
untestable, the scope needs an ADR, or the change would break an architecture boundary — it
comments what is missing, applies `blocked`, and stops. It does not widen scope to make the Issue
fit.

## Deployment

Merging to `master` does not deploy. A maintainer runs the `deploy` workflow manually
([ADR 0006](../../specs/architecture/adr/0006-self-hosted-cd-deployment.md)). An Issue may be
closed before its change is live; if a reporter needs to know when it is, the maintainer comments
on the Issue after deploying.
