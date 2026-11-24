# Blog API Roadmap

## Phase 1 — Foundation

- [x] Add Alembic migrations and remove `Base.metadata.create_all()` from application startup.
- [x] Add pagination with `limit` and `offset` query parameters.
- [x] Add filtering by publication status.
- [x] Add title and content search.
- [x] Add sorting, including newest and oldest posts.
- [x] Add unique, indexed post slugs and a public slug-based lookup endpoint.
- [x] Make SQLAlchemy model nullability consistent with the Pydantic schemas.
- [x] Return an empty response body from successful `204 No Content` endpoints.
- [x] Validate PATCH requests so empty updates and invalid `null` values are rejected.
- [x] Add tests for CRUD operations, validation, missing posts, pagination, and filtering.

Acceptance criteria: database changes are migration-driven, list endpoints are bounded and searchable, API schemas match stored data, and core post behavior has automated test coverage.

## Phase 2 — Users and Authentication

- [x] Add user registration with securely hashed passwords.
- [x] Add login and JWT authentication.
- [x] Add a `GET /users/me` endpoint.
- [x] Associate every post with an author.
- [x] Allow only the author to update or delete a post.
- [x] Add authentication and authorization tests.

Acceptance criteria: authenticated users can manage their own posts, while unauthorized users cannot modify posts owned by others.

## Phase 3 — Content Features

- [ ] Restrict draft visibility across list, numeric ID, and slug endpoints; public readers see only published posts, and authors can explicitly list their own drafts.
- [ ] Replace the `published` boolean with `draft`, `published`, and `archived` states; migrate existing values and update filtering, response schemas, and API documentation together.
- [ ] Define allowed publishing transitions: authors may publish, unpublish, archive, and restore their own posts; archived posts remain private to their author.
- [ ] Add `published_at`; backfill existing published posts from `created_at`, set it on first publication, and preserve it across later edits and republication.
- [ ] Add tags with unique normalized names and a many-to-many relationship to posts; prevent duplicate assignments and support filtering by tag and author.
- [ ] Add authenticated comments on published posts with paginated listing; allow commenters to edit or delete their own comments and post authors to delete comments on their posts.
- [ ] Enforce post visibility when reading comments or voting so those endpoints cannot expose or interact with private posts.
- [ ] Complete voting behavior: commit vote removals, remove the client-supplied `user_id`, and handle concurrent duplicate votes without an unhandled database error.
- [ ] Add integration tests for publishing transitions, visibility across every lookup path, tags, comment permissions, vote creation/removal, and migration backfills.

Acceptance criteria: public users can discover and interact only with published content; authors can manage their private content, tags, and comments; votes persist correctly; publishing changes preserve existing data and have automated coverage.

## Phase 4 — Production Readiness

- [ ] Keep the existing focused routers and extract shared visibility, ownership, and transaction logic into service modules as content features grow.
- [ ] Add consistent structured error responses for validation, authentication, missing resources, and conflicts; roll back failed writes and keep internal exception details out of responses.
- [ ] Add structured application logging with request IDs, response status, and duration; exclude passwords, bearer tokens, and database credentials.
- [ ] Add `/health/live` without a database dependency and `/health/ready` with a bounded database check that returns HTTP `503` on failure; replace the current root endpoint's exception text and tuple response.
- [ ] Add environment-specific settings: require an explicit signing secret in production, validate JWT algorithm choices, configure explicit CORS origins, and disable debug/reload and SQL echo in production.
- [ ] Align `.env.example` with actual setting names, including `SQL_ECHO` and `SECRET_KEY`, and document a reproducible local startup workflow.
- [ ] Add rate limits for registration, login, and write endpoints with consistent HTTP `429` responses; verify behavior across multiple application workers.
- [ ] Add CI checks for formatting, linting, and tests, including a disposable PostgreSQL database for migration and constraint tests alongside SQLite.
- [ ] Package Alembic configuration and revision files in the deployment image and run migrations once as a deployment step before application startup.
- [ ] Add a container startup smoke test covering migrations, readiness, registration, login, and authenticated post creation; run the application container as a non-root user.
- [ ] Inspect list-query counts and plans, eager-load authors to avoid per-post queries, and add indexes for visibility, author, tag, and comment queries where measurements justify them.
- [ ] Add request latency/error metrics and document database backup and restore procedures; verify restoration against a disposable database.

Acceptance criteria: CI validates both SQLite and PostgreSQL behavior; the packaged service can migrate and start from a clean database; invalid production configuration fails early; readiness reports actual availability; logs and metrics support diagnosis without exposing secrets; backup restoration is verified.

## Phase 5 — Account Lifecycle and Moderation

- [ ] Add email verification with expiring, single-use tokens; define which actions require a verified address and test the email flow with a local or fake delivery service.
- [ ] Add password reset with expiring, single-use tokens and responses that do not disclose whether an email address is registered.
- [ ] Add authenticated profile and password updates; require the current password for sensitive changes and verify a new email before replacing the existing one.
- [ ] Add refresh-token sessions with rotation, reuse detection, and logout/revoke-all endpoints; invalidate existing sessions after password reset or account suspension.
- [ ] Add explicit author and moderator permissions; moderators may hide reported posts and comments without receiving unrestricted account access.
- [ ] Add content reports and a paginated moderation queue with a recorded reason and audit history for moderation actions.
- [ ] Define account deactivation and deletion behavior for posts, comments, and votes; implement the chosen retention or anonymization policy with migration and cascade tests.
- [ ] Add tests for token expiry and reuse, session revocation, verified-email permissions, moderator boundaries, and account deletion effects.

Acceptance criteria: users can recover and secure their accounts, revoked sessions stop working, moderators can resolve reports with an audit trail, and account lifecycle actions follow a documented data policy.
