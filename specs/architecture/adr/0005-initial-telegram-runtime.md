# ADR 0005: python-telegram-bot with long polling for the initial Telegram runtime

Status: accepted

Use `python-telegram-bot==22.8` for the first Telegram adapter and run it with long polling. The
library is maintained, production/stable, asynchronous, typed, compatible with Python 3.13, and
supports both polling and webhooks. Its required dependency surface is small: the default networking
backend requires `httpx`, while webhook server support is optional. Pin the direct dependency to the
exact reviewed version in the container build input; update it deliberately through verification.

Long polling requires no public HTTPS endpoint, certificate, reverse proxy, or inbound port, making
local Docker use and a first small deployment straightforward. Only one bot process may poll a token
at a time. The runtime relies on the SDK's polling lifecycle and graceful signal handling. A future
webhook infrastructure adapter can feed the same Telegram message adapter and application use case
without changing domain or application code.

Considered alternatives were aiogram 3.30.0 and PyTelegramBotAPI. Aiogram is maintained, typed,
asynchronous, and supports both delivery modes, but its larger bot-framework feature set is not
needed for this narrow adapter. PyTelegramBotAPI supports synchronous and asynchronous operation but
does not offer a compensating advantage over the selected fully typed async lifecycle.

Primary references reviewed on 2026-08-12:

- [python-telegram-bot 22.8 package metadata](https://pypi.org/project/python-telegram-bot/)
- [python-telegram-bot Application lifecycle](https://docs.python-telegram-bot.org/en/v22.8/telegram.ext.application.html)
- [aiogram package metadata](https://pypi.org/project/aiogram/)
- [PyTelegramBotAPI package metadata](https://pypi.org/project/pyTelegramBotAPI/)
- [Telegram Bot API update delivery](https://core.telegram.org/bots/api#getting-updates)
