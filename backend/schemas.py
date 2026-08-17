from datetime import datetime
from typing import Literal
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
