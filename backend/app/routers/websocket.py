from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import json
import asyncio

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []
        self.by_user: Dict[int, WebSocket] = {}

    async def connect(self, ws: WebSocket, user_id: int = None):
        await ws.accept()
        self.active.append(ws)
        if user_id:
            self.by_user[user_id] = ws

    def disconnect(self, ws: WebSocket, user_id: int = None):
        if ws in self.active:
            self.active.remove(ws)
        if user_id and user_id in self.by_user:
            del self.by_user[user_id]

    async def send_to_user(self, user_id: int, data: Any):
        ws = self.by_user.get(user_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                self.disconnect(ws, user_id)

    async def broadcast(self, data: Any):
        disconnected = []
        for ws in self.active:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            if ws in self.active:
                self.active.remove(ws)


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(ws: WebSocket, user_id: int):
    await manager.connect(ws, user_id)
    try:
        await ws.send_text(json.dumps({"type": "connected", "user_id": user_id}))
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
                # Echo location updates for driver tracking
                if msg.get("type") == "location_update":
                    await manager.broadcast({
                        "type": "driver_location",
                        "driver_id": user_id,
                        "lat": msg.get("lat"),
                        "lng": msg.get("lng"),
                    })
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(ws, user_id)
