from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .adapters import MemoryStore, PostgresAdapter, RedisAdapter, VectorMemoryAdapter


class RuntimeService:
    def __init__(self, db: PostgresAdapter, cache: RedisAdapter, vectors: VectorMemoryAdapter, memory: MemoryStore) -> None:
        self.db = db
        self.cache = cache
        self.vectors = vectors
        self.memory = memory
        self.tasks: list[dict[str, Any]] = []

    async def status(self) -> dict[str, Any]:
        checks = {
            'postgres': await self.db.health(),
            'redis': await self.cache.health(),
            'qdrant': await self.vectors.health(),
        }
        return {'status': 'ok' if all(checks.values()) else 'degraded', 'checkedAt': datetime.now(timezone.utc).isoformat(), 'services': checks}

    async def append_event(self, stream: str, event: dict[str, Any]) -> dict[str, Any]:
        payload = {'stream': stream, 'event': event, 'createdAt': datetime.now(timezone.utc).isoformat()}
        await self.cache.publish(stream, payload)
        return payload

    async def search_memory(self, query: str, workspace_id: str | None = None) -> list[dict[str, Any]]:
        return await self.vectors.search(query, workspace_id=workspace_id)

    async def remember(self, text: str, workspace_id: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        item = {'text': text, 'workspaceId': workspace_id, 'metadata': metadata or {}, 'createdAt': datetime.now(timezone.utc).isoformat()}
        self.memory.add(item)
        await self.vectors.upsert(item)
        await self.append_event('memory', {'type': 'memory.created', 'workspaceId': workspace_id})
        return item
