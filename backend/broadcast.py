from __future__ import annotations
import asyncio
import json
from typing import Any

class EventBroadcaster:
    def __init__(self, redis_url: str = '', redis_token: str = '', stream: str = 'shadowbyte:events'):
        self.redis_url, self.redis_token, self.stream = redis_url, redis_token, stream
        self.connections: dict[str, set[Any]] = {}

    async def connect(self, channel: str, websocket: Any):
        self.connections.setdefault(channel, set()).add(websocket)

    async def disconnect(self, channel: str, websocket: Any):
        self.connections.get(channel, set()).discard(websocket)

    async def publish(self, channel: str, event: dict[str, Any]):
        payload = {'channel': channel, **event}
        clients = list(self.connections.get(channel, set()))
        await asyncio.gather(*(client.send_json(payload) for client in clients), return_exceptions=True)
        if self.redis_url and self.redis_token:
            try:
                from httpx import AsyncClient
                async with AsyncClient(timeout=5) as client:
                    await client.post(f'{self.redis_url}/xadd/{self.stream}/*/payload/{json.dumps(payload)}', headers={'Authorization': f'Bearer {self.redis_token}'})
            except Exception:
                pass
        return payload
