# Blog API Roadmap

## Phase 1 — Foundation

- [ ] Add Alembic migrations and remove `Base.metadata.create_all()` from application startup.
- [ ] Add pagination with `limit` and `offset` query parameters.
- [ ] Add filtering by publication status.
- [ ] Add title and content search.
- [ ] Add sorting, including newest and oldest posts.
- [ ] Add unique, indexed post slugs and a public slug-based lookup endpoint.
- [ ] Make SQLAlchemy model nullability consistent with the Pydantic schemas.
- [ ] Return an empty response body from successful `204 No Content` endpoints.
- [ ] Validate PATCH requests so empty updates and invalid `null` values are rejected.
- [ ] Add tests for CRUD operations, validation, missing posts, pagination, and filtering.

Acceptance criteria: database changes are migration-driven, list endpoints are bounded and searchable, API schemas match stored data, and core post behavior has automated test coverage.

## Phase 2 — Users and Authentication

- [ ] Add user registration with securely hashed passwords.
- [ ] Add login and JWT authentication.
- [ ] Add a `GET /users/me` endpoint.
- [ ] Associate every post with an author.
- [ ] Allow only the author to update or delete a post.
- [ ] Add authentication and authorization tests.

Acceptance criteria: authenticated users can manage their own posts, while unauthorized users cannot modify posts owned by others.

## Phase 3 — Content Features

- [ ] Add tags with a many-to-many relationship to posts.
- [ ] Add comments with a one-to-many relationship to posts.
- [ ] Replace the `published` boolean with `draft`, `published`, and `archived` states.
- [ ] Add `published_at` and set it when a post is published.
- [ ] Limit draft visibility to the author.

Acceptance criteria: posts support tags, comments, and an explicit publishing workflow with correct visibility rules.

## Phase 4 — Production Readiness

- [ ] Split endpoints into focused FastAPI routers and supporting service modules.
- [ ] Add consistent structured error responses.
- [ ] Add structured application logging.
- [ ] Add `/health/live` and `/health/ready` endpoints.
- [ ] Add environment-specific settings with safe production defaults.
- [ ] Add CI checks for tests and formatting.
- [ ] Run database migrations as a deployment step before application startup.

Acceptance criteria: the service has clear module boundaries, operational health checks, consistent diagnostics, and an automated quality gate.
