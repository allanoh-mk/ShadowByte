from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

class StatusResponse(BaseModel):
    status: Literal['ok', 'degraded', 'not_configured']
    version: str
    services: dict[str, dict[str, str]]

class Workspace(BaseModel):
    id: str
    name: str
    description: str
    status: str
    updated_at: datetime

class ChatMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: str = Field(min_length=1, max_length=10000)

class ChatRequest(BaseModel):
    workspace_id: str = 'default'
    mode: Literal['fast', 'chat', 'code', 'write'] = 'chat'
    message: ChatMessage

class AgentTask(BaseModel):
    id: str
    title: str
    status: Literal['queued', 'running', 'completed', 'failed']
    progress: int = Field(ge=0, le=100)

class MemorySearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default='', max_length=4000)
    priority: Literal['low', 'normal', 'high', 'urgent'] = 'normal'
    workspaceId: str = 'default'
    assignee: str | None = None

class MemoryCreate(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    workspaceId: str = 'default'
    metadata: dict[str, Any] = Field(default_factory=dict)

class EventEnvelope(BaseModel):
    stream: str = Field(min_length=1, max_length=80)
    type: str = Field(min_length=1, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)

class PageContract(BaseModel):
    page: str
    status: str
    contractVersion: str
    supports: list[str]
    routes: list[str] = Field(default_factory=list)
    events: list[str] = Field(default_factory=list)
