# Agent Skills

A collection of reusable agent skills for software engineering workflows. Each skill lives in its own folder and is defined by a `SKILL.md` file (plus optional `assets/` templates and `references/` notes).

## Skill layout

- `*/SKILL.md`: the skill definition (name, trigger description, and instructions)
- `*/assets/`: copy-ready templates and scaffolds used by the skill
- `*/references/`: longer notes, checklists, and supporting docs referenced from `SKILL.md`

## Skills in this repo

In the `skills/` folder:

- `electron/`: Electron desktop app development (architecture, IPC, packaging, debugging)
- `fastapi-backend/`: FastAPI backend development (project setup, config, DB patterns, migrations, ops)
- `go-backend/`: Go backend development (APIs/services)
- `nextjs-web-dev/`: Next.js web development (project structure, app router patterns)
- `liscences/`: open source license management (license selection, applying LICENSE/NOTICE, templates)

## How to use

1. Open the skill folder you want.
2. Read `SKILL.md` to see when it should trigger and how it should operate.
3. If your agent/IDE supports “skills”, install the folder into its skills directory (keeping the folder name and `SKILL.md` intact).

## Conventions

- Keep `SKILL.md` focused on workflow and decision guidance; put long snippets in `references/`.
- Put copy/paste templates in `assets/` (scaffolds, example configs, license texts).
- Avoid hard-coding secrets in templates; use environment variable placeholders instead.

## Dependencies

Claude `skill-creator`
