"""SLA113 API Router - Universal AI Game Studio"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import os
import re
import json
import asyncio
import random as _random
import base64
import tempfile

# ─── Graceful fallback for optional emergentintegrations package ───
# In CI/Vercel smoke environments, the private emergentintegrations package may not be installed.
# We try local backup first, then degrade gracefully. Terminal/image endpoints will fail
# at runtime (not import time) with clear error messages if the package is missing.
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:
    try:
        from emergentintegrations_local_backup.llm.chat import LlmChat, UserMessage
    except ImportError:  # pragma: no cover
        # Smoke/CI import-only check: set to None, guard endpoints will detect at runtime
        LlmChat = None
        UserMessage = None

from database import get_database
from sla113.models import (
    GAME_TYPES,
    AUDIO_MIDDLEWARE_TYPES,
    AUDIO_ENGINES,
    CreateProjectRequest,
    VisionGenerateRequest,
    LogicGenerateRequest,
    ComposeRequest,
    AudioForgeRequest,
)
from sla113.vision_engine import generate_vision_assets
from sla113.logic_engine import generate_logic
from sla113.composer_engine import compose_game_bundle
from sla113.audio_forge import generate_audio_asset
from sla113.fish_multiplayer import create_lobby, get_lobby, list_lobbies, delete_lobby

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sla113", tags=["sla113"])
