from typing import Protocol

from src.application.conversational_event_proposal import ResidentIdentity


class CalendarApproverPermissionFacts(Protocol):
    """Configured facts used by the calendar approval authorization policy."""

    def has_calendar_approval_permission(self, resident: ResidentIdentity) -> bool: ...


class CalendarApprovalAuthorization:
    """Application policy deciding whether a resident may approve calendar changes."""

    def __init__(self, permission_facts: CalendarApproverPermissionFacts) -> None:
        self._permission_facts = permission_facts

    def may_approve_calendar_change(self, resident: ResidentIdentity) -> bool:
        return self._permission_facts.has_calendar_approval_permission(resident)
