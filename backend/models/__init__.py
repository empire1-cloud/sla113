"""Models package initialization."""

from .user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserWithTeams,
    PasswordReset,
    PasswordResetConfirm,
    ChangePassword,
    OAuthProvider,
    SystemRole,
)

from .team import (
    TeamCreate,
    TeamUpdate,
    TeamInDB,
    TeamResponse,
    TeamWithRole,
    TeamSettings,
    TeamType,
    TeamRole,
    MembershipCreate,
    MembershipInDB,
    TeamMemberResponse,
    UpdateMemberRole,
    InviteCreate,
    InviteInDB,
    InviteResponse,
    AcceptInvite,
)

from .session import (
    SessionCreate,
    SessionInDB,
    SessionResponse,
)

from .audit import (
    AuditLogCreate,
    AuditLogInDB,
    AuditLogResponse,
    AuditLogQuery,
    AuditAction,
)

from .resources import (
    PipelineStep,
    PipelineCreate,
    PipelineUpdate,
    PipelineInDB,
    PipelineResponse,
    ExecutionLogCreate,
    ExecutionLogInDB,
    ExecutionLogResponse,
    ExecutionLogQuery,
    ExecutionStatus,
)

from .auth import (
    TokenPair,
    TokenRefresh,
    TokenResponse,
    AuthResponse,
)

from .soulfire import (
    SoulfirePayload,
    SoulfirePayloadLegacy,
    TrackMetadata,
    DOPEAudioBlueprint,
    RhythmGroove,
    TextureDSP,
    MasterBusDSP,
    MIDISequence,
    LyricLine,
    EmotionalTag,
    convert_legacy_to_v2,
)

__all__ = [
    # User
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserWithTeams",
    "PasswordReset",
    "PasswordResetConfirm",
    "ChangePassword",
    "OAuthProvider",
    "SystemRole",
    
    # Team
    "TeamCreate",
    "TeamUpdate",
    "TeamInDB",
    "TeamResponse",
    "TeamWithRole",
    "TeamSettings",
    "TeamType",
    "TeamRole",
    "MembershipCreate",
    "MembershipInDB",
    "TeamMemberResponse",
    "UpdateMemberRole",
    "InviteCreate",
    "InviteInDB",
    "InviteResponse",
    "AcceptInvite",
    
    # Session
    "SessionCreate",
    "SessionInDB",
    "SessionResponse",
    
    # Audit
    "AuditLogCreate",
    "AuditLogInDB",
    "AuditLogResponse",
    "AuditLogQuery",
    "AuditAction",
    
    # Resources
    "PipelineStep",
    "PipelineCreate",
    "PipelineUpdate",
    "PipelineInDB",
    "PipelineResponse",
    "ExecutionLogCreate",
    "ExecutionLogInDB",
    "ExecutionLogResponse",
    "ExecutionLogQuery",
    "ExecutionStatus",
    
    # Auth
    "TokenPair",
    "TokenRefresh",
    "TokenResponse",
    "AuthResponse",
    
    # Soulfire
    "SoulfirePayload",
    "SoulfirePayloadLegacy",
    "TrackMetadata",
    "DOPEAudioBlueprint",
    "RhythmGroove",
    "TextureDSP",
    "MasterBusDSP",
    "MIDISequence",
    "LyricLine",
    "EmotionalTag",
    "convert_legacy_to_v2",
]
