# Blogs API

A FastAPI service for blog posts, user accounts, and voting, backed by SQLAlchemy
and PostgreSQL. Database schema changes are managed with Alembic.

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

## Authentication

Register with `POST /users/` using JSON containing `username`, `email`, and `password`.
Usernames and emails must be unique. Passwords use bcrypt hashing and accept 6–71
characters, up to 72 UTF-8 bytes; passwords and hashes are excluded from responses.

Log in with `POST /login` using form fields `username` (the email address) and
`password`. The response contains `access_token` and `token_type: "bearer"`.
Send `Authorization: Bearer <access_token>` on protected requests.
`GET /users/me` returns the authenticated user's profile.

JWT expiry uses UTC and defaults to 30 minutes. Configure `SECRET_KEY`, `ALGORITHM`
(default `HS256`), and `ACCESS_TOKEN_EXPIRE_MINUTES` in the environment. Set a private,
random `SECRET_KEY` before deploying. Missing, expired, invalid, or deleted-user
credentials return `401`; editing another author's post returns `403`.

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
at `GET /posts/slug/{slug}`; numeric ID lookup requires authentication.
The list and slug lookup endpoints expose both published and unpublished posts.

Create, update, and delete require authentication; only the owner may update or
delete a post. PATCH requires at least one supported field and rejects explicit
nulls. Successful DELETE returns `204` with an empty body.

## Tests

```shell
uv run pytest -q -p no:cacheprovider
```

Tests use isolated SQLite databases built through Alembic and do not connect to the
database in `.env`. They cover post behavior, validation, database constraints,
authentication, ownership enforcement with real tokens, and migration upgrades,
backfills, and downgrades. Validate deployment migrations against a disposable
PostgreSQL database as well.
