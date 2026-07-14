"""
WebSocket endpoint for real-time HSE updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional
import json

from app.database import get_db
from app.utils.websocket import connection_manager
from app.utils.rbac import get_current_user_optional

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time updates.
    Client connects with: ws://localhost:8000/ws?token=JWT_TOKEN
    """
    await websocket.accept()

    # Validate token
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    # Validate JWT and get user info
    try:
        from app.utils.rbac import decode_token
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        site_access = payload.get("site_access", ["ALL"])
        role = payload.get("role")
    except Exception as e:
        await websocket.close(code=4002, reason=f"Invalid token: {str(e)}")
        return

    # Connect to manager
    await connection_manager.connect(websocket, user_id, site_access)

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle client messages
            message_type = message.get("type")

            if message_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})

            elif message_type == "subscribe":
                # Client subscribes to specific updates
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": message.get("channel"),
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, user_id, site_access)
    except Exception as e:
        print(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket, user_id, site_access)


@router.get("/ws/stats", tags=["WebSocket"])
async def websocket_stats():
    """Get WebSocket connection statistics."""
    return {
        "total_users": len(connection_manager.user_connections),
        "total_sites": len(connection_manager.site_connections),
        "total_connections": sum(len(conns) for conns in connection_manager.user_connections.values()),
    }
