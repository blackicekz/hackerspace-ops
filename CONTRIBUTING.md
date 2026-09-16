# Contributing

Thank you for contributing to Hackerspace Ops.

This project is developed by humans and by coding agents under one process. This file is the entry
point for human contributors; coding agents start from [`AGENTS.md`](AGENTS.md). Both lead to the
same canonical documents: specifications in [`specs/`](specs/README.md), development policy in
[`docs/development/`](docs/development/README.md), and procedures in
[`docs/workflows/`](docs/workflows/implement-feature.md).

## Workflow

1. Start from a GitHub Issue labelled `ready` with no assignee, or file one through the issue
   templates and wait for triage. States and labels are in
   [`docs/development/issue-lifecycle.md`](docs/development/issue-lifecycle.md).
2. Claim the Issue and create a branch from `master` named `issue-<number>-<short-slug>`.
3. Follow [`docs/workflows/implement-feature.md`](docs/workflows/implement-feature.md):
   specification and acceptance criteria first, then tests, then the smallest implementation.
4. Make only changes related to the Issue.
5. Run the canonical check:

   ```sh
   docker compose run --rm app check
   ```

6. Open a Pull Request using the template; it must contain `Closes #<number>`.

## Development principles

- Follow the existing architecture and specifications.
- Prefer small, independent changes.
- Do not duplicate business logic or infrastructure rules.
- Do not change public contracts without a clear need.
- Add or update tests whenever behaviour changes.
- Keep development equally accessible to humans and to coding agents: if a step needs knowledge
  that is not written down in the repository, write it down.

## Language

Specifications, code, tests, and development documentation are in English. Issue templates and
the bot's replies to residents are in the residents' language (currently Russian). See
[`specs/README.md`](specs/README.md#language).

## Commits

Use short messages in the imperative style:

```text
Add event publishing workflow
Fix calendar event validation
Update contributor documentation
```

## Pull Requests

A Pull Request must:

- solve one clearly defined task;
- reference its Issue with `Closes #<number>`;
- follow [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md), which is the
  completion report for humans and agents alike;
- pass `docker compose run --rm app check`;
- contain no unrelated changes.

Every Pull Request is reviewed by a human maintainer before merge, whoever or whatever authored
it. See [review and accountability](docs/development/contribution-norms.md#review-and-accountability).

## Definition of Done

A change is done when the Issue's requirements are met, documentation and tests are current, the
canonical check passes, and the criteria in
[`docs/development/definition-of-done.md`](docs/development/definition-of-done.md) hold.
