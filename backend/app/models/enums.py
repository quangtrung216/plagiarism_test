from enum import Enum


class TopicStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class SubmissionStatus(str, Enum):
    SUBMITTED = "submitted"
    CHECKING = "checking"
    CHECKED = "checked"


class MemberStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
