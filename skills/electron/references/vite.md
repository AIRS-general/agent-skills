# Vite

A modern frontend build tool that uses native ES modules and ultra-fast hot module replacement to deliver near-instant development startup and updates.

## Project creation

```bash
npm create vite@latest
```
* copies a template (React, Vue, etc.)
* sets up:
    * index.html
    * src/main.tsx
    * config (vite.config.ts)
* installs dependencies

## Dev server

```bash
npm run dev
```
* opens a browser window
* serves the project at `http://localhost:3000`
* watches for changes in the project files
* automatically reloads the browser when changes are detected

Vite does NOT bundle your app like older tools.
It: 
- Uses native ES modules in the browser.
  - Browser requests files like:
  ```
  src/main.tsx
  src/App.ts
  ```
  - each file is served on demand.
- Transforms files on the fly
When the browser requests a module:
  1. Vite intercepts request
  2. Transforms it using:
      * esbuild (very fast)
      * plugins (React, TS, etc.)
  3. Returns valid browser JS
- Hot module replacement
When you edit a file:
  1. Vite detects change
  2. Rebuilds ONLY that module
  3. Pushes update via WebSocket
  4. Browser updates instantly

## Production build

`npm run build`

It uses `rollup` to bundle your app.

Build process:
1. Start from entry (index.html)
2. Build dependency graph
3. Bundle everything into optimized chunks
4. Apply optimizations:
    * tree-shaking
    * code splitting
    * minification

## vite defineConfig


```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron/simple'

export default defineConfig({
  plugins: [
    react(),
  ],
})
```
- react() is a plugin that adds React support to Vite.
- it enables JSX, Fast Refresh, etc. 

Plugins are functions/objects that hook into Vite’s lifecycle to transform code, handle files, or customize behavior.

What plugins actually do?
Plugins can hook into different stages:
1. Dev server (on-the-fly transforms)
* modify files as they’re requested
* enable HMR

2. Build process (Rollup-based)
* bundle transformations
* code optimization

## Vite + React + Electron

Set up the plugins in the `vite.config.ts`
```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import electron from "vite-plugin-electron/simple";

export default defineConfig({
  plugins: [
    react(),
    electron({
      main: {
        entry: "electron/main.ts"
      },
      preload: {
        input: "electron/preload.ts"
      }
    })
  ]
});
```

It automatically builds and runs your **Electron main + preload scripts** alongside **Vite’s dev server**.

## During development (`npm run dev`)

1. Starts Vite dev server
* serves your React app at localhost

2. Builds Electron files (main + preload)
* uses esbuild (fast)
* watches for changes

3. Launches Electron automatically
* opens a window
* points to Vite dev server

4. Handles reloads
* Renderer changes → Vite HMR (instant)
* Main/preload changes → Electron restarts

## During production build (`npm run build`)

1. Builds React app -> dist/
2. Builds Electron main + preload -> dist-electron/
3. Keeps them aligned

Output:
```
dist/              # frontend (Vite build)
dist-electron/     # main + preload
```
