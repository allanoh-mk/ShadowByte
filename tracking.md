# ShadowByte Frontend Tracking

**Date:** 2026-08-14  
**Phase:** Stage 5 — Dual living interfaces
**Completion:** 100% frontend UI surface + adaptive device layer

## Pages
- [x] Dashboard
- [x] Route-ready module surfaces: Chats, Projects, Research, Memory, Files, Models, Agents, Monitoring, Settings
- [x] Expanded runtime route surfaces: Workspaces, Knowledge, Boundary, Sandbox, Plugins, Automation, Tasks, Logs, Analytics
- [x] Interactive module surfaces with search, filters, rows, statuses, and insight panels
- [x] Dashboard focus queue and workspace list
- [x] Phase 1 backend-connected module contracts and FastAPI gateway scaffold
- [x] Full page registry: 25 distinct page definitions with purpose, metrics, sections, actions, and backend routes
- [x] Page-specific metrics and connected route summaries rendered in the UI

## Components
- [x] Living Glass shell
- [x] Sidebar navigation
- [x] Topbar and global UI interface switcher
- [x] Runtime health panel
- [x] User-focused chat drawer and assistant interaction
- [x] Assistant-focused Orb-only interface with floating cards
- [x] Live mesh-of-nerves Orb with listening, working, and speaking reactions
- [x] Process progress cards and assistant working states
- [x] Command palette
- [ ] Full shadcn component inventory

## Services / Stores / Events
- [x] Typed dashboard service with mock adapter
- [x] Zustand UI store
- [x] Internal event bus
- [x] Expanded typed navigation contract
- [ ] Complete service layer
- [ ] Workspace and layout stores

## APIs referenced
- [ ] GET /api/system/status
- [ ] GET /api/workspaces/:id/dashboard
- [ ] GET /api/notifications

## WebSocket channels referenced
- [ ] /ws/system
- [ ] /ws/orb
- [ ] /ws/monitoring

## Theme and animation
- [x] Living Glass semantic tokens
- [x] Dark graphite, cyan, violet, green status palette
- [x] Orb breathe and float motion
- [x] Reduced-motion handling
- [x] Responsive module layouts and mobile navigation drawer
- [x] Desktop-first baseline with fluid large-desktop scaling
- [x] Laptop and tablet breakpoints with adaptive grids and sidebars
- [x] Tablet overflow correction and mobile navigation behavior at 1100px and below
- [x] Mobile portrait/landscape-friendly layouts with touch targets and bottom sheets
- [x] Custom/default accent tokens cascade through panels, controls, navigation, Orb, and status surfaces
- [x] Theme persistence across reloads via frontend preference storage
- [x] Motion-aware orb, hover, focus, and reduced-motion states
- [x] Theme engine: Midnight, Glass, Violet, High Contrast
- [x] Theme switching from assistant interface and workspace interface
- [x] Global toast notifications and mode transition feedback
- [x] Reduced-motion accessibility behavior
- [x] Theme variants and global switcher behavior
- [x] Theme-aware Living Glass surfaces
- [x] Custom theme creator with accent, background, blur placement, blur intensity, glass opacity, and background opacity controls
- [x] Theme reset and live preview controls
- [x] Accessibility controls: keyboard focus, labeled icon buttons, reduced motion, contrast-ready tokens
- [x] Utility interactions: share, retry, copy, speaker, mute, model dropdown, mode selector, fast/chat/code/write modes
- [x] Toast notifications, retry states, progress states, assistant speaking/listening/working reactions
- [x] Frontend UI surface complete; backend wiring remains contract-driven

## Backend connection map
Frontend dev server: `http://localhost:5173` (Vite). Production deployment uses the same relative `/api` and `/ws` paths behind the hosting origin.

REST endpoints consumed by future service adapters:
- `GET /api/auth/session`, `GET /api/profile`
- `GET/POST/PATCH/DELETE /api/workspaces`, `GET /api/workspaces/:id/dashboard`
- `GET/POST/PATCH/DELETE /api/projects`, `GET/POST/PATCH/DELETE /api/chats`, `GET/POST /api/chats/:id/messages`
- `GET /api/research`, `GET/POST/PATCH/DELETE /api/files`, `GET /api/files/:id/preview`
- `GET/POST/PATCH/DELETE /api/memory`, `GET /api/knowledge/search`
- `GET /api/models`, `POST /api/models/:id/load`, `POST /api/models/:id/unload`
- `GET/POST/PATCH/DELETE /api/agents`, `GET/POST/PATCH/DELETE /api/automation`, `GET /api/tasks`
- `GET /api/boundary/policies`, `POST /api/boundary/scans`, `GET /api/sandbox/sessions`, `POST /api/sandbox/sessions`
- `GET/POST/DELETE /api/plugins`, `GET /api/marketplace`, `GET /api/integrations`
- `GET /api/notifications`, `PATCH /api/notifications/:id/read`, `GET /api/history`, `GET /api/logs`
- `GET /api/analytics`, `GET /api/monitoring`, `GET /api/search`, `GET /api/version`, `GET /api/updates`
- `POST /api/terminal/commands`, `POST /api/voice/transcribe`, `POST /api/voice/speak`

WebSocket channels consumed by future event adapters:
- `/ws/system`, `/ws/status`, `/ws/orb`, `/ws/chat`, `/ws/agents`, `/ws/models`
- `/ws/boundary`, `/ws/tasks`, `/ws/monitoring`, `/ws/logs`, `/ws/notifications`
- `/ws/research`, `/ws/workspaces`, `/ws/projects`, `/ws/files`, `/ws/memory`

Frontend-to-backend seams:
- `src/services.ts`: replace typed mock methods with REST clients.
- `src/events.ts`: map WebSocket payloads into typed internal events.
- `src/store.ts`: hydrate workspace, mode, theme, and assistant state from session APIs.
- `src/App.tsx`: UI-only orchestration; no backend calls inside presentational components.

## TODO
- Replace mock adapters when backend endpoints are available.
- Add generated OpenAPI/WebSocket payload types.
- Connect auth/session and persistence.

## Backend dependencies
- [x] FastAPI gateway scaffold under `backend/`
- [x] Neon Postgres adapter using `DATABASE_URL`
- [x] Upstash Redis adapter using `REDIS_URL` and `REDIS_TOKEN`
- [x] Qdrant vector memory adapter using `QDRANT_URL` and `QDRANT_API_KEY`
- [x] Typed service registry, Pydantic contracts, domain routes, and WebSocket channels
- [x] Runtime service layer for health, event publishing, memory capture, and memory search
- [x] Strict task, memory, event, and page contract schemas
- [x] Runtime status, page contracts, task creation, memory capture/search, event publish, and stream routes
- [ ] Production persistence queries, agent execution, and vector indexing


## Mock data usage
- Dashboard snapshot and runtime telemetry are mocked behind `dashboardService`.

## TODO
- Add React Router nested route registry and lazy route boundaries.
- Add typed API contracts for every service and WebSocket payload.
- Add backend-driven Orb event stream through /ws/orb.
- Add draggable and dockable workspace layout engine.
- Add full custom theme editor and export/import.
- Replace mock adapters when backend endpoints are available.

## Current frontend integration status
- UI modes share the same Zustand navigation state and mock service boundary.
- Assistant-focused mode intentionally hides navigation and presents only Orb, floating cards, and assistant composer.
- User-focused mode exposes navigation, pages, command palette, and an assistant drawer.
- No backend, AI model, Linux integration, or business logic has been implemented.
