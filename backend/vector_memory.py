from __future__ import annotations
from hashlib import sha256
from typing import Any

class VectorMemory:
    def __init__(self, url: str, api_key: str, collection: str):
        self.url, self.api_key, self.collection = url.rstrip('/'), api_key, collection
        self.items: list[dict[str, Any]] = []

    def _vector(self, content: str) -> list[float]:
        digest = sha256(content.encode()).digest()
        return [round((byte / 255) * 2 - 1, 5) for byte in digest[:32]]

    async def ensure_collection(self):
        if not self.url: return False
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.put(f'{self.url}/collections/{self.collection}', headers=self._headers(), json={'vectors': {'size': 32, 'distance': 'Cosine'}})
            return response.status_code in (200, 201)
        except Exception: return False

    async def upsert(self, item: dict[str, Any]):
        item = {**item, 'vectorId': item.get('id'), 'vector': self._vector(item['content'])}
        self.items = [existing for existing in self.items if existing.get('id') != item.get('id')] + [item]
        if self.url:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=8) as client:
                    await client.put(f'{self.url}/collections/{self.collection}/points', headers=self._headers(), json={'points': [{'id': item['id'], 'vector': item['vector'], 'payload': item}]})
            except Exception: pass
        return item

    async def search(self, query: str, limit: int = 10):
        vector = self._vector(query)
        if self.url:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=8) as client:
                    response = await client.post(f'{self.url}/collections/{self.collection}/points/search', headers=self._headers(), json={'vector': vector, 'limit': limit, 'with_payload': True})
                    if response.is_success: return response.json().get('result', [])
            except Exception: pass
        tokens = set(query.lower().split())
        return sorted(self.items, key=lambda item: len(tokens & set(item['content'].lower().split())), reverse=True)[:limit]

    def _headers(self):
        return {'api-key': self.api_key} if self.api_key else {}
