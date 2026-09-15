# ADR 0006: CD deployment via the existing self-hosted runner and Docker Compose

Status: accepted

Deploy the bot to the target host by running `docker compose build bot` and `docker compose up -d
bot` on the self-hosted GitHub Actions runner already registered there, from a `deploy` workflow.
For this bootstrap stage (see `specs/features/bot-bootstrap/`) the workflow trigger is manual
(`workflow_dispatch`) rather than automatic on push to `master`, so the first pipeline runs can be
verified deliberately before any automatic deployment is wired up.

Secrets (`TELEGRAM_BOT_TOKEN`) and the test chat ID stay in an operator-managed `.env` file on the
host, read by Compose via `env_file`; the workflow never creates, edits, or prints this file,
matching the repository's no-secrets-in-git norm
([contribution-norms.md](../../../docs/development/contribution-norms.md)). The `check` workflow
(GitHub-hosted runner) and `deploy` workflow (self-hosted runner) stay separate: `check` verifies
every push and pull request, while `deploy`, in this stage, is invoked independently once a change
is ready to reach the target host.

This makes the target host, its self-hosted runner, and Docker Compose (already the toolchain per
[ADR 0002](0002-docker-toolchain.md)) the concrete deployment mechanism referenced as deferred in
[system.md](../system.md#major-decisions). A later change may switch `deploy` to trigger
automatically after `check` succeeds on `master`; that is a workflow-trigger change, not a change to
the deployment mechanism itself.
