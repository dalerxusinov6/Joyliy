"""ORM Models registry."""

from src.database import Base
from src.models.user import User, UserSearchPreference, AuthSession
from src.models.listing import (
    Listing,
    ListingClassification,
    Favorite,
    NotificationHistory,
    ChannelPostHistory,
    ChannelPublishQueue,
    ChannelPublishSchedule,
    QueueStatus,
)
from src.models.system import SourceMonitorRun, AdminAuditLog
from src.models.ecosystem import (
    ListingPriceHistory,
    RoommateProfile,
    RoommateConnectionRequest,
    ListingReport,
    SavedSearchAlert,
)

__all__ = [
    "Base",
    "User",
    "UserSearchPreference",
    "AuthSession",
    "Listing",
    "ListingClassification",
    "Favorite",
    "NotificationHistory",
    "ChannelPostHistory",
    "ChannelPublishQueue",
    "ChannelPublishSchedule",
    "QueueStatus",
    "SourceMonitorRun",
    "AdminAuditLog",
    "ListingPriceHistory",
    "RoommateProfile",
    "RoommateConnectionRequest",
    "ListingReport",
    "SavedSearchAlert",
]

