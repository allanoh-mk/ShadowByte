from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from .schemas import EventEnvelope, MemoryCreate, TaskCreate

router = APIRouter(prefix='/api')


def service(request: Request):
    return request.app.state.runtime


@router.get('/runtime/status')
async def runtime_status(request: Request):
    return await service(request).status()


@router.get('/pages/{page_key}')
async def page_contract(page_key: str):
    return {'page': page_key, 'status': 'ready', 'contractVersion': '1.0', 'supports': ['list', 'search', 'create', 'events']}


@router.post('/tasks')
async def create_task(payload: TaskCreate, request: Request):
    result = {'id': f'task_{payload.title.lower().replace(" ", "_")}', 'status': 'queued', **payload.model_dump()}
    await service(request).append_event('tasks', {'type': 'task.created', 'task': result})
    return result


@router.post('/memory')
async def create_memory(payload: MemoryCreate, request: Request):
    return await service(request).remember(payload.text, payload.workspaceId, payload.metadata)


@router.get('/memory/search')
async def search_memory(q: str, request: Request, workspaceId: str | None = None):
    return {'items': await service(request).search_memory(q, workspaceId)}


@router.post('/events')
async def publish_event(payload: EventEnvelope, request: Request):
    return await service(request).append_event(payload.stream, payload.model_dump())


@router.websocket('/ws/{stream}')
async def stream_events(websocket: WebSocket, stream: str):
    await websocket.accept()
    await websocket.send_json({'type': 'connected', 'stream': stream})
    try:
        while True:
            message = await websocket.receive_json()
            await websocket.send_json({'type': 'ack', 'stream': stream, 'payload': message})
    except WebSocketDisconnect:
        return
