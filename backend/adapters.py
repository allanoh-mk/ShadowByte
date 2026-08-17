from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import json
import os
import httpx

try:
    from .config import get_settings
except ImportError:
    from config import get_settings

@dataclass
class PostgresAdapter:
    database_url: str
    async def health(self) -> dict[str, str]:
        if not self.database_url:
            return {'status': 'not_configured', 'provider': 'neon'}
        try:
            import asyncpg
            connection = await asyncpg.connect(self.database_url, timeout=2)
            await connection.fetchval('SELECT 1')
            await connection.close()
            return {'status': 'ok', 'provider': 'neon'}
        except Exception:
            return {'status': 'degraded', 'provider': 'neon'}

@dataclass
class RedisAdapter:
    url: str
    token: str
    async def health(self) -> dict[str, str]:
        if not self.url or not self.token:
            return {'status': 'not_configured', 'provider': 'upstash'}
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                response = await client.get(f'{self.url}/ping', headers={'Authorization': f'Bearer {self.token}'})
            return {'status': 'ok' if response.is_success else 'degraded', 'provider': 'upstash'}
        except Exception:
            return {'status': 'degraded', 'provider': 'upstash'}
    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        if not self.url or not self.token:
            return
        encoded = httpx.QueryParams({'payload': json.dumps(payload, separators=(',', ':'))})
        async with httpx.AsyncClient(timeout=3) as client:
            await client.post(f'{self.url}/publish/{channel}', content=encoded.get('payload'), headers={'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'})

@dataclass
class QdrantAdapter:
    url: str
    api_key: str
    collection: str = 'shadowbyte_memory'
    async def health(self) -> dict[str, str]:
        if not self.url:
            return {'status': 'not_configured', 'provider': 'qdrant'}
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                response = await client.get(f'{self.url.rstrip("/")}/healthz', headers={'api-key': self.api_key} if self.api_key else {})
            return {'status': 'ok' if response.is_success else 'degraded', 'provider': 'qdrant'}
        except Exception:
            return {'status': 'degraded', 'provider': 'qdrant'}
    async def upsert(self, item: dict[str, Any]) -> None:
        return None
    async def search(self, query: str, workspace_id: str | None = None) -> list[dict[str, Any]]:
        return []

@dataclass
class MemoryStore:
    items: list[dict[str, Any]] = field(default_factory=list)
    def add(self, item: dict[str, Any]) -> None:
        self.items.append(item)

class ServiceRegistry:
    def __init__(self) -> None:
        settings = get_settings()
        self.postgres = PostgresAdapter(settings.database_url)
        self.redis = RedisAdapter(settings.redis_url, settings.redis_token)
        self.qdrant = QdrantAdapter(settings.qdrant_url, settings.qdrant_api_key)
        self.memory = MemoryStore()
    async def health(self) -> dict[str, dict[str, str]]:
        import asyncio
        postgres, redis, qdrant = await asyncio.gather(self.postgres.health(), self.redis.health(), self.qdrant.health())
        return {'postgres': postgres, 'redis': redis, 'qdrant': qdrant}

services = ServiceRegistry()
