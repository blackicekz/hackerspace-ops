import sqlite3
import unittest
from typing import Any

from src.adapters.calendar_permissions import (
    GoogleSheetCalendarApproverPermissionFacts,
    GoogleSheetsApiValuesReader,
    PermissionSourceError,
    PostgresCalendarApproverPermissionFacts,
    SqliteCalendarApproverPermissionFacts,
    calendar_approver_ids_from_rows,
)
from src.application.calendar_approval import CalendarApprovalAuthorization
from src.application.conversational_event_proposal import ResidentIdentity


class ValuesReader:
    def __init__(self, values: list[list[Any]]) -> None:
        self.values = values
        self.calls: list[tuple[str, str]] = []

    def read_values(self, spreadsheet_id: str, cell_range: str) -> list[list[Any]]:
        self.calls.append((spreadsheet_id, cell_range))
        return self.values


class FailingValuesReader:
    def read_values(self, spreadsheet_id: str, cell_range: str) -> list[list[Any]]:
        raise OSError("network unavailable")


class FakeGoogleRequest:
    def __init__(self, result: Any) -> None:
        self.result = result

    def execute(self) -> Any:
        return self.result


class FakeGoogleValues:
    def __init__(self, result: Any) -> None:
        self.result = result
        self.arguments: dict[str, str] | None = None

    def get(self, **kwargs: str) -> FakeGoogleRequest:
        self.arguments = kwargs
        return FakeGoogleRequest(self.result)


class FakeGoogleSheets:
    def __init__(self, result: Any) -> None:
        self.values_resource = FakeGoogleValues(result)

    def values(self) -> FakeGoogleValues:
        return self.values_resource


class FakeGoogleService:
    def __init__(self, result: Any) -> None:
        self.sheets_resource = FakeGoogleSheets(result)

    def spreadsheets(self) -> FakeGoogleSheets:
        return self.sheets_resource


class FakePostgresCursor:
    def __init__(self, resident_ids: set[str]) -> None:
        self.resident_ids = resident_ids
        self.result: tuple[int] | None = None
        self.executed: tuple[str, tuple[str, ...] | None] | None = None
        self.closed = False

    def execute(self, statement: str, parameters: tuple[str, ...] | None = None) -> None:
        self.executed = (statement, parameters)
        if statement.startswith("SELECT"):
            self.result = (1,) if parameters and parameters[0] in self.resident_ids else None

    def fetchone(self) -> tuple[int] | None:
        return self.result

    def close(self) -> None:
        self.closed = True


class FakePostgresConnection:
    def __init__(self, resident_ids: set[str]) -> None:
        self.cursor_value = FakePostgresCursor(resident_ids)
        self.commits = 0

    def cursor(self) -> FakePostgresCursor:
        return self.cursor_value

    def commit(self) -> None:
        self.commits += 1


class CalendarApprovalPermissionsTest(unittest.TestCase):
    approver = ResidentIdentity("resident-approver")
    other_resident = ResidentIdentity("resident-other")

    def test_policy_delegates_to_permission_facts(self) -> None:
        connection = sqlite3.connect(":memory:")
        SqliteCalendarApproverPermissionFacts.initialize_schema(connection)
        connection.execute(
            "INSERT INTO calendar_approvers (resident_id) VALUES (?)", (self.approver.value,)
        )
        facts = SqliteCalendarApproverPermissionFacts(connection)

        policy = CalendarApprovalAuthorization(facts)

        self.assertTrue(policy.may_approve_calendar_change(self.approver))
        self.assertFalse(policy.may_approve_calendar_change(self.other_resident))

    def test_google_sheet_reader_accepts_header_and_uses_first_column(self) -> None:
        reader = ValuesReader([["resident_id", "note"], ["resident-approver", "on duty"]])
        facts = GoogleSheetCalendarApproverPermissionFacts(reader, "sheet-1", "Approvers!A:B")

        self.assertTrue(facts.has_calendar_approval_permission(self.approver))
        self.assertFalse(facts.has_calendar_approval_permission(self.other_resident))
        self.assertEqual([("sheet-1", "Approvers!A:B")] * 2, reader.calls)

    def test_google_sheet_source_failure_is_explicit(self) -> None:
        facts = GoogleSheetCalendarApproverPermissionFacts(
            FailingValuesReader(), "sheet-1", "Approvers!A:A"
        )

        with self.assertRaises(PermissionSourceError):
            facts.has_calendar_approval_permission(self.approver)

    def test_google_rows_reject_blank_and_duplicate_ids(self) -> None:
        with self.assertRaisesRegex(ValueError, "blank resident_id"):
            calendar_approver_ids_from_rows([["resident_id"], [""]])
        with self.assertRaisesRegex(ValueError, "duplicates resident_id"):
            calendar_approver_ids_from_rows([["resident_id"], ["resident-1"], ["resident-1"]])

    def test_google_api_reader_translates_values_request(self) -> None:
        service = FakeGoogleService({"values": [["resident_id"], ["resident-approver"]]})
        reader = GoogleSheetsApiValuesReader(service)

        self.assertEqual(
            [["resident_id"], ["resident-approver"]], reader.read_values("sheet-1", "A:A")
        )
        self.assertEqual(
            {"spreadsheetId": "sheet-1", "range": "A:A"},
            service.sheets_resource.values_resource.arguments,
        )

    def test_sqlite_adapter_reads_the_approver_table(self) -> None:
        connection = sqlite3.connect(":memory:")
        SqliteCalendarApproverPermissionFacts.initialize_schema(connection)
        connection.execute(
            "INSERT INTO calendar_approvers (resident_id) VALUES (?)", (self.approver.value,)
        )
        facts = SqliteCalendarApproverPermissionFacts(connection)

        self.assertTrue(facts.has_calendar_approval_permission(self.approver))
        self.assertFalse(facts.has_calendar_approval_permission(self.other_resident))

    def test_postgres_adapter_uses_parameterized_query_and_closes_cursor(self) -> None:
        connection = FakePostgresConnection({self.approver.value})
        facts = PostgresCalendarApproverPermissionFacts(connection)

        self.assertTrue(facts.has_calendar_approval_permission(self.approver))
        self.assertFalse(facts.has_calendar_approval_permission(self.other_resident))
        self.assertTrue(connection.cursor_value.closed)
        executed = connection.cursor_value.executed
        self.assertIsNotNone(executed)
        assert executed is not None
        statement, parameters = executed
        self.assertIn("WHERE resident_id = %s", statement)
        self.assertEqual((self.other_resident.value,), parameters)

    def test_postgres_schema_initialization_commits_and_closes_cursor(self) -> None:
        connection = FakePostgresConnection(set())

        PostgresCalendarApproverPermissionFacts.initialize_schema(connection)

        self.assertEqual(1, connection.commits)
        self.assertTrue(connection.cursor_value.closed)
        self.assertIsNotNone(connection.cursor_value.executed)
        assert connection.cursor_value.executed is not None
        self.assertIn(
            "CREATE TABLE IF NOT EXISTS calendar_approvers", connection.cursor_value.executed[0]
        )


if __name__ == "__main__":
    unittest.main()
