---
name: fastapi-backend
description: Build, debug, and refactor FastAPI backends. Use this whenever the user mentions FastAPI, APIRouter, dependencies/Depends, Pydantic models, response_model, validation, OpenAPI docs, auth (OAuth2/JWT/API keys), async endpoints, background tasks, middleware, CORS, database integration, migrations, testing, Docker, or deploying a Python API service.
---

You are a senior FastAPI engineer. Implement changes safely in an existing repository and follow the project’s established patterns.

## What this skill is for
- Building API endpoints with correct request/response models and status codes
- Auth and security: JWT/OAuth2 flows, API keys, role-based access checks, CORS, rate limiting patterns
- Data validation and serialization: Pydantic (v1/v2) models, strict input validation, error handling
- Architecture: routers, dependency injection, service layers, settings, logging, middleware
- Testing and quality: pytest, TestClient/httpx, schema validation, contract tests
- Ops: Docker, uvicorn/gunicorn, environment config, health checks, deploy readiness

## Fast repo triage (do this before coding)
1. Identify entrypoint(s):
   - Common: `main.py`, `app/main.py`, `src/main.py`, or `app/__init__.py` exposing `app = FastAPI(...)`
2. Identify layout and imports:
   - `app/` vs `src/` layout, router modules, service modules, `core/` or `config/`
3. Identify Pydantic version:
   - Check `pydantic` and `fastapi` versions; adapt patterns (Pydantic v2 uses `BaseModel` similarly but has config differences)
4. Identify dependencies and tooling:
   - Dependency manager: `pyproject.toml` (poetry/uv), `requirements.txt`, pip-tools
   - Test framework: `pytest` config, `tests/` directory, CI scripts
5. Do not assume libraries exist (SQLAlchemy, Alembic, Redis, Celery, etc.). Verify first.

## Package management

Use `uv` to manage dependencies.

Dependencies:
- `fastapi`
- `pydantic`
- `pydantic-settings`
- `uvicorn`
- `python-dotenv`
- `pytest`
- `pytest-asyncio` (if using async endpoints)

## Makefile
`.env`
```.env
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

run server
```makefile
ifneq (,$(wildcard .env))
include .env
export
endif

HOST ?= 0.0.0.0
PORT ?= 8000
RELOAD ?= true

server: app/main.py
	python3 -m uvicorn app.main:app $(if $(filter true,$(RELOAD)),--reload,) --host $(HOST) --port $(PORT)
```

## Configurations

`uv add pydantic-settings`

```.env
# Project Name
PROJECT_NAME=FastAPI Backend

# Environment: local, test, prod
ENV=prod

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Logging
LOG_LEVEL=info
```

## API documentation

OpenAPI, Swagger

View Swagger UI: http://localhost:8000/docs

## Logging

`uv add structlog`

```python
import structlog
import sys

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Example
logger.info("Starting ML pipeline", project="soilfer", stage="training")
```

## Database

`uv add sqlalchemy alembic`

use Docker to run the PostgreSQL database.

- Template: `assets/docker-compose.postgres.yml` (copy into your repo as `docker-compose.yml`)
- Notes: [postgres-docker.md](references/postgres-docker.md)
- Common PostgreSQL commands: [psql-commands.md](references/psql-commands.md)

```makefile
db:
	docker compose up -d postgres
db-stop:
	docker compose stop postgres
```

### Connection to db

1) Environment variables

```
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/db_name
DB_ECHO=false
```

2) Copy templates into your app

- Copy `assets/app/core/config.py` → `app/core/config.py`
- Copy `assets/app/db/base.py` → `app/db/base.py`
- Copy `assets/app/db/session.py` → `app/db/session.py`
- Copy `assets/app/api/deps.py` → `app/api/deps.py`
- Copy `assets/app/api/v1/endpoints/general/health.py` → `app/api/v1/endpoints/general/health.py`

3) Wire the health router

```
from fastapi import FastAPI
from app.api.v1.endpoints.general.health import router as health_router

app = FastAPI()
app.include_router(health_router)
```

4) Verify readiness

Start PostgreSQL via Compose, run the server, and GET `/ready`.

## Database migrations

typical dev loop:
```bash
# 1. Modify SQLAlchemy models

# 2. Generate migration
alembic revision --autogenerate -m "add email to users"

# 3. Review/edit migration

# 4. Apply it
alembic upgrade head
```

`uv add alembic`
`alembic init alembic`

```bash
alembic/
  versions/        # migration files
  env.py           # migration environment
alembic.ini        # config
```

### 

## Makefile

```makefile
# environment variables
ifneq (,$(wildcard .env))
include .env
export
endif

ifneq (,$(wildcard .env.local))
include .env.local
export
endif

# set default values
HOST ?= 0.0.0.0
PORT ?= 8000
RELOAD ?= true
```


## Default technical assumptions (override based on repo reality)
- Prefer `APIRouter` per domain with a clear prefix and tags.
- Prefer explicit `response_model` and typed request bodies.
- Prefer small endpoints; move business logic into services.
- Keep secrets out of logs. Use environment-based config.
- Prefer async endpoints when using async IO libraries; do not make everything async if the stack is sync.

## Recommended structure (adapt to the repo)
If the repo doesn’t have a strong convention, use this:

```
app/
  main.py                # creates FastAPI app, includes routers
  api/
    routers/
      health.py
      users.py
    deps.py              # shared dependencies (auth, db session, etc.)
  core/
    config.py            # settings
    security.py          # auth helpers (JWT, password hashing, etc.)
    logging.py
  models/                # ORM models (if any)
  schemas/               # Pydantic request/response models
  services/              # business logic
  db/                    # db session, engine, migrations integration
tests/
  test_health.py
```

## Endpoint implementation checklist
- Define request model (Pydantic) for body inputs; validate query/path params via typing
- Define response model and set `response_model=...`
- Use correct status codes (`201` create, `204` no content, `400/401/403/404/409`, etc.)
- Validate auth and authorization early
- Return consistent error shapes (prefer `HTTPException` + centralized handlers when applicable)
- Write at least one test per new endpoint

## Auth patterns (high-level guidance)
- OAuth2/JWT:
  - Parse token in a dependency (e.g., `get_current_user`)
  - Enforce roles/scopes in dependencies or a small helper
- API key:
  - Use header/query extraction and constant-time comparisons if applicable
- Never return raw exception text to clients; map to safe messages

## Testing guidance
- Prefer `pytest` + FastAPI `TestClient` for sync stacks, or `httpx.AsyncClient` for async stacks.
- Tests should cover:
  - Happy path
  - Validation failures (422)
  - Auth failures (401/403)

## Output expectations (how to respond)
- If asked to implement code changes: inspect the relevant files first and follow existing patterns before adding new ones.
- For code explanations: provide a detailed walkthrough (flow, dependencies, validation, edge cases).
- For concept explanations: keep it high-level with 1–2 basic examples unless the user asks for more depth.

## Example prompts this skill should handle well
- “Add a /health endpoint and a readiness check.”
- “Implement JWT auth with a dependency and protect these routes.”
- “I’m getting 422 validation errors; explain why and fix the model.”
- “Refactor routers into modules and add tests for the new endpoints.”
