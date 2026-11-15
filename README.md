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

The migration history includes the original posts table, users, post ownership,
votes, and unique indexed post slugs. The foundation migration preserves existing
posts and votes, gives existing posts a slug ending in their ID, and replaces null
content with an empty string before making content non-nullable. Legacy posts may
retain an unknown (`null`) owner.

The previously incomplete historical migrations have been repaired so a fresh
database can be initialized. Databases already stamped at the previous head
(`7b40c5d184a2`) apply only the new foundation migration. An existing schema without
an Alembic revision needs its schema reviewed before choosing a baseline; do not
stamp it blindly.

## Posts

`GET /posts/` accepts these optional query parameters:

| Parameter | Default | Values |
| --- | --- | --- |
| `limit` | `20` | `1` through `100` |
| `offset` | `0` | Any nonnegative integer |
| `published` | No filter | `true` or `false` |
| `search` | No filter | Case-insensitive literal substring in title or content |
| `sort` | `newest` | `newest` or `oldest`, with ID as the timestamp tie-breaker |

For example: `/posts/?published=true&search=python&sort=oldest&limit=10&offset=0`.

Post responses include a unique slug. New slugs combine a normalized title with
a random suffix and stay stable when the title changes. Public lookup is available
at `GET /posts/slug/{slug}`; numeric ID lookup continues to require authentication.
Draft visibility restrictions belong to Phase 3 and are not yet implemented.

Create, update, and delete require authentication; only the owner may update or
delete a post. PATCH requires at least one supported field and rejects explicit
nulls. Successful DELETE returns `204` with an empty body.

## Tests

```shell
uv run pytest -q -p no:cacheprovider
```

Tests use isolated SQLite databases built through Alembic and do not connect to the
database in `.env`. They cover post behavior, validation, database constraints,
and migration upgrades, backfills, and downgrades. PostgreSQL deployment validation
should also run migrations against a disposable PostgreSQL database.
