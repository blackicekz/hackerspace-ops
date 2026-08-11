from datetime import datetime
from typing import Protocol

from src.application import CreateEvent, CreateEventCommand


class AuthorizedEventInstruction(Protocol):
    @property
    def title(self) -> str: ...

    @property
    def starts_at(self) -> datetime: ...

    @property
    def actor_id(self) -> str: ...

    @property
    def source_reference(self) -> str: ...


class EventInstructionHandler:
    """Vendor-neutral boundary for authenticated, normalized messages."""

    def __init__(self, create_event: CreateEvent) -> None:
        self._create_event = create_event

    def handle(self, instruction: AuthorizedEventInstruction) -> str:
        return self._create_event.execute(
            CreateEventCommand(
                title=instruction.title,
                starts_at=instruction.starts_at,
                actor_id=instruction.actor_id,
                source_reference=instruction.source_reference,
            )
        )
