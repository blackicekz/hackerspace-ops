import sqlite3
from collections.abc import Iterable, Sequence
from typing import Any, Protocol

from src.application.calendar_approval import CalendarApproverPermissionFacts
from src.application.conversational_event_proposal import ResidentIdentity

CALENDAR_APPROVERS_TABLE = "calendar_approvers"
CALENDAR_APPROVERS_HEADER = "resident_id"


class PermissionSourceError(RuntimeError):
    """A permission source could not provide a trustworthy answer."""


class GoogleSheetsValuesReader(Protocol):
    def read_values(self, spreadsheet_id: str, cell_range: str) -> Sequence[Sequence[Any]]: ...


class GoogleSheetsApiValuesReader:
    """Adapt a Google Sheets API service resource to the narrow reader port.

    Authentication and construction of the Google API service belong to infrastructure. Keeping
    that setup outside this class prevents Google credential types from crossing the application
    boundary and makes permission parsing testable without network access.
    """

    def __init__(self, service: Any) -> None:
        self._service = service

    def read_values(self, spreadsheet_id: str, cell_range: str) -> Sequence[Sequence[Any]]:
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=cell_range)
                .execute()
            )
        except Exception as exc:  # noqa: BLE001 - provider errors become one adapter error
            raise PermissionSourceError("Google Sheets permission read failed") from exc
        values = result.get("values", [])
        if not isinstance(values, list):
            raise PermissionSourceError("Google Sheets returned an invalid values payload")
        return values


class GoogleSheetCalendarApproverPermissionFacts(CalendarApproverPermissionFacts):
    """Read calendar approver resident IDs from the first column of a Google Sheet range."""

    def __init__(
        self,
        reader: GoogleSheetsValuesReader,
        spreadsheet_id: str,
        cell_range: str,
    ) -> None:
        self._reader = reader
        self._spreadsheet_id = spreadsheet_id
        self._cell_range = cell_range

    def has_calendar_approval_permission(self, resident: ResidentIdentity) -> bool:
        try:
            rows = self._reader.read_values(self._spreadsheet_id, self._cell_range)
            approver_ids = calendar_approver_ids_from_rows(rows)
        except PermissionSourceError:
            raise
        except Exception as exc:  # noqa: BLE001 - source failures must fail closed upstream
            raise PermissionSourceError("Google Sheets permission data is unavailable") from exc
        return resident.value in approver_ids


def calendar_approver_ids_from_rows(rows: Iterable[Sequence[Any]]) -> frozenset[str]:
    """Validate the sheet's first-column contract and return unique resident IDs."""

    materialized = list(rows)
    if not materialized:
        return frozenset()

    first_cell = _cell_as_text(materialized[0], 0)
    data_rows = materialized[1:] if first_cell == CALENDAR_APPROVERS_HEADER else materialized
    approver_ids: set[str] = set()
    for row_number, row in enumerate(
        data_rows, start=2 if first_cell == CALENDAR_APPROVERS_HEADER else 1
    ):
        resident_id = _cell_as_text(row, 0)
        if not resident_id:
            raise ValueError(f"calendar approver row {row_number} has a blank resident_id")
        if resident_id in approver_ids:
            raise ValueError(f"calendar approver row {row_number} duplicates resident_id")
        approver_ids.add(resident_id)
    return frozenset(approver_ids)


def _cell_as_text(row: Sequence[Any], index: int) -> str:
    if len(row) <= index or row[index] is None:
        return ""
    return str(row[index]).strip()


class SqliteCalendarApproverPermissionFacts(CalendarApproverPermissionFacts):
    """Read calendar approvers from a SQLite database connection."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    @staticmethod
    def initialize_schema(connection: sqlite3.Connection) -> None:
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {CALENDAR_APPROVERS_TABLE} (
                resident_id TEXT PRIMARY KEY
            )
            """
        )
        connection.commit()

    def has_calendar_approval_permission(self, resident: ResidentIdentity) -> bool:
        try:
            row = self._connection.execute(
                f"SELECT 1 FROM {CALENDAR_APPROVERS_TABLE} WHERE resident_id = ? LIMIT 1",
                (resident.value,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise PermissionSourceError("SQLite permission read failed") from exc
        return row is not None


class PostgresConnection(Protocol):
    def cursor(self) -> Any: ...

    def commit(self) -> Any: ...


class PostgresCalendarApproverPermissionFacts(CalendarApproverPermissionFacts):
    """Read calendar approvers from a PostgreSQL DB-API connection."""

    def __init__(self, connection: PostgresConnection) -> None:
        self._connection = connection

    @staticmethod
    def initialize_schema(connection: PostgresConnection) -> None:
        cursor = connection.cursor()
        try:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {CALENDAR_APPROVERS_TABLE} (
                    resident_id TEXT PRIMARY KEY
                )
                """
            )
            connection.commit()
        finally:
            cursor.close()

    def has_calendar_approval_permission(self, resident: ResidentIdentity) -> bool:
        cursor = self._connection.cursor()
        try:
            cursor.execute(
                f"SELECT 1 FROM {CALENDAR_APPROVERS_TABLE} WHERE resident_id = %s LIMIT 1",
                (resident.value,),
            )
            return cursor.fetchone() is not None
        except Exception as exc:  # noqa: BLE001 - DB-API implementations vary
            raise PermissionSourceError("PostgreSQL permission read failed") from exc
        finally:
            cursor.close()
