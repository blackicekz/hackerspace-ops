from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Event:
    id: str
    title: str
    starts_at: datetime
    created_by: str
    source_reference: str

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("event title must not be blank")
        if self.starts_at.tzinfo is None or self.starts_at.utcoffset() is None:
            raise ValueError("event start time must include a timezone")
        if not self.created_by.strip():
            raise ValueError("event creator must not be blank")
        if not self.source_reference.strip():
            raise ValueError("event source reference must not be blank")
