export type AppMode = 'static' | 'alive';
export type NavKey = 'dashboard' | 'chats' | 'projects' | 'workspaces' | 'research' | 'knowledge' | 'memory' | 'files' | 'models' | 'agents' | 'boundary' | 'sandbox' | 'plugins' | 'marketplace' | 'automation' | 'tasks' | 'history' | 'logs' | 'analytics' | 'monitoring' | 'notifications' | 'security' | 'developer' | 'settings' | 'help';
export interface Activity { id: string; title: string; detail: string; icon: string; }
export interface RuntimeStatus { state: 'online' | 'offline' | 'busy'; version: string; uptime: string; }
export interface DashboardSnapshot { activeAgents: number; tasksToday: number; memoryItems: number; activity: Activity[]; runtime: RuntimeStatus; }
export interface ApiError { code: string; message: string; retryable: boolean; }
export interface Service<T> { list(): Promise<T[]>; }
