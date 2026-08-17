from dataclasses import dataclass

@dataclass(frozen=True)
class RouteSpec:
    method: str
    path: str
    owner: str
    purpose: str

ROUTES = [
    RouteSpec('GET', '/api/health', 'gateway', 'service health'),
    RouteSpec('GET', '/api/status', 'gateway', 'runtime status'),
    RouteSpec('GET', '/api/version', 'gateway', 'gateway version'),
    RouteSpec('GET', '/api/workspaces', 'workspace', 'list workspaces'),
    RouteSpec('GET', '/api/chats', 'chat', 'list chats'),
    RouteSpec('POST', '/api/chats/messages', 'chat', 'send chat message'),
    RouteSpec('GET', '/api/agents', 'agent', 'list agents'),
    RouteSpec('GET', '/api/tasks', 'tasks', 'list tasks'),
    RouteSpec('POST', '/api/memory/search', 'memory', 'search vector memory'),
]
