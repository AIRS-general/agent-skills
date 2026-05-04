# Xyan overview

```
Electron App (Frontend + Host)
├─ Main Process (Electron)
│   ├─ Window & Menu Management
│   ├─ Extension Manager (load/unload extensions)
│   └─ IPC / RPC to Go backend
├─ Renderer Process (React + Tailwind)
│   ├─ Chat UI (GPT-style interface)
│   ├─ Extensions UI
│   └─ Extension Loader / Webview host
└─ Go Backend (local server)
    ├─ Chat Session Management
    ├─ Message History (LevelDB / SQLite)
    └─ Extension API endpoints
```

## Tack stack 

Layer | Technology
-|-
Electron Host | Node.js + Electron
Renderer UI | React + Tailwind CSS + shadcn/ui
Backend AI | Golang + LevelDB/SQLite
Extensions | Python + optional React webview
IPC/Communication | HTTP (localhost) or WebSocket

- Use websocket for chats
- RPC for extension APIs
