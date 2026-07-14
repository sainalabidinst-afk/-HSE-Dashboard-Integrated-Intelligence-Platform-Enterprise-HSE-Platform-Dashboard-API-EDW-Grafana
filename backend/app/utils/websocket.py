"""
WebSocket Manager for Real-Time Updates
Provides real-time notifications for alerts, incidents, and dashboard updates
"""

from typing import Dict, Set, Optional
from datetime import datetime
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.user_connections: Dict[int, Set[WebSocket]] = defaultdict(set)
        self.site_connections: Dict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, user_id: int, site_access: list):
        """Accept new WebSocket connection."""
        await websocket.accept()

        # Store by user
        self.user_connections[user_id].add(websocket)

        # Store by site
        for site_id in site_access:
            self.site_connections[site_id].add(websocket)

        # Store by connection ID
        conn_id = f"{user_id}_{id(websocket)}"
        self.active_connections[conn_id].add(websocket)

        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to HSE Real-Time Dashboard",
            "timestamp": datetime.utcnow().isoformat(),
        })

    def disconnect(self, websocket: WebSocket, user_id: int, site_access: list):
        """Remove WebSocket connection."""
        # Remove from user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove from site connections
        for site_id in site_access:
            if site_id in self.site_connections:
                self.site_connections[site_id].discard(websocket)
                if not self.site_connections[site_id]:
                    del self.site_connections[site_id]

        # Remove from active connections
        conn_id = f"{user_id}_{id(websocket)}"
        if conn_id in self.active_connections:
            self.active_connections[conn_id].discard(websocket)
            if not self.active_connections[conn_id]:
                del self.active_connections[conn_id]

    async def send_to_user(self, user_id: int, message: dict):
        """Send message to specific user."""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    async def send_to_site(self, site_id: str, message: dict):
        """Send message to all users connected to a site."""
        if site_id in self.site_connections:
            for connection in self.site_connections[site_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    async def broadcast(self, message: dict):
        """Broadcast message to all active connections."""
        for connections in self.user_connections.values():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    async def send_alert(self, site_id: str, alert_data: dict):
        """Send alert to all users monitoring a site."""
        message = {
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_to_site(site_id, message)

    async def send_incident_update(self, site_id: str, incident_data: dict):
        """Send incident update to all users monitoring a site."""
        message = {
            "type": "incident_update",
            "data": incident_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_to_site(site_id, message)

    async def send_ptw_update(self, site_id: str, ptw_data: dict):
        """Send PTW update to all users monitoring a site."""
        message = {
            "type": "ptw_update",
            "data": ptw_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_to_site(site_id, message)

    async def send_dashboard_refresh(self, site_id: str, dashboard_type: str):
        """Notify clients to refresh specific dashboard section."""
        message = {
            "type": "dashboard_refresh",
            "dashboard_type": dashboard_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_to_site(site_id, message)


# Global connection manager instance
connection_manager = ConnectionManager()
