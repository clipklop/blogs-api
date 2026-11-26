# Blog API Roadmap

Development follows the [OpenSpec specifications and change proposals](openspec/README.md) and
[contribution workflow](CONTRIBUTING.md). Specify every new feature before code,
develop it on a dedicated feature branch, and deliver it through a pull request
to `main`. Checkboxes track verified implementation, not specification readiness.

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

- [x] Restrict draft visibility across list, numeric ID, and slug endpoints; public readers see only published posts, and authors can explicitly list their own drafts.
- [x] Replace the `published` boolean with `draft`, `published`, and `archived` states; migrate existing values and update filtering, response schemas, and API documentation together.
- [x] Define allowed publishing transitions: authors may publish, unpublish, archive, and restore their own posts; archived posts remain private to their author.
- [x] Add `published_at`; backfill existing published posts from `created_at`, set it on first publication, and preserve it across later edits and republication.
- [ ] Add tags with unique normalized names and a many-to-many relationship to posts; prevent duplicate assignments and support filtering by tag and author.
- [ ] Add authenticated comments on published posts with paginated listing; allow commenters to edit or delete their own comments and post authors to delete comments on their posts.
- [x] Restrict voting to published posts, including when the caller owns the draft or archive.
- [ ] Enforce parent-post visibility when reading or writing comments.
- [ ] Complete voting behavior: commit vote removals, remove the client-supplied `user_id`, and handle concurrent duplicate votes without an unhandled database error.
- [x] Test publishing transitions, lookup and vote visibility, migration backfills, and PostgreSQL concurrency.
- [ ] Add integration tests for tags, comments, and vote creation/removal persistence.

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

## Phase 6 — AI Discovery and Author Tools

Implement summaries and tag suggestions first, then semantic search and related posts. Add question answering after retrieval quality and visibility checks are verified.

- [ ] Add author-requested title, summary, and existing-tag suggestions with structured, validated responses; require explicit author approval before changing stored content.
- [ ] Add writing feedback, outline suggestions, and rewriting of selected text; preserve the original text until the author accepts a suggestion.
- [ ] Generate and store post embeddings and add semantic search alongside existing keyword search.
- [ ] Add related-post recommendations using the same embeddings and restrict public recommendations to published, visible posts.
- [ ] Add moderation assistance that flags potentially harmful posts and comments for human review; keep spam detection and community-rule enforcement explicit and separate from model safety classifications.
- [ ] Add an "Ask the blog" endpoint that retrieves published content, returns answers with supporting post and passage references, and reports insufficient information when sources do not support an answer.
- [ ] Add author-requested translations stored separately from the original and tied to its revision; require approval before publication and mark translations stale when the source changes.
- [ ] Run generation and embedding work as background jobs with bounded retries, timeouts, observable job status, and per-user usage and cost limits; keep ordinary post operations available during provider outages.
- [ ] Tie generated artifacts to the source revision and model/prompt version; invalidate or regenerate stale summaries, translations, and embeddings after edits, and remove searchable artifacts when content is deleted.
- [ ] Enforce visibility before retrieval and before returning results; promptly exclude unpublished, archived, or moderator-hidden content from public search, recommendations, and answers, including cached results.
- [ ] Restrict private-draft assistance to the author; treat retrieved posts as untrusted input and prevent embedded instructions from changing permissions or triggering unrelated actions.
- [ ] Add provider mocks and a small evaluation dataset covering suggestion validity, search relevance, source-supported answers, insufficient-information responses, draft leakage, stale artifacts, and provider failures.

Acceptance criteria: authors can review AI suggestions without losing their original content; public discovery and answers use only currently visible published posts; answers reference supporting passages or acknowledge insufficient evidence; generated artifacts track source revisions; usage is bounded and provider failures do not block core API operations.
