import type { DashboardSnapshot } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export type ApiStatus = { status: string; version: string; services: Record<string, { status: string; provider: string }> };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } });
  if (!response.ok) throw new Error(`ShadowByte API ${response.status}`);
  return response.json() as Promise<T>;
}

async function withFallback<T>(load: () => Promise<T>, fallback: T): Promise<T> {
  try { return await load(); } catch { return fallback; }
}

const emptyList = <T,>(): T[] => [];

export const dashboardService = {
  async getSnapshot(): Promise<DashboardSnapshot> {
    return { activeAgents: 4, tasksToday: 18, memoryItems: 1248, runtime: { state: 'online', version: '0.9.4-beta', uptime: '03d 14h 22m' }, activity: [{ id: '1', title: 'Research agent completed synthesis', detail: '12 sources · 2 minutes ago', icon: 'sparkles' }, { id: '2', title: 'Workspace memory indexed', detail: '48 new items · 18 minutes ago', icon: 'database' }, { id: '3', title: 'Boundary scan passed', detail: 'No anomalies detected · 41 minutes ago', icon: 'shield' }] };
  },
  async getStatus(): Promise<ApiStatus> { return withFallback(() => request<ApiStatus>('/api/status'), { status: 'degraded', version: '0.1.0', services: {} }); },
};

export const workspaceService = {
  list: () => withFallback(() => request<unknown[]>('/api/workspaces'), emptyList()),
  dashboard: (id: string) => withFallback(() => request<unknown>(`/api/workspaces/${id}/dashboard`), { id, status: 'offline', items: [] }),
};

export const chatService = {
  list: () => withFallback(() => request<unknown[]>('/api/chats'), emptyList()),
  send: (message: string, mode: string) => request<{ content: string }>('/api/chats/messages', { method: 'POST', body: JSON.stringify({ message: { role: 'user', content: message }, mode }) }),
};

export const runtimeService = {
  agents: () => withFallback(() => request<unknown[]>('/api/agents'), emptyList()),
  tasks: () => withFallback(() => request<unknown[]>('/api/tasks'), emptyList()),
  memorySearch: (query: string) => request<unknown>('/api/memory/search', { method: 'POST', body: JSON.stringify({ query }) }),
  pageContract: (key: string) => request<unknown>(`/api/pages/${key}`),
};

export const realtimeService = {
  connect: (channel: string) => new WebSocket(`${(import.meta.env.VITE_WS_BASE_URL ?? 'ws://localhost:8000')}/ws/${channel}`),
};
