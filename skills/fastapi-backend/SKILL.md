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
- `uvicorn`
- `sqlalchemy`
- `alembic`
- `dependency-injector`
- `python-dotenv`
- `structlog`
- `pydantic`
- `pydantic-settings`
- `uvicorn`
- `python-dotenv`
- `pytest-asyncio` (if using async endpoints)

Dev dependencies:
- `pytest`
- `ruff`
- `httpx`
- `factory-boy` (for test fixtures)
- `faker`
- `mypy`

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

## alembic

**setup alembic**

`uv add alembic`
`alembic init alembic`

```bash
root/
  alembic/
    versions/        # migration files
    env.py           # migration environment
  alembic.ini        # config
```

`env.py` is the runtime entry point that wires Alembic to your database and SQLAlchemy models so migrations can run correctly.

when you run commands like:
```bash
alembic upgrade head
alembic revision --autogenerate
```

Alembic executes `env.py`, which:
1. connects to your database
2. loads your SQLAlchemy models
  - compare DB schema and models
3. define migration execution mode
  - offline: runs migrations without connecting to the database
  - online: runs migrations while connected to the database

`alembic.ini`
- `script_location = %(here)s/alembic`
  - path to alembic migration folder
  - `%(here)s` is the directory where `alembic.ini` is located
- `prepend_sys_path = .`
  - Before running migrations, add the current project directory to `sys.path`.
  - When alembic runs `env.py`, it needs to import your app code
- `sqlalchemy.url = driver://user:pass@localhost/dbname`
  - the database connection string used by Alembic to connect to your database when running migrations
  - DO NOT hardcode this in production, override it in `env.py`
  - use a placeholder `sqlalchemy.url = driver://user:pass@localhost/dbname`
  - Do not leave it empty
  ```py
  from app.core.config import Settings

  settings = Settings()
  config.set_main_option(
      "sqlalchemy.url",
      settings.DATABASE_URL
  )
  ```
  - `.set_main_option` used inside env.py to override values from alembic.ini at runtime

`alembic/env.py`
- override `sqlalchemy.url` in this file
```py
from app.core.config import Settings

settings = Settings()
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL
    )
```
- `target_metadata`, 
  - one of the most important variables in Alembic—it tells Alembic what your current database schema should look like based on your SQLAlchemy models.
  - it points to the SQLAlchemy metadata object, which contains:
    - all tables
    - columns
    - constraints
    - relationships
  - alembic uses `target_metadata` for: `alembic revision --autogenerate`. it compares:
    - database schema (current state)
    - `target_metadata` (your models)
  - then generates migration scripts based on the differences.
  ```py
  from app.db.base import Base

  target_metadata = Base.metadata
  ```


Migration offline and online
- online: Alembic connects to the database and applies changes directly.
in `env.py`
```py
def run_migrations_online():
    ...
```
when you run `alembic upgrade head`
alembic:
- connects to DB
- runs SQL immediately
- updates schema
- records version in alembic_version

- offline: Alembic does NOT connect to a database. Instead, it generates raw SQL scripts.
in `env.py`
```py
def run_migrations_offline():
    ...
```
when you run `alembic upgrade head --sql`. alembic output raw SQL scripts. e.g. `ALTER TABLE users ADD COLUMN name VARCHAR;`

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
    v1/
      health.py
      users.py
    deps.py              # shared dependencies (auth, db session, etc.)
  core/
    config.py            # settings
    security.py          # auth helpers (JWT, password hashing, etc.)
    logging.py
  schemas/               # Pydantic request/response models
  services/              # business logic
  db/                    # db session, engine, migrations integration
    models/              # ORM models (if any)
    base.py              # Alembic base model
    session.py           # db session factory
alembic/                 # Alembic migration scripts
  versions/              # Alembic version files
  env.py                 # Alembic environment file
tests/
  test_health.py
alembic.ini              # Alembic configuration file
project.toml
docker-compose.yml       # Docker Compose file for DB, Server, etc.
Makefile                 # Makefile for common tasks
```

## Formatting

`ruff` is a very fast Python tool that formats code, sorts imports, and checks for linting errors all in one.

configure ruff in `project.toml`
```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I"]
```

### Issues

E501: Line too long

B008: warns against using function calls as default values for function parameters, because those expressions are evaluated at function definition time (import time), not at runtime.
```py
def func(x=Depends(get_x)):
    ...
```
- `Depends(get_x)` is a function call.
- It sits in a default argument.
- Python evaluates default arguments at import time. 

Fix: Annotated
Annotated fixes the B008 issue because it removes the function call from the default argument position entirely and instead stores dependency metadata in the type system, which frameworks like FastAPI interpret at runtime.

```py
from typing import Annotated
from fastapi import Depends

def health(logger: Annotated[Logger, Depends(get_logger)]):
    ...
```
- No function call in default argument
- It becomes metadata attached to the type
- Python does NOT execute it during function definition

How does FastAPI use Annotated?
FastAPI explicitly inspects Python type annotations at runtime and parses Annotated metadata using its dependency system.

Step-by-step explanation:
When FastAPI loads your endpoint, it 
1. Reads function signature
Using Python introspection: `inspect.signature(endpoint)`
It gets:
* parameter name: `user`
* annotation: `Annotated[str, Depends(get_user)]`

2. Detects Annotated
FastAPI checks: `typing.get_origin(annotation) is Annotated`
Then extract metadata: `get_args(annotation)`
Result:
- `str`
- `Depends(get_user)`

3. Detects `Depends(...)`
FastAPI recognizes Depends objects via:
* internal marker class Depends: `isinstance(metadata_item, Depends)`

4. Registers dependency
It stores the `get_user` dependency and builds a dependency graph.

5. Executes at request time
When a request hits the endpoint, FastAPI:
* resolves dependencies
* calls get_user()
* injects result into user

B904: Within an except block, raise exceptions using raise ... from err

Bad example:
```py
try:
    do_something()
except ValueError as e:
    raise RuntimeError("Failed")
```
* Original exception (ValueError) is lost
* Debugging becomes harder

```py
try:
    do_something()
except ValueError as e:
    raise RuntimeError("Failed") from e
```
- Preserves original error context
- Improves debugging
- Makes error flow explicit

You can intentionally suppress chaining:
```py
raise RuntimeError("Clean error") from None
```
* you don’t want internal details exposed
* you’re sanitizing errors for external APIs

Case | Meaning
-|-
`raise X` | lose original error
`raise X from e` | preserve cause (best practice)
`raise X from None` | hide original cause

## Endpoint implementation checklist
- Define request model (Pydantic) for body inputs; validate query/path params via typing
- Define response model and set `response_model=...`
- Use correct status codes (`201` create, `204` no content, `400/401/403/404/409`, etc.)
- Validate auth and authorization early
- Return consistent error shapes (prefer `HTTPException` + centralized handlers when applicable)
- Write at least one test per new endpoint

## lifespan context manager

lifespan is a mechanism that lets you define **startup** and **shutdown** logic for your application in a single, clean context manager.

It replaces the older `@app.on_event("startup")` and `@app.on_event("shutdown")` approach.

Lifespan = the full lifetime of your FastAPI app:
* startup (app begins running)
* running (serving requests)
* shutdown (app stops)

```py
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("App starting...")

    yield  # app runs here

    # Shutdown code
    print("App shutting down...")
```


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

## Background job architecture
**Typical follow**
1. Client calls /run-job
2. FastAPI:
- create job ID
- pushes task to queue
- returns {job_iod }
3. Worker:
- Runs the job
- Save results
4. Client pools /jobs/{job_id} or uses websocket

**Architecture**
1. API layer:
- FastAPI handles HTTP
- validates input
- creates a job
2. Task queue: Celery
- stores job in database
- pushes task to queue
3. Broker/Queue
- Redis
4. Workers
- Separate processes/containers
5. Result storage
- DB (PostgreSQL)
- File storage (S3)
