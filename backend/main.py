from datetime import UTC, datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from .adapters import services
from .config import get_settings
from .registry import ROUTES
from .schemas import AgentTask, ChatRequest, MemorySearchRequest, StatusResponse, Workspace
from .services import RuntimeService
from .routes import router as runtime_router
from .auth import current_identity
from .repository import DurableRepository
from .broadcast import EventBroadcaster
from .vector_memory import VectorMemory

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version, docs_url='/api/docs')
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.state.runtime = RuntimeService(services.postgres, services.redis, services.qdrant, services.memory)
app.state.jwt_secret = settings.jwt_secret
app.state.auth_required = settings.auth_required
app.state.repository = DurableRepository(settings.database_url)
app.state.broadcast = EventBroadcaster(settings.redis_url, settings.redis_token, settings.redis_stream)
app.state.vector_memory = VectorMemory(settings.qdrant_url, settings.qdrant_api_key, settings.qdrant_collection)
app.include_router(runtime_router, dependencies=[Depends(current_identity)])

@app.on_event('startup')
async def startup():
    await app.state.repository.connect()
    await app.state.vector_memory.ensure_collection()

@app.on_event('shutdown')
async def shutdown():
    await app.state.repository.close()

@app.get('/api/health')
async def health() -> dict[str, str]:
    return {'status': 'ok', 'service': settings.app_name, 'timestamp': datetime.now(UTC).isoformat()}

@app.get('/api/status', response_model=StatusResponse)
async def status() -> StatusResponse:
    service_health = await services.health()
    degraded = any(item['status'] == 'degraded' for item in service_health.values())
    not_configured = any(item['status'] == 'not_configured' for item in service_health.values())
    return StatusResponse(status='degraded' if degraded else 'not_configured' if not_configured else 'ok', version=settings.app_version, services=service_health)

@app.get('/api/version')
async def version() -> dict[str, str]:
    return {'name': settings.app_name, 'version': settings.app_version}

@app.get('/api/routes')
async def routes() -> list[dict[str, str]]:
    return [route.__dict__ for route in ROUTES]

@app.get('/api/workspaces', response_model=list[Workspace])
async def workspaces() -> list[Workspace]:
    now = datetime.now(UTC)
    return [Workspace(id='default', name='Command center', description='Primary ShadowByte runtime workspace', status='active', updated_at=now)]

@app.get('/api/chats')
async def chats() -> list[dict[str, str]]:
    return [{'id': 'chat-default', 'title': 'Runtime briefing', 'status': 'active'}]

@app.post('/api/chats/messages')
async def send_message(request: ChatRequest) -> dict[str, str]:
    return {'id': 'message-preview', 'role': 'assistant', 'content': f'Accepted in {request.mode} mode. Backend agent streaming is connected to the runtime contract.'}

@app.get('/api/agents')
async def agents() -> list[dict[str, str]]:
    return [{'id': 'eve', 'name': 'eve', 'status': 'ready'}]

@app.get('/api/tasks', response_model=list[AgentTask])
async def tasks() -> list[AgentTask]:
    return [AgentTask(id='task-1', title='Gateway bootstrap', status='running', progress=68)]

@app.post('/api/memory/search')
async def memory_search(request: MemorySearchRequest) -> dict[str, object]:
    return {'query': request.query, 'matches': [], 'provider': 'qdrant'}

@app.websocket('/ws/{channel}')
async def websocket_channel(websocket: WebSocket, channel: str) -> None:
    token = websocket.query_params.get('token')
    if app.state.auth_required and not token:
        await websocket.close(code=4401)
        return
    await websocket.accept()
    await app.state.broadcast.connect(channel, websocket)
    try:
        await app.state.broadcast.publish(channel, {'event': 'connected', 'timestamp': datetime.now(UTC).isoformat()})
        while True:
            message = await websocket.receive_json()
            await app.state.broadcast.publish(channel, {'event': 'message', 'payload': message})
    except WebSocketDisconnect:
        await app.state.broadcast.disconnect(channel, websocket)
