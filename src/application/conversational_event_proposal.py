from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from src.application.create_event import CreateEvent, CreateEventCommand


@dataclass(frozen=True)
class ExternalIdentity:
    issuer: str
    subject: str


@dataclass(frozen=True)
class ResidentIdentity:
    value: str


@dataclass(frozen=True)
class ConversationalInput:
    text: str
    external_identity: ExternalIdentity | None
    source_reference: str


@dataclass(frozen=True)
class EventProposal:
    title: str
    starts_at: datetime


@dataclass(frozen=True)
class Irrelevant:
    pass


@dataclass(frozen=True)
class Incomplete:
    missing_fields: tuple[str, ...]


@dataclass(frozen=True)
class Ambiguous:
    ambiguous_fields: tuple[str, ...]


@dataclass(frozen=True)
class Ready:
    proposal: EventProposal


type ProposalExtractionResult = Irrelevant | Incomplete | Ambiguous | Ready


@dataclass(frozen=True)
class UnidentifiedSender:
    pass


@dataclass(frozen=True)
class UnauthorizedResident:
    pass


@dataclass(frozen=True)
class IrrelevantMessage:
    pass


@dataclass(frozen=True)
class IncompleteProposal:
    missing_fields: tuple[str, ...]


@dataclass(frozen=True)
class AmbiguousProposal:
    ambiguous_fields: tuple[str, ...]


@dataclass(frozen=True)
class EventCreated:
    event_id: str


type ConversationalIngestionResult = (
    UnidentifiedSender
    | UnauthorizedResident
    | IrrelevantMessage
    | IncompleteProposal
    | AmbiguousProposal
    | EventCreated
)


class ResidentIdentityResolver(Protocol):
    def resolve(self, identity: ExternalIdentity) -> ResidentIdentity | None: ...


class EventProposalPermissionFacts(Protocol):
    def has_event_proposal_permission(self, resident: ResidentIdentity) -> bool: ...


class EventProposalExtractor(Protocol):
    def extract(self, text: str) -> ProposalExtractionResult: ...


class EventProposalAuthorization:
    """Application policy deciding whether a resident may propose an event."""

    def __init__(self, permission_facts: EventProposalPermissionFacts) -> None:
        self._permission_facts = permission_facts

    def may_propose_event(self, resident: ResidentIdentity) -> bool:
        return self._permission_facts.has_event_proposal_permission(resident)


class IngestConversationalEventProposal:
    def __init__(
        self,
        identity_resolver: ResidentIdentityResolver,
        authorization: EventProposalAuthorization,
        extractor: EventProposalExtractor,
        create_event: CreateEvent,
    ) -> None:
        self._identity_resolver = identity_resolver
        self._authorization = authorization
        self._extractor = extractor
        self._create_event = create_event

    def execute(self, input_data: ConversationalInput) -> ConversationalIngestionResult:
        if input_data.external_identity is None:
            return UnidentifiedSender()

        resident = self._identity_resolver.resolve(input_data.external_identity)
        if resident is None:
            return UnidentifiedSender()
        if not self._authorization.may_propose_event(resident):
            return UnauthorizedResident()

        extraction = self._extractor.extract(input_data.text)
        if isinstance(extraction, Irrelevant):
            return IrrelevantMessage()
        if isinstance(extraction, Incomplete):
            return IncompleteProposal(extraction.missing_fields)
        if isinstance(extraction, Ambiguous):
            return AmbiguousProposal(extraction.ambiguous_fields)

        event_id = self._create_event.execute(
            CreateEventCommand(
                title=extraction.proposal.title,
                starts_at=extraction.proposal.starts_at,
                actor_id=resident.value,
                source_reference=input_data.source_reference,
            )
        )
        return EventCreated(event_id)
