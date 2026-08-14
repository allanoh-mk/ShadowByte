export type ShadowByteEvent = 'ThemeChanged' | 'LayoutChanged' | 'OrbStateChanged' | 'TaskCompleted' | 'WorkspaceLoaded';
type Listener = (payload?: unknown) => void;
const listeners = new Map<ShadowByteEvent, Set<Listener>>();
export const eventBus = { on(event: ShadowByteEvent, listener: Listener) { const set = listeners.get(event) ?? new Set<Listener>(); set.add(listener); listeners.set(event, set); return () => set.delete(listener); }, emit(event: ShadowByteEvent, payload?: unknown) { listeners.get(event)?.forEach((listener) => listener(payload)); } };
