

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional
import json
from app.core.security import get_current_user_ws
from app.websockets.manager import manager

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    user = Depends(get_current_user_ws)
):
    try:
        # Connect
        await manager.connect(websocket, client_id)

        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            message_type = message.get("type")
            if message_type == "subscribe":
                topic = message.get("topic")
                if topic:
                    await manager.subscribe(client_id, topic)
                    await websocket.send_json({
                        "type": "subscribed",
                        "topic": topic
                    })

            elif message_type == "unsubscribe":
                topic = message.get("topic")
                if topic:
                    await manager.unsubscribe(client_id, topic)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "topic": topic
                    })

    except WebSocketDisconnect:
        await manager.disconnect(client_id)

