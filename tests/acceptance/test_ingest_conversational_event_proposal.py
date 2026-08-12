import unittest
from datetime import UTC, datetime

from src.adapters.in_memory import InMemoryEventRepository
from src.application import CreateEvent
from src.application.conversational_event_proposal import (
    Ambiguous,
    AmbiguousProposal,
    ConversationalInput,
    EventCreated,
    EventProposal,
    EventProposalAuthorization,
    ExternalIdentity,
    Incomplete,
    IncompleteProposal,
    IngestConversationalEventProposal,
    Irrelevant,
    IrrelevantMessage,
    Ready,
    ResidentIdentity,
    UnauthorizedResident,
    UnidentifiedSender,
)


class StubIdentityResolver:
    def __init__(self, resident: ResidentIdentity | None) -> None:
        self.resident = resident
        self.calls = 0

    def resolve(self, identity: ExternalIdentity) -> ResidentIdentity | None:
        self.calls += 1
        return self.resident


class StubPermissionFacts:
    def __init__(self, permitted: bool) -> None:
        self.permitted = permitted
        self.calls = 0

    def has_event_proposal_permission(self, resident: ResidentIdentity) -> bool:
        self.calls += 1
        return self.permitted


class StubExtractor:
    def __init__(self, result: Irrelevant | Incomplete | Ambiguous | Ready) -> None:
        self.result = result
        self.calls = 0

    def extract(self, text: str) -> Irrelevant | Incomplete | Ambiguous | Ready:
        self.calls += 1
        return self.result


class CountingIdentifierGenerator:
    def __init__(self) -> None:
        self.calls = 0

    def new_id(self) -> str:
        self.calls += 1
        return "event-123"


class ConversationalEventProposalAcceptanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryEventRepository()
        self.identifiers = CountingIdentifierGenerator()
        self.resolver = StubIdentityResolver(ResidentIdentity("resident-7"))
        self.permission_facts = StubPermissionFacts(True)
        self.extractor = StubExtractor(Irrelevant())
        self.use_case = IngestConversationalEventProposal(
            identity_resolver=self.resolver,
            authorization=EventProposalAuthorization(self.permission_facts),
            extractor=self.extractor,
            create_event=CreateEvent(self.repository, self.identifiers),
        )

    def input(self, identity: ExternalIdentity | None = None) -> ConversationalInput:
        return ConversationalInput(
            text="Open night this Friday at 19:00",
            external_identity=identity,
            source_reference="conversation:message:42",
        )

    def test_missing_external_identity_is_unidentified_without_processing(self) -> None:
        result = self.use_case.execute(self.input())

        self.assertEqual(UnidentifiedSender(), result)
        self.assertEqual(0, self.resolver.calls)
        self.assertEqual(0, self.permission_facts.calls)
        self.assertEqual(0, self.extractor.calls)
        self.assert_no_event_created()

    def test_unmapped_external_identity_is_unidentified_without_authorization(self) -> None:
        self.resolver.resident = None

        result = self.use_case.execute(self.input(ExternalIdentity("chat", "user-42")))

        self.assertEqual(UnidentifiedSender(), result)
        self.assertEqual(1, self.resolver.calls)
        self.assertEqual(0, self.permission_facts.calls)
        self.assertEqual(0, self.extractor.calls)
        self.assert_no_event_created()

    def test_resident_without_permission_is_unauthorized_without_extraction(self) -> None:
        self.permission_facts.permitted = False

        result = self.use_case.execute(self.input(ExternalIdentity("chat", "user-42")))

        self.assertEqual(UnauthorizedResident(), result)
        self.assertEqual(1, self.permission_facts.calls)
        self.assertEqual(0, self.extractor.calls)
        self.assert_no_event_created()

    def test_irrelevant_message_does_not_create_event(self) -> None:
        result = self.use_case.execute(self.input(ExternalIdentity("chat", "user-42")))

        self.assertEqual(IrrelevantMessage(), result)
        self.assertEqual(1, self.extractor.calls)
        self.assert_no_event_created()

    def test_incomplete_proposal_returns_missing_fields_without_creating_event(self) -> None:
        self.extractor.result = Incomplete(("starts_at",))

        result = self.use_case.execute(self.input(ExternalIdentity("chat", "user-42")))

        self.assertEqual(IncompleteProposal(("starts_at",)), result)
        self.assert_no_event_created()

    def test_ambiguous_proposal_returns_ambiguous_fields_without_creating_event(self) -> None:
        self.extractor.result = Ambiguous(("starts_at",))

        result = self.use_case.execute(self.input(ExternalIdentity("chat", "user-42")))

        self.assertEqual(AmbiguousProposal(("starts_at",)), result)
        self.assert_no_event_created()

    def test_ready_proposal_invokes_create_event_once_and_returns_identifier(self) -> None:
        self.extractor.result = Ready(
            EventProposal("Open night", datetime(2026, 9, 4, 19, tzinfo=UTC))
        )

        result = self.use_case.execute(self.input(ExternalIdentity("chat", "user-42")))

        self.assertEqual(EventCreated("event-123"), result)
        self.assertEqual(1, self.identifiers.calls)
        self.assertEqual(1, len(self.repository.events))

    def test_created_event_retains_proposal_resident_and_provenance(self) -> None:
        starts_at = datetime(2026, 9, 4, 19, tzinfo=UTC)
        self.extractor.result = Ready(EventProposal("Open night", starts_at))

        self.use_case.execute(self.input(ExternalIdentity("chat", "external-99")))

        event = self.repository.get("event-123")
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual("Open night", event.title)
        self.assertEqual(starts_at, event.starts_at)
        self.assertEqual("resident-7", event.created_by)
        self.assertEqual("conversation:message:42", event.source_reference)

    def assert_no_event_created(self) -> None:
        self.assertEqual(0, self.identifiers.calls)
        self.assertEqual({}, self.repository.events)


if __name__ == "__main__":
    unittest.main()
