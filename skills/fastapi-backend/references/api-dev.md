# General workflows to develop an API

`DB -> Schema -> Service -> Routers`

1. Database Models (SQLAlchemy)
Define your DB structure.
2. Pydantic Schemas (validation & serialization)
Separate schemas for:
    * Create
    * Update
    * Read (response)
3. Repository / CRUD layer (DB access) (Optional)
Use only when the project is complex enough to warrant a separate layer.
4. Service layer (business logic)
This is where you:
    * Validate business rules
    * Orchestrate workflows
    * Call ML pipelines
5. Routers (API endpoints)
A thin layer that defines the API endpoints. No business logic here
6. Background tasks / workers (if needed)
7. Dependencies (auth, db session, etc.)
