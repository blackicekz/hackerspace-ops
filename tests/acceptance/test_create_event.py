import unittest
from dataclasses import dataclass
from datetime import UTC, datetime

from src.adapters.in_memory import FixedIdentifierGenerator, InMemoryEventRepository
from src.adapters.message_input import EventInstructionHandler
from src.application import CreateEvent, CreateEventCommand


@dataclass(frozen=True)
class AuthorizedInstruction:
    title: str
    starts_at: datetime
    actor_id: str
    source_reference: str


class CreateEventAcceptanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryEventRepository()
        self.use_case = CreateEvent(self.repository, FixedIdentifierGenerator("event-123"))
        self.handler = EventInstructionHandler(self.use_case)

    def test_authorized_instruction_creates_a_traceable_event(self) -> None:
        starts_at = datetime(2026, 9, 1, 19, tzinfo=UTC)

        event_id = self.handler.handle(
            AuthorizedInstruction("Open night", starts_at, "resident-7", "bot:message:42")
        )

        event = self.repository.get(event_id)
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual("event-123", event_id)
        self.assertEqual("Open night", event.title)
        self.assertEqual(starts_at, event.starts_at)
        self.assertEqual("resident-7", event.created_by)
        self.assertEqual("bot:message:42", event.source_reference)

    def test_blank_title_does_not_store_an_event(self) -> None:
        with self.assertRaisesRegex(ValueError, "title"):
            self.use_case.execute(
                CreateEventCommand(
                    "",
                    datetime(2026, 9, 1, 19, tzinfo=UTC),
                    "resident-7",
                    "bot:message:42",
                )
            )

        self.assertEqual({}, self.repository.events)

    def test_start_without_timezone_does_not_store_an_event(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.use_case.execute(
                CreateEventCommand(
                    "Open night", datetime(2026, 9, 1, 19), "resident-7", "bot:message:42"
                )
            )

        self.assertEqual({}, self.repository.events)

    def test_blank_actor_does_not_store_an_event(self) -> None:
        with self.assertRaisesRegex(ValueError, "creator"):
            self.use_case.execute(
                CreateEventCommand(
                    "Open night",
                    datetime(2026, 9, 1, 19, tzinfo=UTC),
                    " ",
                    "bot:message:42",
                )
            )

        self.assertEqual({}, self.repository.events)

    def test_blank_source_reference_does_not_store_an_event(self) -> None:
        with self.assertRaisesRegex(ValueError, "source"):
            self.use_case.execute(
                CreateEventCommand(
                    "Open night",
                    datetime(2026, 9, 1, 19, tzinfo=UTC),
                    "resident-7",
                    " ",
                )
            )

        self.assertEqual({}, self.repository.events)


if __name__ == "__main__":
    unittest.main()
