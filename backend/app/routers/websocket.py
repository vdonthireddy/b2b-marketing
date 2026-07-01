import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.security import decode_token
from app.services.collaboration_service import collaboration_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/journey/{journey_id}")
async def journey_websocket(websocket: WebSocket, journey_id: str):
    """WebSocket endpoint for real-time journey collaboration."""

    # Authenticate via query param token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing auth token")
        return

    try:
        payload = decode_token(token)
        user_id = payload["sub"]
        # We'll use a simple name from the token; in production, look up the user
        user_name = payload.get("name", f"User-{user_id[:8]}")
    except (ValueError, KeyError):
        await websocket.close(code=4001, reason="Invalid auth token")
        return

    # Connect
    await collaboration_manager.connect(journey_id, user_id, user_name, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "stage_update":
                # Broadcast stage change to other users
                await collaboration_manager.broadcast(journey_id, {
                    "type": "stage_updated",
                    "stage_id": message.get("stage_id"),
                    "field": message.get("field"),
                    "value": message.get("value"),
                    "by": user_id,
                    "by_name": user_name,
                }, exclude_user=user_id)

            elif msg_type == "item_update":
                await collaboration_manager.broadcast(journey_id, {
                    "type": "item_updated",
                    "item_id": message.get("item_id"),
                    "item_type": message.get("item_type"),
                    "action": message.get("action"),  # add, update, delete
                    "data": message.get("data"),
                    "by": user_id,
                    "by_name": user_name,
                }, exclude_user=user_id)

            elif msg_type == "cursor_move":
                await collaboration_manager.broadcast(journey_id, {
                    "type": "cursor_moved",
                    "user_id": user_id,
                    "user_name": user_name,
                    "x": message.get("x"),
                    "y": message.get("y"),
                }, exclude_user=user_id)

    except WebSocketDisconnect:
        await collaboration_manager.disconnect(journey_id, user_id)
    except Exception:
        await collaboration_manager.disconnect(journey_id, user_id)
