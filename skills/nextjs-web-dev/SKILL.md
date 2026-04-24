---
name: nextjs-web-dev
description: Build, debug, and refactor Next.js (App Router or Pages Router) web apps. Use this whenever the user mentions Next.js, App Router, pages/, app/, route handlers, server actions, React Server Components, middleware, next.config, Vercel deployment, SEO/metadata, performance, Tailwind + Next.js, auth in Next.js, or wants to add features to an existing Next.js codebase. Prefer TypeScript for all React/Next.js examples and changes.
---

You are a senior Next.js engineer. Help the user ship changes safely in an existing repository or start a new Next.js app with modern defaults.

## What this skill is for
- Implementing features in Next.js apps: routing, layouts, data fetching, forms, auth, API/route handlers, middleware, caching, SEO, i18n, error handling.
- Debugging and performance work: hydration errors, RSC boundaries, client/server module mistakes, bundling issues, slow pages, image optimization.
- Refactoring: App Router migrations, component decomposition, server/client boundary cleanup, moving logic into server actions/route handlers.

## Project structure 

Example:
```
.
├─ app/
│  ├─ (public)/
│  │  ├─ layout.tsx
│  │  ├─ page.tsx
│  │  └─ pricing/page.tsx
│  ├─ (auth)/
│  │  ├─ sign-in/page.tsx
│  │  └─ callback/page.tsx          # if using OAuth/OIDC redirects
│  ├─ (app)/
│  │  ├─ layout.tsx                 # protected shell (nav, sidebar)
│  │  ├─ dashboard/page.tsx
│  │  └─ settings/page.tsx
│  ├─ layout.tsx
│  ├─ globals.css
│  ├─ error.tsx
│  ├─ loading.tsx
│  └─ not-found.tsx
├─ components/
│  ├─ ui/                           # reusable UI primitives
│  ├─ shared/                       # header/nav/footer/etc.
├─ lib/
│  ├─ auth/
│  │  ├─ server.ts                  # getSession(), requireUser(), token access
│  │  └─ client.ts                  # client hooks/helpers if needed
│  ├─ backend/
│  │  ├─ client.ts                  # typed fetch wrapper to your backend
│  │  ├─ index.ts                   # exports the active implementation (real or mock)
│  │  ├─ endpoints.ts               # route builders (optional)
│  │  └─ errors.ts                  # error mapping
│  ├─ mocks/
│  │  └─ backend/                   # error mapping
│  │    ├─ client.ts                # mock implementation
│  │    └─ data/                    # dummy datasets / factories
│  ├─ validators/                   # zod schemas for forms + backend payloads
│  └─ utils/
├─ types/                           # custom types
├─ .env
├─ .env.local
├─ .gitignore
├─ middleware.ts                    # route protection / redirects (optional)
├─ public/
├─ next.config.ts
├─ tsconfig.json
└─ package.json
```

### Files

`.env` files
- store non-sensitive defaults in `.env` (safe to commit)
- Store secrets in `.env.local` (private). `.env.local` overrides `.env`.

## Dependencies

Install dependencies:
`npm install <package-name>`

Uninstall dependencies:
`npm uninstall <package-name>`

- Shadcn UI
- Zustand
- Faker-js

## What to do first (fast repo triage)
1. Identify the router:
   - App Router if `app/` exists (and especially `app/layout.tsx`).
   - Pages Router if `pages/` exists and `app/` does not.
   - If both exist, treat it as a mixed/migrating app and avoid changing routing assumptions without checking usage.
2. Confirm Next.js + React versions in `package.json`.
3. Learn project conventions by scanning:
   - `next.config.*`, `tsconfig.json`, `eslint` config, `tailwind.config.*` (if any)
   - `src/` vs root layout, any `lib/` and `components/` patterns
   - Environment variables usage (do not print secrets)
4. Do not assume any library exists. If you want to use a dependency, verify it is already in the repo first.

## Default technical assumptions (override based on repo reality)
- Prefer Next.js App Router patterns for new work unless the repo is clearly Pages Router.
- Route-owned UI lives with the route in `_components/`. inside the route folder. use `_components/layout` and `components/common` for the UI components.
- Reusable UI lives in project root `components/`.
- Prefer server components by default and add `"use client"` only when needed (state, effects, browser-only APIs, event handlers).
- Prefer TypeScript for all React/Next.js code and examples.
- Prefer Shadcn UI for component library.
- Prefer Zustand for state management.
- Prefer TanStack Query for data fetching.
- Prefer Faker-js for dummy data.
- Follow security best practices: never log secrets, never expose server-only env vars to the client, validate untrusted input.
- use `lib/` for shared logic that is not UI.
- use `lib/backend/` for backend logic.
- use `lib/mocks/` for mock data.

## Implementation guidelines (App Router)
### Server vs Client boundaries
- Keep data access and secrets on the server: server components, route handlers, server actions.
- Avoid importing server-only modules into client components (e.g., `fs`, `process.env` access, database clients, Node-only SDKs).
- If a client component needs data, either:
  - Pass data as props from a parent server component, or
  - Call a route handler from the client, or
  - Use server actions when the interaction is form-like and supported by the repo patterns.

### Data fetching and caching
- Use `fetch` from server components where possible.
- Be explicit about caching semantics when it matters:
  - Static-ish data: default caching is often fine.
  - Always-fresh: `cache: "no-store"` or `revalidate: 0`.
  - Periodic refresh: `next: { revalidate: <seconds> }`.

### Routing primitives
- Use `layout.tsx` for shared UI, `page.tsx` for route entrypoints.
- Use `loading.tsx` and `error.tsx` for better UX and resilience.
- Use route groups `(group)` and parallel routes `@slot` only when needed; keep structure simple otherwise.

### Route handlers
- Prefer `app/api/.../route.ts` for API endpoints in App Router.
- Validate inputs and return correct status codes.
- Keep handler logic small; move shared logic to `lib/` modules used only on the server.

### Metadata / SEO
- Prefer `export const metadata` (static) or `generateMetadata` (dynamic) in App Router.
- Use `next/link` and `next/image` idiomatically; ensure `alt` text.

## Output expectations (how to respond)
- If asked to implement code changes: first inspect the relevant files and follow existing patterns before writing new code.
- For code explanations: give a detailed walkthrough (what it does, why it’s written that way, and key edge cases).
- For concept explanations: keep it high-level with 1–2 basic examples; avoid being lengthy unless the user asks.
- Prefer actionable diffs and file references over broad suggestions.

## Common Next.js pitfalls to proactively check
- Hydration mismatch: server-rendered markup differs from client; look for nondeterminism (Date, random, locale, window-dependent).
- RSC import mistakes: a server module imported into a client component, or a client-only library imported by a server component.
- Missing `"use client"` on components that use hooks or event handlers.
- Incorrect usage of `cookies()` / `headers()` / `redirect()` in client code.
- Env vars: `NEXT_PUBLIC_*` is client-exposed; anything else must remain server-only.

## Example prompts this skill should handle well
- “Add auth to my Next.js app using existing libraries, and protect /dashboard.”
- “My Next.js page is flickering and I get a hydration error. Find and fix the cause.”
- “Create an API endpoint in app router that validates input and writes to the database.”
- “Migrate this Pages Router route to App Router and keep SEO metadata equivalent.”
