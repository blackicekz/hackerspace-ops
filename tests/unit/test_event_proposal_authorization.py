import unittest

from src.application.conversational_event_proposal import (
    EventProposalAuthorization,
    ResidentIdentity,
)


class PermissionFacts:
    def __init__(self, permitted: bool) -> None:
        self.permitted = permitted
        self.requested_resident: ResidentIdentity | None = None

    def has_event_proposal_permission(self, resident: ResidentIdentity) -> bool:
        self.requested_resident = resident
        return self.permitted


class EventProposalAuthorizationTest(unittest.TestCase):
    def test_policy_decides_from_permission_fact_for_resident(self) -> None:
        resident = ResidentIdentity("resident-7")
        facts = PermissionFacts(permitted=False)
        policy = EventProposalAuthorization(facts)

        decision = policy.may_propose_event(resident)

        self.assertFalse(decision)
        self.assertEqual(resident, facts.requested_resident)


if __name__ == "__main__":
    unittest.main()
