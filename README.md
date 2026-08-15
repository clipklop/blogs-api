# Blogs API

## Database migrations

Set `DATABASE_URL`, then apply all pending migrations before starting the API:

```shell
uv run alembic upgrade head
```

After changing the SQLAlchemy models, generate and review a new migration:

```shell
uv run alembic revision --autogenerate -m "describe the schema change"
```

Application startup does not create or update database tables.
