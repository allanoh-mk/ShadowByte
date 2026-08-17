from datetime import UTC, datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .adapters import services
from .config import get_settings
from .registry import ROUTES
from .schemas import AgentTask, ChatRequest, MemorySearchRequest, StatusResponse, Workspace
from .services import RuntimeService
from .routes import router as runtime_router

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version, docs_url='/api/docs')
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.state.runtime = RuntimeService(services.postgres, services.redis, services.qdrant, services.memory)
app.include_router(runtime_router)

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
    await websocket.accept()
    try:
        await websocket.send_json({'event': 'connected', 'channel': channel, 'timestamp': datetime.now(UTC).isoformat()})
        while True:
            message = await websocket.receive_json()
            await websocket.send_json({'event': 'ack', 'channel': channel, 'payload': message})
    except WebSocketDisconnect:
        return
