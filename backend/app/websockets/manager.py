

from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # client_id -> WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
        # topic -> set of client_ids
        self.subscriptions: Dict[str, Set[str]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str
    ):
        """Accept websocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: str):
        """Handle client disconnection"""
        # Remove from active connections
        self.active_connections.pop(client_id, None)

        # Remove from all subscriptions
        for subscribers in self.subscriptions.values():
            subscribers.discard(client_id)

    async def subscribe(
        self,
        client_id: str,
        topic: str
    ):
        """Subscribe client to topic"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(client_id)

    async def unsubscribe(
        self,
        client_id: str,
        topic: str
    ):
        """Unsubscribe client from topic"""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(client_id)

    async def publish(
        self,
        topic: str,
        message: dict
    ):
        """Publish message to topic subscribers"""
        if topic not in self.subscriptions:
            return

        # Get subscribers
        subscribers = self.subscriptions[topic]
        if not subscribers:
            return

        # Prepare message
        message_data = {
            "topic": topic,
            "data": message
        }

        # Send to all subscribers
        for client_id in subscribers:
            try:
                websocket = self.active_connections.get(client_id)
                if websocket:
                    await websocket.send_json(message_data)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {str(e)}")
                await self.disconnect(client_id)

manager = ConnectionManager()

