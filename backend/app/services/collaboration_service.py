import asyncio
import json
from fastapi import WebSocket
from dataclasses import dataclass, field


@dataclass
class ConnectedUser:
    user_id: str
    user_name: str
    websocket: WebSocket


class CollaborationService:
    """Manages WebSocket connections and broadcasts for real-time collaboration."""

    def __init__(self):
        # journey_id -> list of connected users
        self._connections: dict[str, list[ConnectedUser]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, journey_id: str, user_id: str, user_name: str, websocket: WebSocket):
        """Register a user connection for a journey."""
        await websocket.accept()
        user = ConnectedUser(user_id=user_id, user_name=user_name, websocket=websocket)

        async with self._lock:
            if journey_id not in self._connections:
                self._connections[journey_id] = []
            self._connections[journey_id].append(user)

        # Broadcast user joined
        await self.broadcast(journey_id, {
            "type": "user_joined",
            "user": {"id": user_id, "name": user_name},
            "online_users": self._get_online_users(journey_id),
        }, exclude_user=None)  # Include everyone

    async def disconnect(self, journey_id: str, user_id: str):
        """Remove a user connection."""
        async with self._lock:
            if journey_id in self._connections:
                self._connections[journey_id] = [
                    u for u in self._connections[journey_id] if u.user_id != user_id
                ]
                if not self._connections[journey_id]:
                    del self._connections[journey_id]

        await self.broadcast(journey_id, {
            "type": "user_left",
            "user_id": user_id,
            "online_users": self._get_online_users(journey_id),
        }, exclude_user=user_id)

    async def broadcast(self, journey_id: str, message: dict, exclude_user: str | None = None):
        """Broadcast a message to all connected users in a journey."""
        connections = self._connections.get(journey_id, [])
        dead_connections = []

        for conn in connections:
            if exclude_user and conn.user_id == exclude_user:
                continue
            try:
                await conn.websocket.send_json(message)
            except Exception:
                dead_connections.append(conn)

        # Clean up dead connections
        if dead_connections:
            async with self._lock:
                for dead in dead_connections:
                    if journey_id in self._connections:
                        self._connections[journey_id] = [
                            c for c in self._connections[journey_id] if c.user_id != dead.user_id
                        ]

    def _get_online_users(self, journey_id: str) -> list[dict]:
        """Get list of online users for a journey."""
        connections = self._connections.get(journey_id, [])
        seen = set()
        users = []
        for conn in connections:
            if conn.user_id not in seen:
                seen.add(conn.user_id)
                users.append({"id": conn.user_id, "name": conn.user_name})
        return users

    def get_online_count(self, journey_id: str) -> int:
        """Get count of unique online users."""
        return len(set(c.user_id for c in self._connections.get(journey_id, [])))


# Singleton instance
collaboration_manager = CollaborationService()
