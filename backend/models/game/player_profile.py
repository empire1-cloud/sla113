"""
Player Profile Model for Game-specific data
Stores welcome bonuses, daily login rewards, progression, and other game-related data
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId type for Pydantic."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class WelcomeBonusStatus(str):
    """Welcome bonus status constants."""
    NOT_ELIGIBLE = "not_eligible"
    ELIGIBLE_NOT_CLAIMED = "eligible_not_claimed"
    CLAIMED_NOT_WAGERED = "claimed_not_wagered"
    WAGER_IN_PROGRESS = "wager_in_progress"
    WAGER_COMPLETE = "wager_complete"


class PlayerProfileBase(BaseModel):
    """Base player profile fields."""
    user_id: str  # Reference to users collection
    username: str


class PlayerProfileCreate(PlayerProfileBase):
    """Schema for creating a new player profile."""
    pass


class PlayerProfileUpdate(BaseModel):
    """Schema for updating player profile."""
    welcome_bonus_claimed: Optional[bool] = None
    welcome_bonus_amount: Optional[float] = None
    welcome_bonus_used: Optional[float] = None
    welcome_bonus_wagered: Optional[float] = None
    welcome_bonus_claimed_at: Optional[datetime] = None
    first_transaction_date: Optional[datetime] = None
    login_streak: Optional[int] = None
    last_login_date: Optional[datetime] = None
    level: Optional[int] = None
    current_xp: Optional[int] = None
    total_xp: Optional[int] = None
    unlocked_weapons: Optional[List[str]] = None
    unlocked_cosmetics: Optional[Dict[str, List[str]]] = None
    equipped_weapon: Optional[str] = None
    equipped_bullet_trail: Optional[str] = None
    equipped_avatar: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None


class PlayerProfileInDB(PlayerProfileBase):
    """Player profile as stored in database."""
    id: str = Field(alias="_id")

    # Welcome Bonus Fields
    welcome_bonus_claimed: bool = False
    welcome_bonus_amount: float = 0.0
    welcome_bonus_used: float = 0.0
    welcome_bonus_wagered: float = 0.0
    welcome_bonus_claimed_at: Optional[datetime] = None
    first_transaction_date: Optional[datetime] = None

    # Daily Login Rewards
    login_streak: int = 0
    last_login_date: Optional[datetime] = None

    # Player Progression
    level: int = 1
    current_xp: int = 0
    total_xp: int = 0
    unlocked_weapons: List[str] = []
    unlocked_cosmetics: Dict[str, List[str]] = {
        "bullet_trails": [],
        "avatars": [],
        "weapon_skins": []
    }
    equipped_weapon: str = "basic"
    equipped_bullet_trail: str = "default"
    equipped_avatar: str = "default"

    # Player Stats
    stats: Dict[str, Any] = {
        "total_fish_caught": 0,
        "fish_by_type": {},
        "total_damage": 0,
        "accuracy": 0.0,
        "longest_streak": 0,
        "favorite_weapon": "basic",
        "multiplayer_wins": 0,
        "multiplayer_losses": 0
    }

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class PlayerProfileResponse(PlayerProfileBase):
    """Player profile response (public fields)."""
    id: str

    # Welcome Bonus Info
    welcome_bonus_claimed: bool
    welcome_bonus_amount: float
    welcome_bonus_used: float
    welcome_bonus_wagered: float
    welcome_bonus_claimed_at: Optional[datetime] = None
    first_transaction_date: Optional[datetime] = None

    # Daily Login Rewards
    login_streak: int
    last_login_date: Optional[datetime] = None

    # Player Progression
    level: int
    current_xp: int
    total_xp: int
    unlocked_weapons: List[str]
    unlocked_cosmetics: Dict[str, List[str]]
    equipped_weapon: str
    equipped_bullet_trail: str
    equipped_avatar: str

    # Player Stats
    stats: Dict[str, Any]

    # Computed Properties
    welcome_bonus_status: str
    welcome_bonus_remaining_wager: float

    class Config:
        from_attributes = True