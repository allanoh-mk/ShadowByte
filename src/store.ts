import { create } from 'zustand';
import type { AppMode, NavKey } from './types';
interface UIState { mode: AppMode; activeNav: NavKey; commandOpen: boolean; setMode: (mode: AppMode) => void; setActiveNav: (nav: NavKey) => void; setCommandOpen: (open: boolean) => void; }
export const useUIStore = create<UIState>((set) => ({ mode: 'static', activeNav: 'dashboard', commandOpen: false, setMode: (mode) => set({ mode }), setActiveNav: (activeNav) => set({ activeNav }), setCommandOpen: (commandOpen) => set({ commandOpen }) }));
