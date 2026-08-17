from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import json

SCHEMA = """
CREATE TABLE IF NOT EXISTS shadowbyte_events (id BIGSERIAL PRIMARY KEY, stream TEXT NOT NULL, event_type TEXT NOT NULL, subject TEXT NOT NULL, payload JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
CREATE INDEX IF NOT EXISTS shadowbyte_events_stream_idx ON shadowbyte_events(stream, created_at DESC);
CREATE TABLE IF NOT EXISTS shadowbyte_tasks (id TEXT PRIMARY KEY, subject TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL, progress INTEGER NOT NULL DEFAULT 0, payload JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
CREATE TABLE IF NOT EXISTS shadowbyte_memory (id TEXT PRIMARY KEY, subject TEXT NOT NULL, workspace_id TEXT, content TEXT NOT NULL, metadata JSONB NOT NULL, vector_id TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
"""

class DurableRepository:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._pool = None

    async def connect(self):
        if not self.database_url:
            return False
        try:
            import asyncpg
            self._pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=5)
            async with self._pool.acquire() as connection:
                for statement in SCHEMA.split(';'):
                    if statement.strip(): await connection.execute(statement)
            return True
        except Exception:
            self._pool = None
            return False

    async def close(self):
        if self._pool: await self._pool.close()

    async def save_task(self, task: dict[str, Any], subject: str):
        if not self._pool: return task
        async with self._pool.acquire() as connection:
            await connection.execute('INSERT INTO shadowbyte_tasks (id, subject, title, status, progress, payload) VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT (id) DO UPDATE SET status=$4, progress=$5, payload=$6, updated_at=NOW()', task['id'], subject, task['title'], task['status'], task.get('progress', 0), json.dumps(task))
        return task

    async def list_tasks(self, subject: str):
        if not self._pool: return []
        async with self._pool.acquire() as connection:
            rows = await connection.fetch('SELECT payload FROM shadowbyte_tasks WHERE subject=$1 ORDER BY updated_at DESC LIMIT 100', subject)
        return [json.loads(row['payload']) for row in rows]

    async def save_memory(self, item: dict[str, Any], subject: str):
        if not self._pool: return item
        async with self._pool.acquire() as connection:
            await connection.execute('INSERT INTO shadowbyte_memory (id, subject, workspace_id, content, metadata, vector_id) VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT (id) DO UPDATE SET content=$4, metadata=$5, vector_id=$6', item['id'], subject, item.get('workspaceId'), item['content'], json.dumps(item.get('metadata', {})), item.get('vectorId'))
        return item
