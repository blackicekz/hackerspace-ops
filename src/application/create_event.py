from dataclasses import dataclass
from datetime import datetime

from src.application.ports import EventRepository, IdentifierGenerator
from src.domain import Event


@dataclass(frozen=True)
class CreateEventCommand:
    title: str
    starts_at: datetime
    actor_id: str
    source_reference: str


class CreateEvent:
    def __init__(self, repository: EventRepository, identifiers: IdentifierGenerator) -> None:
        self._repository = repository
        self._identifiers = identifiers

    def execute(self, command: CreateEventCommand) -> str:
        event = Event(
            id=self._identifiers.new_id(),
            title=command.title.strip(),
            starts_at=command.starts_at,
            created_by=command.actor_id,
            source_reference=command.source_reference,
        )
        self._repository.add(event)
        return event.id
