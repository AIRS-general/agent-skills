# Architecture

A modular desktop platform:
* Electron = desktop shell + native integrations
* React = dynamic UI/workspace
* Go = high-performance backend + AI orchestration
* Extensions = product surface (notes, kanban, calendar, AI tools, etc.)

The key architectural decision is this:
Treat Electron as the platform host, and treat your Go backend as a local application server.
That scales much better than putting business logic into Electron main process.

## Recommended High-Level Architecture

```
┌──────────────────────────────────────────────┐
│                Electron Main                 │
│----------------------------------------------│
│ Window lifecycle                             │
│ Native OS APIs                               │
│ Tray/menu/deep links                         │
│ Secure IPC bridge                            │
│ Extension loader                             │
└──────────────────────────────────────────────┘
                    │ IPC
                    ▼
┌──────────────────────────────────────────────┐
│              React Renderer                  │
│----------------------------------------------│
│ Workspace shell                              │
│ Routing/layout                               │
│ Extension frontend host                      │
│ Global state                                 │
│ WebSocket client                             │
└──────────────────────────────────────────────┘
                    │ HTTP/WebSocket
                    ▼
┌──────────────────────────────────────────────┐
│                 Go Backend                   │
│----------------------------------------------│
│ AI agents                                    │
│ Extension backend runtime                    │
│ REST API                                     │
│ WebSocket event bus                          │
│ Persistence                                  │
│ Job queue                                    │
│ Vector DB / embeddings                       │
│ File indexing                                │
└──────────────────────────────────────────────┘
```

This is similar in spirit to architectures used by systems like Visual Studio Code and Eclipse Theia, where frontend and backend are isolated and communicate over RPC/WebSockets.  ￼

Why This Architecture Scales

## Keep Electron Thin

Electron main process should NOT contain:
* AI logic
* app business logic
* extension execution
* data orchestration

It should mainly do:
* window management
* native APIs
* secure IPC
* bootstrapping backend
* update/install lifecycle

This prevents:
* renderer crashes affecting backend
* giant Electron spaghetti architecture
* Node.js bottlenecks

## Best Way to Connect Electron ↔ Go

Recommendation
Use:
* REST API → request/response
* WebSocket → realtime events/streaming
* Electron IPC → only for native desktop features

Communication Layers
```
React UI
   │
   ├── HTTP → Go backend
   ├── WebSocket → Go backend
   └── IPC → Electron Main
```
Use HTTP for:
* CRUD
* extension APIs
* settings
* persistence
* AI task creation

Use WebSocket for:
* streaming LLM responses
* realtime updates
* cross-extension events
* notifications
* collaborative state
* background task progress

Use IPC ONLY for:
* filesystem dialogs
* native menus
* notifications
* clipboard
* OS integrations

This separation is critical.

## Recommended Transport Strategy

Frontend ↔ Backend

REST

Use:
* JSON
* OpenAPI/Swagger

Good Go choices:
* chi
* gin
* fiber

WebSocket
Use a single persistent WS connection.
Recommended message structure:
```
{
  "type": "event",
  "domain": "notes",
  "event": "note.updated",
  "payload": {}
}
```

This becomes your internal realtime event bus.

In Go:
* `coder/websocket`

Suggested Monorepo Structure
```
xyan/
├── apps/
│   ├── desktop/              # Electron app
│   ├── backend/              # Go backend
│   └── extensions/
│       ├── notes/
│       ├── kanban/
│       └── calendar/
│
├── packages/
│   ├── ui/                   # shared React components
│   ├── sdk/                  # extension SDK
│   ├── types/                # shared schemas
│   ├── eventbus/
│   └── protocol/
│
├── tooling/
├── scripts/
└── docs/
```

Electron Structure
```
apps/desktop/
├── electron/
│   ├── main/
│   ├── preload/
│   └── ipc/
│
├── src/
│   ├── app/
│   ├── workspace/
│   ├── extensions/
│   ├── services/
│   └── state/
```

Go Backend Structure

Keep it domain-driven.
```
apps/backend/
├── cmd/
│   └── server/
│
├── internal/
│   ├── api/
│   ├── ws/
│   ├── agents/
│   ├── extensions/
│   ├── eventbus/
│   ├── storage/
│   ├── auth/
│   └── jobs/
│
├── pkg/
└── configs/
```

## Extension Architecture

This is the most important part.

Design extensions as:
```
Extension =
    frontend module
    + backend module
    + manifest
```

Recommended Extension Structure
```
extensions/notes/
├── manifest.json
├── frontend/
│   ├── pages/
│   ├── components/
│   ├── routes.ts
│   └── index.ts
│
├── backend/
│   ├── handlers.go
│   ├── events.go
│   ├── service.go
│   └── migrations/
│
└── shared/
    ├── types.ts
    └── events.ts
```

Extension Manifest Example
```
{
  "id": "notes",
  "name": "Notes",
  "version": "1.0.0",
  "frontend": {
    "entry": "frontend/index.ts"
  },
  "backend": {
    "module": "backend"
  },
  "permissions": [
    "storage",
    "workspace"
  ],
  "routes": [
    "/notes"
  ]
}
```

Frontend Extension Loading

Use dynamic imports:
```ts
const extension = await import(extensionPath)
```

Each extension registers:
* routes
* panels
* commands
* widgets
* settings pages

Like:
```ts
registerExtension({
  routes: [],
  commands: [],
  panels: [],
})
```

Backend Extension Runtime

Your Go backend should have an extension registry:
```go
type Extension interface {
    ID() string
    RegisterRoutes(r chi.Router)
    RegisterEvents(bus EventBus)
    Start(ctx context.Context) error
}
```

At startup:
```go
LoadExtensions()
RegisterRoutes()
RegisterEventHandlers()
```

### Communication Among Extensions

This is where many apps become messy.

DO NOT let extensions directly call each other.

Instead use:
* event bus
* command bus
* shared state contracts

Recommended Model
```
Extension A
     │
     ▼
 Publish Event
     │
     ▼
 Global Event Bus
     │
     ▼
Extension B subscribes
```

Example

Notes extension publishes:
```json
{
  "event": "note.created",
  "payload": {
    "id": "123"
  }
}
```

Calendar extension listens:
```go
Subscribe("note.created")
```

Now extensions stay decoupled.

Event Bus Design

You want:

Internal Backend Event Bus

In Go:
```go
type Event struct {
    Type string
    Payload any
}
```

Could use:
* channels
* pub/sub
* NATS (later)
* Redis streams (later)

Initially:
* in-memory pub/sub is enough

Frontend Event Bus

React side:
* Zustand
* RxJS
* EventEmitter
* custom pub/sub

I strongly recommend:
Backend = authoritative events
Frontend = reactive projections

Recommended Extension Capabilities

Each extension can contribute:

Capability	| Example
-|-
Routes | `/notes`
Sidebar items | Notes icon
Commands | Create Note
AI tools | summarize note
Context menus | right-click actions
Background jobs | sync
Panels/widgets | dashboard
Search providers | unified search

AI Agent Architecture

Do NOT embed agent orchestration into extensions directly.

Instead:
```
AI Core
 ├── memory
 ├── tools
 ├── model routing
 ├── embeddings
 └── workflows
```

Extensions expose tools to AI.

Example:
```
type Tool interface {
    Name() string
    Execute(ctx context.Context, input any) (any, error)
}
```

Notes extension:
* search notes
* create note
* summarize note

Calendar:
* create event
* query schedule

This becomes extremely scalable later.

Persistence Recommendation
Use:
* SQLite locally initially
* optionally Postgres later

For local-first desktop apps:
* SQLite is ideal

Recommended:
* modernc.org/sqlite
* sqlc
* gorm only if you prefer speed over type safety

Security Recommendations

Very important for Electron.

Enable:
* `contextIsolation: true`
* `sandbox: true`
* disable remote module
* strict preload APIs

Expose ONLY safe APIs:
```ts
contextBridge.exposeInMainWorld("native", {
  openFileDialog,
})
```

Do not expose raw IPC.

Electron security architecture matters a lot at scale.  ￼

Packaging Strategy

Bundle:
* Electron app
* Go backend binary

Electron launches Go process on startup:
```ts
spawn("./backend/xyan-server")
```

Then:
* health check
* connect WS
* app ready

This is a very common architecture for hybrid desktop apps.  ￼

Tech Stack Recommendations

Frontend
* React
* TypeScript
* Vite
* Zustand
* TanStack Query
* Tailwind
* shadcn/ui

Electron
* electron-vite
* electron-builder

Backend
* Go
* Chi
* Coder WebSocket
* SQLite
* sqlc

Most Important Long-Term Decision

The biggest architectural win:

**Make extensions first-class citizens from day 1.**

Meaning:
* frontend extensions
* backend extensions
* event system
* permissions
* contribution APIs

Do NOT hardcode Notes/Kanban/Calendar into the core app.

Treat them exactly like third-party plugins.

That is what enables:
* scalability
* marketplace later
* AI tool ecosystem
* team development
* independent feature shipping

A very good reference model to study is:
* Visual Studio Code extension host architecture
* Eclipse Theia plugin system
* Docker Desktop extension architecture  ￼
