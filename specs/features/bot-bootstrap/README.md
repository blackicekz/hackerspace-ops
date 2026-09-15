# Bot bootstrap and CD verification

## Purpose

Stand up the smallest possible executable, deployable Telegram bot before any product feature work
begins, to validate the deployment path end to end: build the runtime image, run it as the `bot`
Compose service, and deploy it through the CD workflow onto the self-hosted GitHub Actions runner
already registered on the target host. The bot's only observable behavior is replying to the
universal Telegram `/start` and `/help` commands in one configured test group. This slice
intentionally carries no hackerspace domain behavior: it creates no events, resolves no residents,
and decides no authorization.

## Relationship to telegram-input

[`telegram-input`](../telegram-input/README.md) specifies the eventual `/event` ingestion runtime,
built on the same `python-telegram-bot` polling runtime
([ADR 0005](../../architecture/adr/0005-initial-telegram-runtime.md)) and the same Docker `bot`
service and infrastructure bootstrap layout. This spec implements that runtime's first slice:
process startup, configuration loading, the polling lifecycle, and Docker/CD wiring, with `/start`
and `/help` as the only recognized commands. When `/event` extraction and authorization are
implemented, they extend this same adapter and bootstrap rather than replace it. `/start` and
`/help` remain always-available, authorization-free bot commands and are not subject to
telegram-input's "ignore commands other than `/event`" rule.

## Terminology

- **Test group**: the one Telegram chat, identified by `HACKERSPACE_TEST_CHAT_ID`, that this
  bootstrap bot is allowed to respond in.
- **Eligible message**: a new, human-authored `/start` or `/help` text command, addressed to this
  bot, sent in the test group.

## Inputs

The bot receives Telegram `message` updates via long polling (ADR 0005). It reads no other update
kind.

## Behavior

1. `/start` (and `/start@bot_username`) sent by a human in the test group replies with a short
   one-line identification message naming the bot as a hackerspace-ops bootstrap deployment.
2. `/help` (and `/help@bot_username`) sent by a human in the test group replies by listing the
   currently supported commands (`/start`, `/help`).
3. Any other message or command, a message sent in a chat other than the configured test group, or
   a message authored by a bot account, is ignored: no reply, no processing.

## Configuration

| Variable | Required | Meaning |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Yes | Secret bot token issued by BotFather. |
| `HACKERSPACE_TEST_CHAT_ID` | Yes | Telegram chat ID of the one test group this bootstrap bot responds in. |
| `HACKERSPACE_LOG_LEVEL` | No | Standard log level, default `INFO`. |

These values live in an operator-managed, uncommitted `.env` file, consistent with
telegram-input's configuration rule and
[contribution-norms.md](../../../docs/development/contribution-norms.md)'s no-secrets rule. `.env`
is never read into the repository or logs. Missing or invalid configuration fails startup before
any Telegram contact and names the missing variable, never its value.

The operator-managed `.env` lives at a fixed path outside the CD workflow's checkout, not inside
the repository checkout itself: `actions/checkout` runs `git clean -ffdx` before every run, which
deletes any untracked file — including a manually placed `.env` — from the checked-out working
directory. The canonical location is `/opt/github-actions-runner/secrets/hackerspace-ops.env` on
the target host; the `deploy` workflow copies it into the checkout before building the image (see
CD verification below).

A future change will move non-sensitive settings (chat IDs, privileged user lists, and similar) to
a Google Sheet or a database; `TELEGRAM_BOT_TOKEN` remains a secret regardless of that migration,
which is explicitly out of scope here.

## Docker runtime interface

Realizes telegram-input's previously designed, not-yet-built interface:

```sh
docker compose build bot
docker compose up -d bot
docker compose run --rm app check
```

The `bot` service uses the Dockerfile's `runtime` target, receives configuration only via
`env_file: .env`, exposes no inbound port, and has no host source bind mount.

## CD verification

A `deploy` GitHub Actions workflow, manually triggered (`workflow_dispatch`) for this stage, runs
on the self-hosted runner already registered on the target host:

1. Checks out the repository at the dispatched ref (destructively cleaning the working directory).
2. Copies the operator-managed `.env` from its fixed, out-of-checkout path into the checkout.
3. Builds the `bot` service image locally on the host.
4. Restarts the `bot` service (`docker compose up -d bot`) using the copied `.env` file.

The workflow reads the operator-managed `.env` byte-for-byte; it never generates, edits, or prints
its contents. The operator manages that file's content directly on the host, outside the
repository checkout, so it survives every run's clean checkout. See
[ADR 0006](../../architecture/adr/0006-self-hosted-cd-deployment.md) for why the trigger is manual
at this stage and for the fixed-path decision.

## Invariants

- No application or domain code is invoked; `src/adapters` and `src/infrastructure` are the only
  layers touched.
- The Telegram bot token and chat ID are never logged or committed.
- The bot never processes or replies in a chat other than the configured test group.
- Telegram SDK types stop at the adapter boundary, matching
  [`specs/architecture/boundaries.md`](../../architecture/boundaries.md).

## Acceptance criteria

1. Given `/start` sent by a non-bot sender in the configured test group, the bot replies with the
   identification message exactly once.
2. Given `/help` sent by a non-bot sender in the configured test group, the bot replies with the
   supported-commands message, naming both `/start` and `/help`, exactly once.
3. Given `/start` or `/help` sent in any chat other than the configured test group, the bot sends
   no reply.
4. Given any other text, command, or non-text content in the configured test group, the bot sends
   no reply.
5. Given a message authored by a bot account, the bot sends no reply, even in the configured test
   group.
6. Missing or invalid `TELEGRAM_BOT_TOKEN` or `HACKERSPACE_TEST_CHAT_ID` terminates startup before
   polling begins and names the missing or invalid variable without its value.
7. The `bot` Compose service builds from the `runtime` Dockerfile target and starts without a host
   source bind mount or inbound port.
8. Running the `deploy` workflow via manual dispatch against the self-hosted runner successfully
   starts the `bot` service on the target host, and the bot visibly answers `/start` and `/help` in
   the real test group.

Criteria 1-6 are covered by acceptance tests. Criteria 7-8 are operational and are verified by
running the Docker and CD commands above against the target host; they are not exercised by the
automated test suite.

## Operational failures

- **Telegram network/API interruption**: rely on SDK polling reconnection; log a sanitized warning.
- **Persistent startup/authentication error**: terminate the process; do not fall back to silent
  retry.
- **Malformed or unsupported update**: ignore silently, continue polling.

## Scope exclusions

This bootstrap deliberately excludes `/event` extraction, resident identity resolution,
authorization, event creation, persistence beyond process memory, Google Sheets/database-backed
configuration, automatic CD triggering on push, and any product feature behavior. These remain the
concern of `telegram-input` and later features.
