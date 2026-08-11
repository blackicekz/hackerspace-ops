from typing import Protocol

from src.domain import Event


class EventRepository(Protocol):
    def add(self, event: Event) -> None: ...


class IdentifierGenerator(Protocol):
    def new_id(self) -> str: ...
