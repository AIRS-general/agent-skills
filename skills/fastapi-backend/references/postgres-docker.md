## PostgreSQL via Docker Compose

Use the template at `assets/docker-compose.postgres.yml` and copy it into your app repo as `docker-compose.yml`.

### Volume mount note (PostgreSQL 18+)

- If using PostgreSQL >= 18, volume mount should be `/var/lib/postgresql`.
- For earlier versions, it should be `/var/lib/postgresql/data`.

### Start/stop

```bash
docker compose up -d postgres
docker compose stop postgres
```

### Useful commands

Common PostgreSQL commands are in [psql-commands.md](psql-commands.md).
