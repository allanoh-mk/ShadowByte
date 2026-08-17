# ShadowByte Phase 1 backend

FastAPI gateway scaffold for the Vite frontend. It intentionally keeps domain behavior behind adapters while exposing stable API and WebSocket contracts.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The frontend runs on `http://localhost:5173`. The gateway runs on `http://localhost:8000`.

## Integrations

- Neon Postgres: `DATABASE_URL`; `PostgresAdapter` owns health and future persistence queries.
- Upstash Redis: `REDIS_URL` + `REDIS_TOKEN`; `RedisAdapter` owns cache, pub/sub, and event transport.
- Qdrant: `QDRANT_URL` + `QDRANT_API_KEY`; `QdrantAdapter` owns vector memory operations.

## Contract groups

Gateway: `/api/health`, `/api/status`, `/api/version`, `/api/routes`
Workspace/chat: `/api/workspaces`, `/api/chats`, `/api/chats/messages`
Runtime: `/api/agents`, `/api/tasks`, `/api/memory/search`
Realtime: `/ws/{channel}` for `orb`, `chat`, `agents`, `tasks`, `monitoring`, `logs`, `notifications`, and future channels.

No credentials are hardcoded. Domain persistence and agent execution remain deliberately unimplemented behind typed boundaries.
