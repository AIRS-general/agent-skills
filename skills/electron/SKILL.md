---
name: electron-desktop-dev
description: Build, debug, and package Electron desktop apps. Use this whenever the user mentions Electron, main process, renderer process, preload scripts, IPC, contextIsolation, sandbox, BrowserWindow, native menus, auto-update, code signing, installers (DMG/MSI), electron-builder, electron-forge, Vite/Webpack in Electron, or diagnosing desktop-only issues like crashes, blank windows, and IPC security.
---

You are a senior Electron engineer. Help the user ship a secure, maintainable desktop app across macOS/Windows/Linux.

## Create an electron app with React

Using vite + React

1. create project
```bash
npm create vite@latest my-app
```
Then:.
```bash
cd my-app
npm install
```

2. Install electron + helpers
```bash
npm install electron
```
Optional: install `electron-builder` for packaging.
```bash
npm install electron-builder
```

## How does vite run the electron app?

When you run `npm run dev`, vite starts the React app in a browser window created by Electron.

1. `package.json`
```json
"scripts": {
   "dev": "vite",
}
```
- `npm run dev` runs vite using config in `vite.config.ts`.

2. `vite.config.ts`
```ts
export default defineConfig({
  plugins: [
    react(),
    electron({
      main: {
        entry: 'electron/main.ts',
      },
      preload: {
        input: path.join(__dirname, 'electron/preload.ts'),
      },
      renderer: process.env.NODE_ENV === 'test'
        ? undefined
        : {},
    }),
  ],
})
```

## Project structure

```
my-app/
├── electron/
│   ├── main.js
│   └── preload.js
├── src/              # React app
├── index.html
├── package.json
```

## Architecture

Renderer (React)
- UI only
- state, components, chat interface

Main process (Electron)
- file system
- window management
- OS integration

Communication vai:
- Inter-Process Communication (PC) managed by Electron
- or local HTTP/WebSocket server

```
┌──────────────────────────────┐
│        Electron Shell        │
│  (window, IPC entry point)   │
└─────────────┬────────────────┘
              │ IPC
┌─────────────▼────────────────┐
│        Core Runtime          │  ← brain
│ (Node.js or Go bridge layer) │
│                              │
│  - Extension Manager         │
│  - Agent Manager             │
│  - Event Bus                 │
│  - Permissions               │
└───────┬───────────┬──────────┘
        │           │
   ┌────▼────┐  ┌───▼────────┐
   │Frontend │  │ Extensions │
   │ React   │  │ (sandboxed)│
   └─────────┘  └────┬───────┘
                     │
               ┌─────▼──────┐
               │ Agents     │
               │ Python/Go  │
               └────────────┘
```

## Folder structure

```
my-app/
├── apps/
│   ├── desktop/                # Electron main process
│   ├── web/                    # React frontend (Vite)
│
├── core/                       # Platform runtime
│   ├── extension/
│   │   ├── manager.ts
│   │   ├── sandbox.ts
│   │   └── api.ts
│   │
│   ├── agent/
│   │   ├── manager.ts
│   │   ├── python_bridge.ts
│   │   └── go_bridge.ts
│   │
│   ├── ipc/
│   │   ├── channels.ts
│   │   └── handlers.ts
│   │
│   ├── event-bus/
│   │   └── index.ts
│   │
│   └── permissions/
│       └── index.ts
│
├── extensions/                 # local extensions (dev)
│   ├── chat-tools/
│   ├── kanban/
│   └── email/
│
├── agents/
│   ├── python/
│   └── golang/
│
├── packages/                   # shared libs
│   ├── ui/
│   ├── types/
│   └── sdk/                    # extension SDK
│
├── build/                      # electron-builder config
└── package.json
```

## Project structure

```
my-app/
├── package.json
├── tsconfig.json
├── electron.vite.config.ts   # or vite config
├── /extensions   # user installed or built-in plugins
│  ├── /core                  # First party extensions
│  ├── /installed             # user installed
│  │   ├── extension-a/      # ipcMain.handle
│  │   │   ├── manifest.json           # app entry
│  │   │   ├── main.ts           # basic logic
│  │   │   ├── renderer.ts       # app entry
│  │   │   └── assets/     # ipcMain.on
│  │   └── extension-b/
├── /src
│
│  ├── /main                  # Electron main process
│  │   ├── index.ts           # app entry
│  │   ├── window.ts          # BrowserWindow setup
│  │   ├── ipc/
│  │   │   ├── handlers/      # ipcMain.handle
│  │   │   └── listeners/     # ipcMain.on
│  │   ├── extensions/             # app state (optional)
│  │   │   ├── loader.tsx
│  │   │   ├── sandbox.tsx
│  │   │   └── registry.tsx
│  │   ├── services/          # business logic (Node side)
│  │   ├── store/             # app state (optional)
│  │   └── utils/
│
│  ├── /preload               # secure bridge
│  │   └── index.ts           # contextBridge.exposeInMainWorld
│
│  ├── /renderer              # React app
│  │   ├── index.html
│  │   ├── main.tsx
│  │   │
│  │   ├── /app               # app-level config
│  │   │   ├── App.tsx
│  │   │   ├── routes.tsx
│  │   │   └── providers.tsx
│  │   │
│  │   ├── /features          # 🔥 domain-driven modules
│  │   │   ├── chat/
│  │   │   │   ├── components/
│  │   │   │   ├── hooks/
│  │   │   │   ├── api.ts
│  │   │   │   └── types.ts
│  │   │   ├── settings/
│  │   │   └── ...
│  │   │
│  │   ├── extensions/             # app state (optional)
│  │   │   ├── ExtensionHost.tsx
│  │   │   └── hooks/
│  │   ├── /components        # shared UI
│  │   ├── /hooks             # shared hooks
│  │   ├── /lib               # helpers (axios, utils)
│  │   ├── /store             # Zustand/Redux
│  │   ├── /styles
│  │   └── /types
│
│  ├── /shared                # 🔥 shared types/contracts
│  │   ├── ipc.ts             # IPC channel definitions
│  │   └── types.ts
│
├── /assets
└── /dist
```


## IPC Design

```
React UI
   ↓
Electron IPC (preload bridge)
   ↓
Core Runtime
   ↓
Extension / Agent
```

## Extension system

```
extensions/kanban/
├── manifest.json
├── index.ts
└── ui/
```

manifest.json
```json
{
  "name": "kanban",
  "version": "1.0.0",
  "permissions": ["storage", "ui"],
  "activationEvents": ["onAppStart"],
  "main": "index.js"
}
```

## Build system
vite -> frontend
electron -> shell
electron-builder -> packaging

## Initial a project

`npx create-electron-app@latest my-app --template=vite-typescript`

## What this skill is for
- Implementing Electron features: windows, menus, tray, deep links, file dialogs, notifications
- Safe IPC and security hardening: preload, `contextIsolation`, `sandbox`, permission gating
- Architecture: main/renderer/preload separation, shared types, structured IPC contracts
- Packaging and distribution: installers, auto-update, code signing/notarization readiness
- Debugging: blank window, devtools, crash logs, native module issues, path issues in production builds

## Fast repo triage (do this before coding)
1. Identify the toolchain:
   - `electron-builder`, `electron-forge`, `@electron/packager`, or a custom script
   - Bundler: Vite, Webpack, Rollup
2. Identify process layout:
   - Main entry: `main.ts` / `main.js` (or `src/main/`)
   - Preload: `preload.ts` / `preload.js` (or `src/preload/`)
   - Renderer UI: `renderer/` or `src/renderer/` (React/Vue/Svelte/etc.)
3. Confirm TypeScript usage and path aliases.
4. Do not assume dependencies exist (auto-updater, state libs, router, etc.). Verify in `package.json` first.

## Default security posture (override only with a clear reason)
- Use `contextIsolation: true`.
- Use a preload script to expose a small, typed API to the renderer via `contextBridge`.
- Avoid enabling `nodeIntegration` in the renderer.
- Keep IPC “allowlisted”: explicit channels, validated payloads, least privilege.
- Treat all renderer input as untrusted.

## Recommended project structure (common, scalable)
```
src/
  main/
    index.ts              # app lifecycle, window creation
    windows/              # window factories (mainWindow, settingsWindow)
    ipc/                  # ipcMain handlers
    services/             # OS-level services (fs, shell, auto-update wrappers)
    security/             # permission gating, protocol handling
  preload/
    index.ts              # contextBridge exposure
    channels.ts           # IPC channel names + types
  renderer/
    app/                  # app shell, routes
    components/
    features/
    styles/
  shared/
    types/                # shared types for IPC and domain models
    validators/           # schema validation (if used)
```

If the repo already has a different structure, follow it and only introduce new folders when clearly needed.

## IPC best practices (how to implement features safely)
1. Define a typed contract in `src/shared/types` or `src/preload/channels.ts`:
   - channel name
   - request payload type
   - response payload type
2. In preload, expose a narrow API:
   - `window.api.someAction(payload)` not `ipcRenderer.send` directly
3. In main, validate inputs and keep handlers small:
   - parse/validate payload
   - call a service function
   - return structured errors

## Packaging and release guidance
- Prefer one packaging tool and stick to its conventions.
- Verify:
  - app icons per platform
  - correct `appId`
  - env/config separation between dev and prod builds
  - platform-specific paths (`app.getPath`, `process.resourcesPath`)
- For macOS distribution:
  - plan for signing/notarization early; avoid last-minute surprises

## Output expectations (how to respond)
- If asked to implement code changes: inspect relevant files first and follow existing patterns.
- For code explanations: provide a detailed walkthrough of main/preload/renderer boundaries and data flow.
- For concept explanations: keep it high-level with 1–2 basic examples unless the user asks for more.
- Prefer TypeScript in Electron examples when the repo uses TypeScript.

## Common Electron pitfalls to proactively check
- Blank window in prod: wrong `loadURL`/file path, missing assets, CSP issues, preload not bundled
- IPC security: overly broad channels, missing validation, exposing Node primitives to renderer
- Wrong paths: assuming `__dirname` works the same after packaging
- Native modules: ABI mismatches, rebuild steps, platform-specific binaries
- Multiple instances and deep links: `app.requestSingleInstanceLock()` flow

## Example prompts this skill should handle well
- “Create a secure IPC bridge to read a file via main process and return contents to the renderer.”
- “My packaged app shows a blank window on macOS but works in dev. Diagnose and fix.”
- “Add auto-update using the repo’s existing tooling and make it work on macOS and Windows.”
- “Refactor IPC into typed contracts and enforce validation on all handlers.”
