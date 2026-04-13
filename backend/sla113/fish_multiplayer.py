"""SLA113 Multiplayer Fish Shooting — WebSocket Game Server"""
import asyncio
import json
import uuid
import random
import logging
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# ─── Lobby State ───
_lobbies = {}  # lobby_id -> Lobby


class Fish:
    __slots__ = ('id', 'x', 'y', 'vx', 'vy', 'tier', 'hp', 'max_hp', 'value', 'color', 'alive')

    TIERS = [
        {"color": "#ff6600", "value": 10,   "hp": 1, "size": 15, "name": "Goldfish"},
        {"color": "#d4af37", "value": 25,   "hp": 2, "size": 20, "name": "Koi"},
        {"color": "#00c8ff", "value": 50,   "hp": 3, "size": 25, "name": "Marlin"},
        {"color": "#ff4444", "value": 100,  "hp": 4, "size": 30, "name": "Barracuda"},
        {"color": "#44ff44", "value": 200,  "hp": 5, "size": 35, "name": "Swordfish"},
        {"color": "#9966ff", "value": 500,  "hp": 8, "size": 42, "name": "Kraken"},
        {"color": "#ff00ff", "value": 1000, "hp": 12, "size": 50, "name": "Leviathan"},
    ]

    def __init__(self, width, height, player_count):
        self.id = uuid.uuid4().hex[:8]
        tier_idx = random.choices(range(len(self.TIERS)), weights=[30, 25, 20, 12, 7, 4, 2])[0]
        tier = self.TIERS[tier_idx]
        self.tier = tier_idx
        self.color = tier["color"]
        self.value = tier["value"]
        hp_scale = max(1, player_count * 0.6)
        self.hp = max(1, int(tier["hp"] * hp_scale))
        self.max_hp = self.hp
        from_left = random.random() > 0.5
        self.x = -40 if from_left else width + 40
        self.y = 60 + random.random() * (height - 140)
        self.vx = (1 if from_left else -1) * (0.4 + random.random() * (0.8 + tier_idx * 0.15))
        self.vy = (random.random() - 0.5) * 0.4
        self.alive = True

    def update(self, width, height):
        if not self.alive:
            return
        self.x += self.vx
        self.y += self.vy
        # Bounce vertically
        if self.y < 50 or self.y > height - 50:
            self.vy *= -1
        # Respawn if off screen
        if self.x < -80 or self.x > width + 80:
            from_left = self.vx < 0  # came from right, respawn left
            self.x = -40 if not from_left else width + 40
            self.y = 60 + random.random() * (height - 140)
            self.vx = abs(self.vx) * (1 if not from_left else -1)

    def to_dict(self):
        return {
            "id": self.id, "x": round(self.x, 1), "y": round(self.y, 1),
            "tier": self.tier, "hp": self.hp, "max_hp": self.max_hp,
            "value": self.value, "color": self.color, "alive": self.alive,
        }


class Player:
    def __init__(self, ws: WebSocket, name: str, color: str):
        self.id = uuid.uuid4().hex[:8]
        self.ws = ws
        self.name = name
        self.color = color
        self.credits = 1000
        self.kills = 0
        self.ammo = 100
        self.x = 0
        self.y = 0

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "color": self.color,
            "credits": self.credits, "kills": self.kills, "ammo": self.ammo,
        }


class Lobby:
    COLORS = ["#00c8ff", "#d4af37", "#ff4444", "#44ff44", "#9966ff", "#ff6600", "#ff00ff", "#00ff88"]

    def __init__(self, lobby_id: str, name: str, width=1200, height=700):
        self.id = lobby_id
        self.name = name
        self.width = width
        self.height = height
        self.players = {}  # player_id -> Player
        self.fish = {}  # fish_id -> Fish
        self.chat = []  # last 50 messages
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.running = False
        self._task = None
        self._color_idx = 0
        # Spawn initial fish
        for _ in range(15):
            f = Fish(width, height, 1)
            self.fish[f.id] = f

    def next_color(self):
        c = self.COLORS[self._color_idx % len(self.COLORS)]
        self._color_idx += 1
        return c

    async def add_player(self, ws: WebSocket, name: str) -> Player:
        color = self.next_color()
        player = Player(ws, name, color)
        self.players[player.id] = player
        # Notify all
        await self.broadcast({
            "type": "player_joined",
            "player": player.to_dict(),
            "players": [p.to_dict() for p in self.players.values()],
        })
        # Send full state to new player
        await ws.send_json({
            "type": "init",
            "player_id": player.id,
            "lobby": {"id": self.id, "name": self.name, "width": self.width, "height": self.height},
            "players": [p.to_dict() for p in self.players.values()],
            "fish": [f.to_dict() for f in self.fish.values() if f.alive],
        })
        # Start game loop if first player
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._game_loop())
        return player

    async def remove_player(self, player_id: str):
        if player_id in self.players:
            name = self.players[player_id].name
            del self.players[player_id]
            await self.broadcast({"type": "player_left", "player_id": player_id, "name": name})
        if len(self.players) == 0:
            self.running = False

    async def handle_shoot(self, player_id: str, fish_id: str):
        player = self.players.get(player_id)
        if not player or player.ammo <= 0:
            return
        fish = self.fish.get(fish_id)
        if not fish or not fish.alive:
            return

        player.ammo -= 1
        fish.hp -= 1
        killed = fish.hp <= 0

        if killed:
            fish.alive = False
            player.credits += fish.value
            player.kills += 1
            await self.broadcast({
                "type": "kill",
                "player_id": player_id, "player_name": player.name,
                "fish_id": fish_id, "value": fish.value,
                "player_credits": player.credits, "player_kills": player.kills,
            })
            # Respawn a new fish after a short delay
            asyncio.create_task(self._respawn_fish_delayed())
        else:
            await self.broadcast({
                "type": "hit",
                "player_id": player_id, "fish_id": fish_id,
                "fish_hp": fish.hp, "fish_max_hp": fish.max_hp,
                "player_ammo": player.ammo,
            })

    async def _respawn_fish_delayed(self):
        await asyncio.sleep(1.0 + random.random() * 2.0)
        if not self.running:
            return
        f = Fish(self.width, self.height, len(self.players))
        self.fish[f.id] = f
        await self.broadcast({"type": "fish_spawn", "fish": f.to_dict()})

    async def handle_chat(self, player_id: str, message: str):
        player = self.players.get(player_id)
        if not player:
            return
        msg = {"player": player.name, "color": player.color, "text": message[:200], "time": datetime.now(timezone.utc).isoformat()}
        self.chat.append(msg)
        if len(self.chat) > 50:
            self.chat = self.chat[-50:]
        await self.broadcast({"type": "chat", "message": msg})

    async def broadcast(self, data):
        dead = []
        for pid, p in self.players.items():
            try:
                await p.ws.send_json(data)
            except Exception:
                dead.append(pid)
        for pid in dead:
            await self.remove_player(pid)

    async def _game_loop(self):
        """Server-authoritative game loop at ~20 ticks/sec."""
        tick = 0
        while self.running:
            try:
                # Update fish positions
                for f in list(self.fish.values()):
                    if f.alive:
                        f.update(self.width, self.height)

                # Clean dead fish older than 30 ticks
                dead_fish = [fid for fid, f in self.fish.items() if not f.alive]
                for fid in dead_fish:
                    del self.fish[fid]

                # Replenish ammo every 2 seconds
                if tick % 40 == 0:
                    for p in self.players.values():
                        p.ammo = min(p.ammo + 3, 100)

                # Spawn fish to maintain count
                target_fish = 12 + len(self.players) * 3
                alive_count = sum(1 for f in self.fish.values() if f.alive)
                if alive_count < target_fish and tick % 10 == 0:
                    f = Fish(self.width, self.height, len(self.players))
                    self.fish[f.id] = f
                    await self.broadcast({"type": "fish_spawn", "fish": f.to_dict()})

                # Send state snapshot every 3 ticks (~6.6 fps network update)
                if tick % 3 == 0:
                    await self.broadcast({
                        "type": "state",
                        "fish": [f.to_dict() for f in self.fish.values() if f.alive],
                        "players": [p.to_dict() for p in self.players.values()],
                    })

                tick += 1
                await asyncio.sleep(0.05)  # 20 ticks/sec
            except Exception as e:
                logger.error(f"Fish lobby game loop error: {e}")
                await asyncio.sleep(0.1)

        logger.info(f"Fish lobby {self.id} game loop stopped")


def get_lobby(lobby_id: str) -> Lobby:
    return _lobbies.get(lobby_id)


def create_lobby(name: str) -> Lobby:
    lobby_id = f"FISH-{uuid.uuid4().hex[:6].upper()}"
    lobby = Lobby(lobby_id, name)
    _lobbies[lobby_id] = lobby
    return lobby


def list_lobbies():
    return [
        {
            "id": l.id, "name": l.name, "players": len(l.players),
            "fish": sum(1 for f in l.fish.values() if f.alive),
            "created_at": l.created_at,
        }
        for l in _lobbies.values()
    ]


def delete_lobby(lobby_id: str):
    if lobby_id in _lobbies:
        _lobbies[lobby_id].running = False
        del _lobbies[lobby_id]
        return True
    return False
