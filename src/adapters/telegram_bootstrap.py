from dataclasses import dataclass

START_REPLY = "Hackerspace Ops bootstrap bot is running."
HELP_REPLY = "Supported commands: /start, /help."

_REPLIES = {"/start": START_REPLY, "/help": HELP_REPLY}


@dataclass(frozen=True)
class BootstrapCommand:
    """A provider-neutral text message eligible for a /start or /help reply."""

    chat_id: int
    text: str
    sender_is_bot: bool


def reply_for(command: BootstrapCommand, test_chat_id: int) -> str | None:
    if command.sender_is_bot or command.chat_id != test_chat_id:
        return None
    return _REPLIES.get(_command_name(command.text))


def _command_name(text: str) -> str:
    if not text:
        return ""
    return text.split()[0].split("@")[0]
