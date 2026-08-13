"""
Event Service for Managing Dynamic and Limited-Time Events
Handles scheduling, triggering, and processing of game events
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
import asyncio
import random
import json
from bson import ObjectId

from database import get_database
from models.game.event_system import (
    DynamicEventType, DynamicEventBase, DynamicEventCreate, DynamicEventUpdate,
    LimitedTimeEventType, LimitedTimeEventBase, LimitedTimeEventCreate, LimitedTimeEventUpdate,
    ActiveDynamicEvent, ActiveLimitedTimeEvent, EventParticipation, EventAnnouncement,
    EventStatus
)
from models.game.player_profile import PlayerProfileInDB as PlayerProfileModel
from services.auth_service import AuthError


class EventService:
    """Service for managing game events."""

    def __init__(self):
        self.db = get_database()
        self.dynamic_events_collection = self.db.dynamic_events
        self.limited_time_events_collection = self.db.limited_time_events
        self.active_dynamic_events_collection = self.db.active_dynamic_events
        self.active_limited_time_events_collection = self.db.active_limited_time_events
        self.event_participation_collection = self.db.event_participation
        self.event_announcements_collection = self.db.event_announcements
        self.player_profiles_collection = self.db.player_profiles
        # Archive collections for historical events
        self.archived_dynamic_events_collection = self.db.archived_dynamic_events
        self.archived_limited_time_events_collection = self.db.archived_limited_time_events

    # ==================== DYNAMIC EVENT METHODS ====================

    async def initialize_default_events(self):
        """Initialize default dynamic and limited-time events if they don't exist."""
        # Initialize dynamic events
        for event_data in self._get_default_dynamic_events():
            existing = await self.dynamic_events_collection.find_one({
                "event_type": event_data["event_type"]
            })
            if not existing:
                await self.dynamic_events_collection.insert_one(event_data)

        # Initialize limited-time events
        for event_data in self._get_default_limited_time_events():
            existing = await self.limited_time_events_collection.find_one({
                "event_type": event_data["event_type"]
            })
            if not existing:
                # Set up timing for recurring events
                event_data = self._schedule_event_timing(event_data)
                await self.limited_time_events_collection.insert_one(event_data)

    def _get_default_dynamic_events(self) -> List[Dict]:
        """Get default dynamic event configurations."""
        from models.game.event_system import DEFAULT_DYNAMIC_EVENTS
        return DEFAULT_DYNAMIC_EVENTS

    def _get_default_limited_time_events(self) -> List[Dict]:
        """Get default limited-time event configurations."""
        from models.game.event_system import DEFAULT_LIMITED_TIME_EVENTS
        return DEFAULT_LIMITED_TIME_EVENTS

    def _schedule_event_timing(self, event_data: Dict) -> Dict:
        """Schedule timing for recurring events based on pattern."""
        now = datetime.now(timezone.utc)
        pattern = event_data.get("recurrence_pattern")

        if pattern == "weekly_friday_sunday":
            # Next Friday-Sunday weekend
            days_ahead = 4 - now.weekday()  # Friday is weekday 4
            if days_ahead <= 0:  # Today is Friday or later
                days_ahead += 7
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
            end_date = start_date + timedelta(days=2)  # Friday to Sunday
        elif pattern == "biweekly_48h":
            # Every 2 weeks for 48 hours
            start_date = now + timedelta(weeks=2)
            end_date = start_date + timedelta(hours=48)
        else:
            # Default to weekly
            start_date = now + timedelta(days=7)
            end_date = start_date + timedelta(hours=24)

        event_data["start_time"] = start_date
        event_data["end_time"] = end_date
        return event_data

    async def get_dynamic_event_templates(self) -> List[Dict]:
        """Get all dynamic event templates."""
        cursor = self.dynamic_events_collection.find({})
        events = await cursor.to_list(length=None)
        return events

    async def get_limited_time_event_templates(self) -> List[Dict]:
        """Get all limited-time event templates."""
        cursor = self.limited_time_events_collection.find({})
        events = await cursor.to_list(length=None)
        return events

    async def create_dynamic_event(self, event_data: DynamicEventCreate) -> str:
        """Create a new dynamic event template."""
        event_dict = event_data.dict()
        result = await self.dynamic_events_collection.insert_one(event_dict)
        return str(result.inserted_id)

    async def create_limited_time_event(self, event_data: LimitedTimeEventCreate) -> str:
        """Create a new limited-time event template."""
        event_dict = event_data.dict()
        # Schedule timing if not already set
        if not event_dict.get("start_time") or not event_dict.get("end_time"):
            event_dict = self._schedule_event_timing(event_dict)
        result = await self.limited_time_events_collection.insert_one(event_dict)
        return str(result.inserted_id)

    # ==================== EVENT TRIGGERING AND MANAGEMENT ====================

    async def check_and_trigger_events(self):
        """Check for events that should be started or ended. Call this periodically."""
        await self._check_dynamic_events()
        await self._check_limited_time_events()

    async def _check_dynamic_events(self):
        """Check and manage dynamic events."""
        now = datetime.now(timezone.utc)

        # Get currently active dynamic events
        active_events = await self.active_dynamic_events_collection.find({}).to_list(length=None)

        # Check if any active events should end
        for event in active_events:
            ends_at = event["ends_at"]
            if ends_at.tzinfo is None:
                ends_at = ends_at.replace(tzinfo=timezone.utc)

            if now >= ends_at:
                await self._end_dynamic_event(event["_id"])

        # Check if we can start new dynamic events
        # Only allow a limited number of concurrent events
        max_concurrent = 2
        if len(active_events) >= max_concurrent:
            return

        # Get event templates
        templates = await self.get_dynamic_event_templates()
        if not templates:
            return

        # Check cooldowns for each template
        available_events = []
        for template in templates:
            # Check if this event type is already active
            active_same_type = any(
                e["event_type"] == template["event_type"] for e in active_events
            )
            if active_same_type:
                continue

            # Check cooldown - when was this type last active?
            last_active = await self.active_dynamic_events_collection.find_one(
                {"event_type": template["event_type"]},
                sort=[("ended_at", -1)]  # Assuming we track ended_at
            )

            # For simplicity, we'll use a random chance based on cooldown
            # In production, you'd want more precise tracking
            cooldown_minutes = template.get("cooldown_minutes", 60)
            if random.random() < (1 / (cooldown_minutes / 5)):  # Check every 5 minutes
                # Check if we have enough eligible players
                eligible_players = await self._count_eligible_players(
                    template.get("min_player_level", 1)
                )
                if eligible_players >= 1:  # At least one player can participate
                    available_events.append(template)

        # Start a random available event
        if available_events:
            selected_event = random.choice(available_events)
            await self._start_dynamic_event(selected_event)

    async def _check_limited_time_events(self):
        """Check and manage limited-time events."""
        now = datetime.now(timezone.utc)

        # Get currently active limited-time events
        active_events = await self.active_limited_time_events_collection.find({}).to_list(length=None)

        # Check if any active events should end
        for event in active_events:
            ends_at = event["ends_at"]
            if ends_at.tzinfo is None:
                ends_at = ends_at.replace(tzinfo=timezone.utc)

            if now >= ends_at:
                await self._end_limited_time_event(event["_id"])

        # Check for events that should start
        templates = await self.get_limited_time_event_templates()
        active_event_types = {e["event_type"] for e in active_events}

        for template in templates:
            # Skip if already active
            if template["event_type"] in active_event_types:
                continue

            start_time = template["start_time"]
            end_time = template["end_time"]

            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=timezone.utc)

            # Check if it's time to start
            if start_time <= now <= end_time:
                await self._start_limited_time_event(template)

    async def _start_dynamic_event(self, event_template: Dict):
        """Start a dynamic event based on template."""
        now = datetime.now(timezone.utc)
        duration = timedelta(minutes=event_template["duration_minutes"])

        active_event = {
            "event_type": event_template["event_type"],
            "name": event_template["name"],
            "description": event_template["description"],
            "started_at": now,
            "ends_at": now + duration,
            "multiplier": event_template["multiplier"],
            "special_rewards": event_template["special_rewards"],
            "participating_players": [],
            "announcements_sent": []
        }

        result = await self.active_dynamic_events_collection.insert_one(active_event)
        event_id = str(result.inserted_id)

        # Send start announcement
        await self._send_event_announcement(
            event_template["event_type"],
            "start",
            f"🚨 {event_template['name']} has begun! {event_template['description']}"
        )

        return event_id

    async def _end_dynamic_event(self, event_id: str):
        """End a dynamic event."""
        event = await self.active_dynamic_events_collection.find_one({"_id": ObjectId(event_id)})
        if not event:
            return

        now = datetime.now(timezone.utc)
        ended_at = now

        # Update the event with end time
        await self.active_dynamic_events_collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": {"ended_at": ended_at}}
        )

        # Archive the event before removing from active
        await self.archived_dynamic_events_collection.insert_one(event)

        # Remove from active events
        await self.active_dynamic_events_collection.delete_one({"_id": ObjectId(event_id)})

        # Send end announcement
        await self._send_event_announcement(
            event["event_type"],
            "end",
            f"🏁 {event['name']} has ended! Thanks for participating!"
        )

        # Process any ongoing participation rewards
        await self._process_event_completion(event_id, is_dynamic=True)

    async def _start_limited_time_event(self, event_template: Dict):
        """Start a limited-time event based on template."""
        # Use the scheduled times from the template
        start_time = event_template["start_time"]
        end_time = event_template["end_time"]

        active_event = {
            "event_type": event_template["event_type"],
            "name": event_template["name"],
            "description": event_template["description"],
            "started_at": start_time,
            "ends_at": end_time,
            "xp_multiplier": event_template["xp_multiplier"],
            "credit_multiplier": event_template["credit_multiplier"],
            "special_rewards": event_template["special_rewards"],
            "participating_players": [],
            "leaderboard": [],
            "total_participants": 0,
            "total_prize_awarded": 0,
            "recurrence_pattern": event_template.get("recurrence_pattern")
        }

        result = await self.active_limited_time_events_collection.insert_one(active_event)
        event_id = str(result.inserted_id)

        # Send start announcement
        await self._send_event_announcement(
            event_template["event_type"],
            "start",
            f"🎉 {event_template['name']} is now live! {event_template['description']}"
        )

        return event_id

    async def _end_limited_time_event(self, event_id: str):
        """End a limited-time event."""
        event = await self.active_limited_time_events_collection.find_one({"_id": ObjectId(event_id)})
        if not event:
            return

        now = datetime.now(timezone.utc)
        ended_at = now

        # Update the event with end time
        await self.active_limited_time_events_collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": {"ended_at": ended_at}}
        )

        # Archive the event before removing from active
        await self.archived_limited_time_events_collection.insert_one(event)

        # Move to completed events or archive
        await self.active_limited_time_events_collection.delete_one({"_id": ObjectId(event_id)})

        # Send end announcement
        await self._send_event_announcement(
            event["event_type"],
            "end",
            f"🏁 {event['name']} has ended! Check the leaderboard for winners!"
        )

        # Process final rewards and leaderboard
        await self._process_event_completion(event_id, is_dynamic=False)

        # If recurring, reschedule
        if event.get("recurrence_pattern"):
            # Get the template and reschedule it
            template = await self.limited_time_events_collection.find_one({
                "event_type": event["event_type"]
            })
            if template:
                updated_template = self._schedule_event_timing(dict(template))
                await self.limited_time_events_collection.update_one(
                    {"_id": ObjectId(template["_id"])},
                    {"$set": {
                        "start_time": updated_template["start_time"],
                        "end_time": updated_template["end_time"]
                    }}
                )

    async def _send_event_announcement(self, event_type: str, trigger: str, message: str):
        """Send an event announcement to all connected clients."""
        # Store the announcement in database for history
        announcement = {
            "event_type": event_type,
            "trigger": trigger,
            "message": message,
            "created_at": datetime.now(timezone.utc),
            "priority": 1,
            "duration_seconds": 10
        }
        await self.event_announcements_collection.insert_one(announcement)

        # In a real implementation, this would broadcast to WebSocket connections
        # For now, we'll just log it
        print(f"EVENT ANNOUNCEMENT [{event_type}:{trigger}]: {message}")

    async def _count_eligible_players(self, min_level: int) -> int:
        """Count players eligible for an event based on minimum level."""
        # Count players with player profiles at or above the minimum level
        count = await self.player_profiles_collection.count_documents({
            "level": {"$gte": min_level}
        })
        return count

    async def join_event(self, user_id: str, event_type: str) -> bool:
        """Allow a player to join an active event."""
        # Check if player has a profile
        player_profile = await self.player_profiles_collection.find_one({"user_id": user_id})
        if not player_profile:
            raise AuthError("Player profile not found", 404)

        # Check if there's an active event of this type
        if event_type in [DynamicEventType.BOSS_RUSH, DynamicEventType.TREASURE_HUNT, DynamicEventType.MULTIPLIER_MADNESS]:
            # Dynamic event
            active_event = await self.active_dynamic_events_collection.find_one({
                "event_type": event_type,
                "status": EventStatus.ACTIVE
            })

            if not active_event:
                return False

            # Check if already participating
            existing = await self.event_participation_collection.find_one({
                "user_id": user_id,
                "event_type": event_type,
                "completed": False
            })
            if existing:
                return True  # Already participating

            # Check player level requirement
            min_level = active_event.get("min_player_level", 1)
            if player_profile["level"] < min_level:
                return False

            # Add participation
            participation = {
                "user_id": user_id,
                "event_type": event_type,
                "event_id": str(active_event["_id"]),
                "joined_at": datetime.now(timezone.utc),
                "rewards_earned": {},
                "xp_earned": 0,
                "credits_earned": 0,
                "completed": False
            }

            await self.event_participation_collection.insert_one(participation)

            # Add player to active event participants
            await self.active_dynamic_events_collection.update_one(
                {"_id": active_event["_id"]},
                {"$addToSet": {"participating_players": user_id}}
            )

            return True

        else:
            # Limited-time event
            active_event = await self.active_limited_time_events_collection.find_one({
                "event_type": event_type,
                "status": EventStatus.ACTIVE
            })

            if not active_event:
                return False

            # Check if already participating
            existing = await self.event_participation_collection.find_one({
                "user_id": user_id,
                "event_type": event_type,
                "completed": False
            })
            if existing:
                return True  # Already participating

            # Check player level requirement
            min_level = active_event.get("min_player_level", 1)
            if player_profile["level"] < min_level:
                return False

            # Check entry fee
            entry_fee = active_event.get("entry_fee", 0)
            if entry_fee > 0:
                # TODO: Check if player has enough credits and deduct
                pass

            # Add participation
            participation = {
                "user_id": user_id,
                "event_type": event_type,
                "event_id": str(active_event["_id"]),
                "joined_at": datetime.now(timezone.utc),
                "rewards_earned": {},
                "xp_earned": 0,
                "credits_earned": 0,
                "completed": False
            }

            await self.event_participation_collection.insert_one(participation)

            # Update participant count
            await self.active_limited_time_events_collection.update_one(
                {"_id": active_event["_id"]},
                {"$inc": {"total_participants": 1}, "$addToSet": {"participating_players": user_id}}
            )

            return True

    async def award_event_rewards(self, user_id: str, event_type: str,
                                xp_amount: int = 0, credit_amount: int = 0,
                                rewards: Optional[Dict[str, int]] = None):
        """Award rewards to a player for participating in an event."""
        if rewards is None:
            rewards = {}

        # Find active participation
        participation = await self.event_participation_collection.find_one({
            "user_id": user_id,
            "event_type": event_type,
            "completed": False
        })

        if not participation:
            return False

        # Update participation with rewards
        update_data = {
            "$inc": {
                "xp_earned": xp_amount,
                "credits_earned": credit_amount
            }
        }

        # Add individual rewards
        for reward_type, amount in rewards.items():
            update_data["$inc"][f"rewards_earned.{reward_type}"] = amount

        await self.event_participation_collection.update_one(
            {"_id": participation["_id"]},
            update_data
        )

        # Also update player's main stats
        if xp_amount > 0 or credit_amount > 0 or rewards:
            await self.player_profiles_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "total_xp": xp_amount,
                        "stats.total_fish_caught": credit_amount // 10  # Rough conversion
                    }
                }
            )

        return True

    async def end_player_event_participation(self, user_id: str, event_type: str):
        """Mark a player's participation in an event as complete."""
        result = await self.event_participation_collection.update_one(
            {
                "user_id": user_id,
                "event_type": event_type,
                "completed": False
            },
            {
                "$set": {
                    "completed": True,
                    "completed_at": datetime.now(timezone.utc)
                }
            }
        )

        # Remove from active participants if it was a dynamic event
        if event_type in [DynamicEventType.BOSS_RUSH, DynamicEventType.TREASURE_HUNT, DynamicEventType.MULTIPLIER_MADNESS]:
            active_event = await self.active_dynamic_events_collection.find_one({
                "event_type": event_type
            })
            if active_event:
                await self.active_dynamic_events_collection.update_one(
                    {"_id": active_event["_id"]},
                    {"$pull": {"participating_players": user_id}}
                )

        elif event_type in [LimitedTimeEventType.DOUBLE_PAYOUT_WEEKEND, LimitedTimeEventType.JACKPOT_FRENZY]:
            active_event = await self.active_limited_time_events_collection.find_one({
                "event_type": event_type
            })
            if active_event:
                await self.active_limited_time_events_collection.update_one(
                    {"_id": active_event["_id"]},
                    {"$pull": {"participating_players": user_id}}
                )

        return result.modified_count > 0

    async def get_active_events(self) -> Dict[str, List[Dict]]:
        """Get currently active events."""
        # Get active dynamic events
        dynamic_cursor = self.active_dynamic_events_collection.find({})
        dynamic_events = await dynamic_cursor.to_list(length=None)

        # Get active limited-time events
        limited_cursor = self.active_limited_time_events_collection.find({})
        limited_events = await limited_cursor.to_list(length=None)

        return {
            "dynamic_events": dynamic_events,
            "limited_time_events": limited_events
        }

    async def get_historical_events(self, limit: int = 50) -> Dict[str, List[Dict]]:
        """Get historical (completed) events."""
        # Get historical dynamic events
        dynamic_cursor = self.archived_dynamic_events_collection.find({}).sort(
            "ended_at", -1
        ).limit(limit)
        dynamic_events = await dynamic_cursor.to_list(length=None)

        # Get historical limited-time events
        limited_cursor = self.archived_limited_time_events_collection.find({}).sort(
            "ended_at", -1
        ).limit(limit)
        limited_events = await limited_cursor.to_list(length=None)

        return {
            "dynamic_events": dynamic_events,
            "limited_time_events": limited_events
        }

    async def get_upcoming_events(self) -> Dict[str, List[Dict]]:
        """Get upcoming events (scheduled but not yet active)."""
        now = datetime.now(timezone.utc)

        # Get upcoming dynamic events (none, as dynamic events are triggered automatically)
        # For now, we'll return empty for dynamic events as they're trigger-based
        upcoming_dynamic = []

        # Get upcoming limited-time events
        upcoming_cursor = self.limited_time_events_collection.find({
            "start_time": {"$gt": now}
        }).sort("start_time", 1)
        upcoming_limited = await upcoming_cursor.to_list(length=None)

        return {
            "dynamic_events": upcoming_dynamic,
            "limited_time_events": upcoming_limited
        }

    async def get_event_leaderboard(self, event_type: str, event_id: str = None) -> List[Dict]:
        """Get leaderboard for a specific event or event type."""
        # If event_id is provided, get leaderboard for that specific event
        if event_id:
            # Get participations for the specific event, ordered by achievement
            participations = await self.event_participation_collection.find({
                "event_type": event_type,
                "event_id": event_id,
                "completed": True
            }).sort([
                ("credits_earned", -1),
                ("xp_earned", -1)
            ]).to_list(length=None)

            leaderboard = []
            for i, participation in enumerate(participations):
                leaderboard.append({
                    "rank": i + 1,
                    "user_id": participation["user_id"],
                    "credits_earned": participation.get("credits_earned", 0),
                    "xp_earned": participation.get("xp_earned", 0),
                    "rewards_earned": participation.get("rewards_earned", {}),
                    "joined_at": participation.get("joined_at"),
                    "completed_at": participation.get("completed_at")
                })

            return leaderboard
        else:
            # Get leaderboard for the most recent completed event of this type
            # First, find the most recent completed event
            recent_event = None
            if event_type in [DynamicEventType.BOSS_RUSH, DynamicEventType.TREASURE_HUNT, DynamicEventType.MULTIPLIER_MADNESS]:
                recent_event = await self.archived_dynamic_events_collection.find_one(
                    {"event_type": event_type},
                    sort=[("ended_at", -1)]
                )
            else:
                recent_event = await self.archived_limited_time_events_collection.find_one(
                    {"event_type": event_type},
                    sort=[("ended_at", -1)]
                )

            if not recent_event:
                return []

            # Get participations for that event
            return await self.get_event_leaderboard(event_type, str(recent_event["_id"]))

    async def get_event_participation_status(self, user_id: str) -> List[Dict]:
        """Get a player's current event participation status."""
        participations = await self.event_participation_collection.find({
            "user_id": user_id,
            "completed": False
        }).to_list(length=None)

        # Enrich with event details
        enriched = []
        for participation in participations:
            event_type = participation["event_type"]
            event_id = participation["event_id"]

            # Get event details
            if event_type in [DynamicEventType.BOSS_RUSH, DynamicEventType.TREASURE_HUNT, DynamicEventType.MULTIPLIER_MADNESS]:
                event = await self.active_dynamic_events_collection.find_one({"_id": ObjectId(event_id)})
            else:
                event = await self.active_limited_time_events_collection.find_one({"_id": ObjectId(event_id)})

            if event:
                enriched.append({
                    "participation_id": str(participation["_id"]),
                    "event_type": event_type,
                    "event_name": event.get("name", "Unknown Event"),
                    "joined_at": participation["joined_at"],
                    "xp_earned": participation.get("xp_earned", 0),
                    "credits_earned": participation.get("credits_earned", 0),
                    "rewards_earned": participation.get("rewards_earned", {}),
                    "time_remaining": self._get_time_remaining(event.get("ends_at"))
                })

        return enriched

    def _get_time_remaining(self, ends_at: Optional[datetime]) -> int:
        """Get seconds remaining until event ends."""
        if not ends_at:
            return 0

        if ends_at.tzinfo is None:
            ends_at = ends_at.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        delta = ends_at - now
        return max(0, int(delta.total_seconds()))

    async def _process_event_completion(self, event_id: str, is_dynamic: bool):
        """Process rewards and cleanup when an event ends."""
        if is_dynamic:
            event = await self.active_dynamic_events_collection.find_one({"_id": ObjectId(event_id)})
            event_type = event["event_type"] if event else "unknown"
        else:
            event = await self.active_limited_time_events_collection.find_one({"_id": ObjectId(event_id)})
            event_type = event["event_type"] if event else "unknown"

        # Get all participations for this event
        participations = await self.event_participation_collection.find({
            "event_type": event_type,
            "event_id": event_id,
            "completed": True
        }).to_list(length=None)

        # Award participation bonuses (everyone gets something for participating)
        for participation in participations:
            user_id = participation["user_id"]
            # Small participation bonus
            await self.award_event_rewards(
                user_id,
                event_type,
                xp_amount=10,
                credit_amount=5
            )

        # For limited-time events with leaderboards, award top performers
        if not is_dynamic and event and event.get("leaderboard_enabled"):
            # Special handling for Jackpot Frenzy tournament
            if event_type == LimitedTimeEventType.JACKPOT_FRENZY:
                await self._process_jackpot_frenzy_completion(event, participations)
            # Standard leaderboard for other events (Double Payout Weekend, etc.)
            else:
                await self._process_standard_leaderboard_completion(event, participations)

    async def _process_jackpot_frenzy_completion(self, event: Dict, participations: List[Dict]):
        """Process completion of Jackpot Frenzy tournament with progressive prize pool."""
        # Calculate total prize pool from entry fees
        entry_fee = event.get("entry_fee", 100)
        total_participants = len(participations)
        prize_pool = entry_fee * total_participants

        # Update the event's total prize awarded
        await self.active_limited_time_events_collection.update_one(
            {"_id": ObjectId(event["_id"])},
            {"$set": {"total_prize_awarded": prize_pool}}
        )

        # Sort by credits earned (primary) and XP earned (secondary) for Jackpot Frenzy
        sorted_participants = sorted(
            participations,
            key=lambda p: (p.get("credits_earned", 0), p.get("xp_earned", 0)),
            reverse=True
        )

        # Award prizes: 50% to 1st, 30% to 2nd, 20% to 3rd
        if len(sorted_participants) >= 1:
            first_place = int(prize_pool * 0.5)
            await self.award_event_rewards(
                sorted_participants[0]["user_id"],
                event["event_type"],
                credit_amount=first_place
            )
            # Update leaderboard position
            await self.event_participation_collection.update_one(
                {"_id": sorted_participants[0]["_id"]},
                {"$set": {"leaderboard_position": 1, "credits_earned": sorted_participants[0].get("credits_earned", 0) + first_place}}
            )

        if len(sorted_participants) >= 2:
            second_place = int(prize_pool * 0.3)
            await self.award_event_rewards(
                sorted_participants[1]["user_id"],
                event["event_type"],
                credit_amount=second_place
            )
            # Update leaderboard position
            await self.event_participation_collection.update_one(
                {"_id": sorted_participants[1]["_id"]},
                {"$set": {"leaderboard_position": 2, "credits_earned": sorted_participants[1].get("credits_earned", 0) + second_place}}
            )

        if len(sorted_participants) >= 3:
            third_place = int(prize_pool * 0.2)
            await self.award_event_rewards(
                sorted_participants[2]["user_id"],
                event["event_type"],
                credit_amount=third_place
            )
            # Update leaderboard position
            await self.event_participation_collection.update_one(
                {"_id": sorted_participants[2]["_id"]},
                {"$set": {"leaderboard_position": 3, "credits_earned": sorted_participants[2].get("credits_earned", 0) + third_place}}
            )

        # Award special rewards to top 3
        special_rewards = event.get("special_rewards", ["trophy_avatar", "exclusive_weapon_skin", "jackpot_ticket"])
        for i, participant in enumerate(sorted_participants[:3]):
            if i < len(special_rewards):
                reward_type = special_rewards[i]
                await self.award_event_rewards(
                    participant["user_id"],
                    event["event_type"],
                    rewards={reward_type: 1}
                )

    async def _process_standard_leaderboard_completion(self, event: Dict, participations: List[Dict]):
        """Process completion of standard leaderboard events (Double Payout Weekend, etc.)."""
        # Sort by credits earned or XP earned
        sorted_participants = sorted(
            participations,
            key=lambda p: p.get("credits_earned", 0) + (p.get("xp_earned", 0) // 10),
            reverse=True
        )

        # Award top 3
        prizes = [500, 300, 100]  # Credit prizes for top 3
        for i, participant in enumerate(sorted_participants[:3]):
            if i < len(prizes):
                user_id = participant["user_id"]
                await self.award_event_rewards(
                    user_id,
                    event["event_type"],
                    credit_amount=prizes[i]
                )

                # Update leaderboard position
                await self.event_participation_collection.update_one(
                    {"_id": participant["_id"]},
                    {"$set": {"leaderboard_position": i + 1}}
                )

        # Award participation rewards to all (already done above, but extra for weekend warriors)
        if event["event_type"] == LimitedTimeEventType.DOUBLE_PAYOUT_WEEKEND:
            # Weekend warrior badge for all participants
            for participation in participations:
                await self.award_event_rewards(
                    participation["user_id"],
                    event["event_type"],
                    rewards={"weekend_warrior_badge": 1}
                )

    # ==================== EVENT EFFECTS ON GAMEPLAY ====================

    async def get_event_modifiers(self, user_id: str) -> Dict[str, float]:
        """Get current active event modifiers for a player."""
        active_events = await self.get_active_events()
        modifiers = {
            "xp_multiplier": 1.0,
            "credit_multiplier": 1.0,
            "special_rewards": [],
            "active_event_names": []
        }

        player_participations = await self.get_event_participation_status(user_id)
        participant_event_types = {p["event_type"] for p in player_participations}

        # Check dynamic events
        for event in active_events["dynamic_events"]:
            event_type = event["event_type"]
            if event_type in participant_event_types:
                modifiers["xp_multiplier"] *= event.get("multiplier", 1.0)
                modifiers["credit_multiplier"] *= event.get("multiplier", 1.0)
                modifiers["special_rewards"].extend(event.get("special_rewards", []))
                modifiers["active_event_names"].append(event.get("name", ""))

        # Check limited-time events
        for event in active_events["limited_time_events"]:
            event_type = event["event_type"]
            if event_type in participant_event_types:
                modifiers["xp_multiplier"] *= event.get("xp_multiplier", 1.0)
                modifiers["credit_multiplier"] *= event.get("credit_multiplier", 1.0)
                modifiers["special_rewards"].extend(event.get("special_rewards", []))
                modifiers["active_event_names"].append(event.get("name", ""))

        return modifiers

    async def should_apply_event_effect(self, user_id: str, effect_type: str) -> bool:
        """Check if a specific game effect should be applied due to active events."""
        modifiers = await self.get_event_modifiers(user_id)

        if effect_type == "xp_bonus":
            return modifiers["xp_multiplier"] > 1.0
        elif effect_type == "credit_bonus":
            return modifiers["credit_multiplier"] > 1.0
        elif effect_type == "special_rewards":
            return len(modifiers["special_rewards"]) > 0

        return False

    async def get_event_bonus_multiplier(self, user_id: str, bonus_type: str) -> float:
        """Get the multiplier for a specific bonus type."""
        modifiers = await self.get_event_modifiers(user_id)
        if bonus_type == "xp":
            return modifiers["xp_multiplier"]
        elif bonus_type == "credit":
            return modifiers["credit_multiplier"]
        return 1.0


# Global event service instance
_event_service_instance = None

def get_event_service():
    global _event_service_instance
    if _event_service_instance is None:
        _event_service_instance = EventService()
    return _event_service_instance