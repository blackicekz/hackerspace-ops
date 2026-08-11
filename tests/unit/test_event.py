import unittest
from datetime import UTC, datetime

from src.domain import Event


class EventTest(unittest.TestCase):
    def test_rejects_blank_title(self) -> None:
        with self.assertRaisesRegex(ValueError, "title"):
            Event("event-1", "  ", datetime.now(UTC), "resident-1", "bot:42")

    def test_rejects_start_without_timezone(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone"):
            Event("event-1", "Open night", datetime(2026, 9, 1, 19), "resident-1", "bot:42")


if __name__ == "__main__":
    unittest.main()
