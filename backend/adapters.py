from dataclasses import dataclass
from typing import Any
import httpx

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
        if self.url and self.token:
            async with httpx.AsyncClient(timeout=3) as client:
                await client.post(f'{self.url}/publish/{channel}/{httpx.URL(str(payload))}', headers={'Authorization': f'Bearer {self.token}'})

@dataclass
class QdrantAdapter:
    url: str
    api_key: str
    async def health(self) -> dict[str, str]:
        if not self.url:
            return {'status': 'not_configured', 'provider': 'qdrant'}
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                response = await client.get(f'{self.url}/healthz', headers={'api-key': self.api_key} if self.api_key else {})
            return {'status': 'ok' if response.is_success else 'degraded', 'provider': 'qdrant'}
        except Exception:
            return {'status': 'degraded', 'provider': 'qdrant'}

class ServiceRegistry:
    def __init__(self) -> None:
        settings = get_settings()
        self.postgres = PostgresAdapter(settings.database_url)
        self.redis = RedisAdapter(settings.redis_url, settings.redis_token)
        self.qdrant = QdrantAdapter(settings.qdrant_url, settings.qdrant_api_key)
    async def health(self) -> dict[str, dict[str, str]]:
        postgres, redis, qdrant = await __import__('asyncio').gather(self.postgres.health(), self.redis.health(), self.qdrant.health())
        return {'postgres': postgres, 'redis': redis, 'qdrant': qdrant}

services = ServiceRegistry()
