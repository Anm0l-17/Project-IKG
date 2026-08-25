from enum import Enum


class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class GroupingStatus(str, Enum):
    UNGROUPED = "UNGROUPED"
    GROUPED = "GROUPED"


class DomainCategory(str, Enum):
    CURRENT_AFFAIRS = "Current Affairs"
    PARLIAMENT = "Parliament"
    ECONOMICS = "Economics"
    TRADE = "Trade"
    DEFENCE = "Defence"
    GEOPOLITICS = "Geopolitics"


class EvidenceType(str, Enum):
    EVENT_EXISTENCE = "EVENT_EXISTENCE"
    STORY_GROUPING = "STORY_GROUPING"
    RELATIONSHIP_SUPPORT = "RELATIONSHIP_SUPPORT"
    CLAIM_PROVENANCE = "CLAIM_PROVENANCE"


class EventLifecycleState(str, Enum):
    DISCOVERED = "DISCOVERED"
    NORMALISED = "NORMALISED"
    MATCHING = "MATCHING"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    ACTIVE = "ACTIVE"
    HISTORICAL = "HISTORICAL"
    ARCHIVED = "ARCHIVED"
    DEPRECATED = "DEPRECATED"
