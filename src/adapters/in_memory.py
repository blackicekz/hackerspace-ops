from src.domain import Event


class InMemoryEventRepository:
    def __init__(self) -> None:
        self.events: dict[str, Event] = {}

    def add(self, event: Event) -> None:
        self.events[event.id] = event

    def get(self, event_id: str) -> Event | None:
        return self.events.get(event_id)


class FixedIdentifierGenerator:
    def __init__(self, value: str) -> None:
        self._value = value

    def new_id(self) -> str:
        return self._value
