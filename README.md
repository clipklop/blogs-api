# Blogs API

A FastAPI service for blog posts, user accounts, and voting, backed by SQLAlchemy
and PostgreSQL. Database schema changes are managed with Alembic.

Local development requires Python 3.14 or later. The Docker image uses Python 3.14.

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
credentials return `401` on protected routes.

## Posts

`GET /posts/` accepts these optional query parameters:

| Parameter | Default | Values |
| --- | --- | --- |
| `limit` | `20` | `1` through `100` |
| `offset` | `0` | Any nonnegative integer |
| `scope` | `public` | `public` or `mine`. Use a bearer token for `mine`. |
| `state` | All states visible in the chosen scope | `published` for public scope. `draft`, `published`, or `archived` for `mine`. |
| `search` | No filter | Case-insensitive literal substring in title or content |
| `tag` | No filter | Exact normalized tag name |
| `author_id` | No filter | Author ID from `1` through `2147483647` |
| `sort` | `newest` | `newest` or `oldest`, with ID as the timestamp tie-breaker |

For example, `/posts/?scope=mine&state=draft&search=python` lists your matching drafts.
The API rejects the `published` query parameter with `422`.

Post responses include a unique slug. New slugs combine a normalized title with
a random suffix and stay stable when the title changes. Public lists and anonymous
slug lookups show published posts. Authors can read their own drafts and archives
using `scope=mine` or an authenticated slug or numeric ID lookup. Numeric lookup
requires authentication, and private posts return `404` to non-authors.

Create, update, and delete require authentication; only the owner may update or
delete a post. Attempts to modify another author's published post return `403`.
PATCH requires at least one supported field and rejects explicit nulls. Successful
DELETE returns `204` with an empty body. Voting requires a published post.

New posts start as drafts. Set the state with `PUT /posts/{post_id}/publication`
and a body such as `{"state":"published"}`. Authors can unpublish to draft or
archive a draft or published post. Restore an archive to draft before publishing
again. Responses include `state` and `published_at`, the UTC time of first
publication, which stays the same on later edits and republication.

Post responses include a sorted `tags` array. Authors can replace a post's tags
with `PUT /posts/{post_id}/tags` and a body such as `{"tags":["Python","Fast-API"]}`.
Send `{"tags":[]}` to clear them. The API accepts up to ten entries, trims whitespace,
and lowercases and deduplicates names. Each trimmed name has 1–32 ASCII letters
or digits, with single hyphens allowed between groups. The `tag` filter uses the
same name rules and combines with the other filters before pagination.

## Tests

```shell
uv run pytest -q -p no:cacheprovider
```

Tests use isolated SQLite databases built through Alembic and do not connect to the
database in `.env`. They cover post behavior, validation, database constraints,
authentication, ownership enforcement with real tokens, and migration upgrades,
backfills, and downgrades. Set `PUBLISHING_TEST_POSTGRES_URL` to a disposable
PostgreSQL database to include PostgreSQL migration and row-lock concurrency tests.
