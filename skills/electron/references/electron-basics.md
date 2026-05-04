# Electron basics

## Multi-process architecture (the foundation)

It is a multi-process desktop runtime built on Chromium + Node.js.

### 3 key processes 

1. Main process
- Single entry point (`main.ts`)
- Controls:
  - app lifecycle
  - windows
  - native OS APIs
  - menus, tray, shortcuts
- Has full Node.js access

2. Renderer process
- Each window = one Chromium tab process
- Runs your UI (React, Vue, etc.)
- Web APIs only (DOM, fetch, etc.)

3. Preload script
- Bridge between main <--> render
- Runs in renderer context but has Node access
- Uses contextBridge 

## Security model

Most Electron apps are insecure by default if you’re not careful.

Key rule: Never expose Node.js directly to renderer.

Must-enable settings
```ts
webPreferences: {
  contextIsolation: true,
  nodeIntegration: false,
  preload: ...
}
```
Preload bridge pattern
```ts
import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("api", {
  send: (msg: string) => ipcRenderer.send("msg", msg)
});
```

Renderer can only access controlled APIs.

## IPC
Used for communication between processes:
- `ipcMain` (main process)
- `ipcRenderer` (renderer process)

Example:
```ts
// renderer (with proper typing on window.api)
window.api.send("save-data", data);
```
```ts
// main
import { ipcMain } from "electron";

ipcMain.on("save-data", (event, data: unknown) => {
  // handle filesystem, DB, etc.
});
```

## App lifecycle management

Must understand:
* `app.whenReady()`: A promise that resolves when Electron finished initializing. Create windows, menus, tray, register IPC, etc. after this (not at module load time).
* `app.on("window-all-closed")`: Fires when all windows are closed. Typical behavior:
  - Windows/Linux : quit the app.
  - macOS : keep the app running (so it can reopen from the dock).
example:
  ```ts
  import { app } from "electron"

  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit()
  })
  ```
* `app.on("activate")`: macOS-specific-ish UX: fired when the user clicks the dock icon (or switches back to the app). Commonly used to re-create a window if none exist.
Example:
  ```ts
  import { app, BrowserWindow } from "electron"

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      // createWindow()
    }
  })
  ```

## BrowserWindow mastery

Must understand:
```ts
import { BrowserWindow } from "electron";

new BrowserWindow({
  width,
  height,
  webPreferences
});
```
Advanced concerns:
* multiple windows (multi-window apps like VS Code)
* hidden windows (background tasks)
* window persistence (restore sessions)

## Packing and distribution

Must know:
* dev vs prod bundling
* ASAR archives
* code signing (macOS / Windows)
* auto-updates

Tool: `electron-builder`

## Performance model

Electron apps fail in production mostly due to performance mistakes.

Key concepts:
Renderer process is expensive
* each window = memory + CPU

Avoid:
* heavy computation in renderer
* large DOM trees
* unbounded re-renders (React issues)

Use:
* background main process tasks
* worker threads (Node)
* separate backend service (Go/Python)

## Native capabilities

Electron gives access to OS features:
* file system
* clipboard
* notifications
* global shortcuts
* tray icons
* system dialogs

Electron is most powerful when used **as a system integration layer**, not just a UI shell.

## Data flow architecture (critical for large apps)

Good Electron apps separate concerns:
```
React (UI)
   ↓ IPC
Preload (API boundary)
   ↓ IPC
Main process (business logic)
   ↓
DB / filesystem / external services
```

## State management strategy
You must choose:
* local UI state (React)
* global app state (Zustand / Redux)
* persistent state (SQLite / file / IndexedDB)

## Persistence layer

Common options:
* SQLite (best default)
* IndexedDB (simple apps)
* flat JSON files (lightweight tools)

For production desktop apps: SQLite is the standard.

## Native module ecosystem

Electron supports Node native modules:
* fs-extra
* better-sqlite3
* sharp
* node-ffi (advanced OS calls)

## Architecture patterns in real Electron apps

1. Modular window architecture
* each feature = window or view

2. Micro-frontend style inside renderer
* plugins/extensions (VS Code style)

3. Backend-in-main-process pattern
* main process behaves like a local server

## app

`import { app } from "electron"`
- only available in the main process
- not accessible directly in the renderer

`app` is the core module and entry point that controls your application’s lifecycle and global behavior

1. Application lifecycle
Controls when your app:
- starts
- becomes ready
- quits

2. System-level behavior
- app name
- paths (user data, cache, etc.)
- OS integration

3. Global events
- window creating timing
- app activation (macOS)
- shutdown handling

Lifecycle flow:
`App starts → app.whenReady() → create windows → user interacts → app quits`

### Important methods

`app.whenReady()`: Ensures Electron is fully initialized before creating windows.
```ts
app.whenReady().then(() => {
  createWindow();
});
```

`app.quit()`: Closes the entire application

### Important events

`window-all-closed` 
```ts
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
```

macOS apps usually stay open even with no windows.

`activate(macOS)`
```ts
app.on("activate", () => {
  createWindow();
});
```
Reopen window when clicking dock icon.

Full example:
```ts
import { app, BrowserWindow } from "electron";

function createWindow(): void {
  new BrowserWindow({
    width: 1200,
    height: 800,
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
```

## browserWindow

BrowserWindow is the module used to create and control application windows (the UI containers that display your web app).

Key configuration:
```ts
const win = new BrowserWindow({
  width: 1200,
  height: 800,
  webPreferences: {
    preload: "/path/to/preload.js",
    contextIsolation: true,
    nodeIntegration: false,
  },
});
```
* `contextIsolation: true` -> separates renderer from Node
* `nodeIntegration: false` -> prevents direct Node access
* `preload: "/path/to/preload.js"` -> sets up controlled API bridge

This is your security boundary.

### Loading content

Dev mode: `win.loadURL("http://localhost:5173")`
Production: `win.loadFile("dist/index.html")`

### window control

```ts
win.show();
win.hide();

win.setSize(800, 600);

win.close();

win.on("closed", () => {
  // cleanup
});
```

### Communication

BrowserWindow connects to renderer via IPC:

```ts
win.webContents.send("event", data);
```

## Main process

`main.ts` runs the app logic.
- Creates windows
- Handles business logic
- Interacts with external services
- Manages state

## Preload

`preload.ts` sets up the API bridge between the **renderer** (UI) and **main process**.

```ts
import { ipcRenderer, contextBridge } from 'electron'
```

`ipcRenderer` and `contextBridge` are part of how your frontend (renderer process) safely talks to your backend (main process).

1. `ipcRenderer` — communication **from renderer -> main**

`ipcRenderer` is a module that lets your UI (React, plain JS, etc.) *send messages to the main process and receive responses*.

Common use cases:
* Read/write files
* Access OS APIs
* Trigger long-running tasks

Example:
Renderer (frontend):
```ts
import { ipcRenderer } from 'electron'

// send message
ipcRenderer.send('read-file', '/path/to/file')

// receive response
ipcRenderer.on('file-content', (_, data) => {
  console.log(data)
})
```
Main process:
```ts
import { ipcMain } from 'electron'
import fs from 'fs'

ipcMain.on('read-file', (event, path) => {
  const content = fs.readFileSync(path, 'utf-8')
  event.reply('file-content', content)
})
```

2. `contextBridge` - secure API exposure
By default, modern Electron apps run with:
* `contextIsolation: true`
* Node.js APIs not directly available in the renderer

It allows you to **safely expose a controlled API from preload -> renderer**.

Without it, doing this is dangerous
```ts
// ❌ BAD: exposes full Node.js
window.require('fs')
```

Instead, you expose only what you want.
```ts
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('api', {
  readFile: (path: string) => ipcRenderer.invoke('read-file', path),
})
```

Renderer usage:
```ts
// now safely available
const content = await window.api.readFile('/path')
console.log(content)
```

The workflow:
```
Renderer (React UI)
    ↓
window.api.readFile()   ← exposed via contextBridge
    ↓
ipcRenderer.invoke()
    ↓
Main process (ipcMain.handle)
    ↓
OS / Node.js (fs, etc.)
    ↓
Result back to renderer
```

### core communication primitives of `ipcRenderer`

```ts
ipcRenderer.send('read-file', '/path/to/file')
ipcRenderer.on('file-content', (_, data) => {
  console.log(data)
})
ipcRenderer.off('file-content')

ipcRenderer.invoke('read-file', '/path/to/file')
```

Event-based (push/listen): send, on, off

Request-response (async call): invoke

1. send -> file-and-forget
```ts
ipcRenderer.send('channel', ...args)
```
Sends a message to the main process without expecting a return value.

Example:
```ts
// renderer
ipcRenderer.send('log-message', 'hello')
```
```ts
// main
ipcMain.on('log-message', (_, msg) => {
  console.log(msg)
})
```

2. on -> listen for events
```ts
ipcRenderer.on(channel, listener)
```
Registers a listener for messages coming from the main process.

Example:
```ts
// renderer
ipcRenderer.on('file-updated', (_, data) => {
  console.log(data)
})
```
```ts
// main
event.sender.send('file-updated', { changed: true })
```

3. off -> remove listener
```ts
ipcRenderer.off(channel, listener)
```
Removes a previously registered listener.

Example:
```ts
const handler = (_: any, data: any) => console.log(data)

ipcRenderer.on('event', handler)

// later, remove the listener
ipcRenderer.off('event', handler)
```

4. invoke -> async request-response (modern way)
```ts
ipcRenderer.invoke('channel', ...args)
```
Sends a message and waits for a result (Promise-based).

```ts
// renderer
const content = await ipcRenderer.invoke('read-file', '/path')
```
```ts
// main
ipcMain.handle('read-file', async (_, path) => {
  return fs.readFileSync(path, 'utf-8')
})
```

use `.invoke()` for most things.

Expose these primitives in `preload.ts` to `contextBridge` could be risky.
