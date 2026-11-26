# Architecture and Planned Design

## Status

This design covers [capability specs and draft changes](../openspec/README.md). Phases 1–2 and the Phase 3 publishing workflow are implemented.
OpenSpec change artifacts must settle API contracts, migration steps,
limits, and failure behavior before code changes. Proposed components below are
not installed or implemented unless explicitly listed as current.

## Current architecture — BASE-01 through BASE-03

- FastAPI wiring/CORS live in src/blogs_api/main.py. Focused routers already exist:
  routers/post.py, user.py, auth.py, and vote.py.
- database.py uses synchronous SQLAlchemy sessions with psycopg; config.py owns
  settings. Connection/pool timeouts currently default to five seconds. A global
  async database conversion is not required for background AI work.
- Models are Post, User, and Vote. Posts have stable slugs and required authors;
  votes have a composite user/post primary key.
- oauth2.py issues UTC-expiring tokens and resolves an existing authenticated user;
  utils.py handles bcrypt. The /users/me route precedes the dynamic user-ID route.
- Alembic owns schema evolution. Preserve this revision chain and append revisions:
  18f430d2b901 → 3eecf97d0d4d → 7b40c5d184a2 → 92f615a3e807 → a10b62d839ef → 61d07bfb923e.
- Isolated SQLite tests build databases through Alembic. Authentication tests use
  real tokens, alongside focused dependency overrides in post tests.
- Compose currently runs PostgreSQL and the API. There is no Redis, worker,
  pgvector, tag/comment model, refresh-session store, or AI adapter yet.

## Phase 3 — Content design

### Shared visibility — CONTENT-01

The post and vote routers share the publication policy in `post_access.py`.
Public lists filter on published state before pagination. Owner lists require
authentication and filter on the caller's ID. Numeric lookup requires a bearer
token. Slug lookup accepts anonymous access to published posts and a bearer token
for author access to private posts. Future nested routes should reuse this policy.

Non-owner reads and mutations of private posts return 404. A non-owner mutation
of a published post returns 403. PostgreSQL post mutations and votes lock the post
row so authorization and publication checks use the committed state.

Revision `61d07bfb923e` backfills `state` and `published_at` from the prior flag
and creation time. Downgrade maps archived and draft posts to unpublished and
discards first-publication times. Older API versions expose unpublished posts, so
keep the service offline during rollback or disable public access to affected
routes until the data and routing are safe to expose. SQLite batch rebuilds detach
and restore votes to avoid cascading deletions.

### Relationships and transactions — CONTENT-02 through CONTENT-04

Add Tag and a unique post/tag association; specify normalization, collision policy,
and limits. Accepted tags remain relational, separate from AI suggestions.

Add Comment with parent/author keys, body, and timestamps. Resolve parent visibility
before access and distinguish commenter permissions from the post author's right
to delete. Specify deletion/retention with migration tests.

Keep the vote composite primary key as the race-safe final uniqueness guard.
Derive voter identity from authentication, commit removals, translate duplicate
insert conflicts, and roll back failed sessions. Verify persistence through an
independent session. Reuse policies in services; routers handle HTTP contracts and
each mutation's related changes share a transaction.

## Phase 4 — Operational design — OPS-01 through OPS-03

Separate database-free liveness from bounded readiness returning an actual 503.
Do not expose raw exceptions. Define a shared error envelope and request-ID
contract before implementing handlers.

Production settings validate explicit signing secrets, algorithm choices, CORS
origins, and disabled debug/SQL echo. Synchronize environment examples. Multi-worker
rate limiting needs shared counters with specified quotas, expiry, and outage policy.

Package Alembic assets in the image. One deployment migration job precedes workers;
database container health alone does not prove API readiness. Run as non-root and
smoke-test clean PostgreSQL deployment.

CI adds formatter/linter checks and PostgreSQL migration/constraint tests alongside
SQLite. Measure author-loading query counts and plans before selecting indexes.
Include metrics, secret redaction, and a verified backup/restore procedure. Define
dependency failure policy before adding a queue/cache to core readiness.

## Phase 5 — Account and moderation design

### Identity — ACCOUNT-01 and ACCOUNT-02

Separate verification, reset, and refresh token purposes. Persist token digests,
account binding, expiry, consumption/revocation, and session-family metadata; never
store reusable reset/refresh secrets in plaintext. Consume/rotate atomically and
detect replay.

Access tokens currently stay valid until expiry while the user exists. Add an
account/session revocation version or equivalent checked on every authenticated
request so logout/reset/suspension can invalidate access immediately. Specify
token transport, expiry, refresh races, email-change verification, and delivery
failure before implementing.

### Moderation and lifecycle — ACCOUNT-03 and ACCOUNT-04

Introduce role checks, reports, decisions/reasons, and audit history. Hiding content
affects shared visibility, nested resources, search, recommendations, and cached
answers. Moderators receive no implicit private-draft or account-management access.

Define retention/anonymization per relationship before account deletion. Review
existing cascades against that policy, including audit records and AI artifacts.

## Phase 6 — AI design

### Components and dependency choices — AI-01 through AI-07

Put provider access behind configurable adapters with validated outputs. Select
SDKs and capability checks in OpenSpec change artifacts: an OpenAI-compatible endpoint does
not guarantee every generation/embedding capability. Define one base-URL convention
to avoid duplicated /v1 paths. Redact raw provider errors and credentials.

Use a separate worker, durable job records, and a transactional outbox or equivalent
recoverable dispatch. ARQ/Redis is a candidate, not an installed dependency or a
mandate. Specify actual queue retry/acknowledgment semantics before implementation;
raising an arbitrary exception does not define exponential backoff.

Retain synchronous request sessions unless an independently specified change
justifies conversion. Workers own their sessions and do not share request sessions.
Any async migration needs a separate spec for driver/fixture/pooling compatibility.

### Proposed persistence

| Entity | Responsibility |
| --- | --- |
| Post revision | Monotonic source revision incremented on source-content changes |
| AI job | Owner, operation, source revision, deduplication key, state, attempts, safe error, usage, timestamps |
| AI artifact | Payload, source/model/prompt versions, approval and freshness |
| Post embedding | Compatible vector with source revision and model/schema version |
| Translation | Locale, source revision, separate content, approval/publication and freshness |
| Outbox entry | Durable dispatch intent committed with its job/content change |

These are responsibilities, not final table definitions. OpenSpec change artifacts define
keys, constraints, retention, and indexes. Accepted tags remain in the taxonomy;
suggestions reference existing IDs. Exclude embeddings from public schemas.
Do not use a null processing timestamp to conflate failed and pending jobs.

Embedding dimensions belong to a versioned storage schema. Migrations record
explicit dimensions rather than reading mutable runtime settings. Dimension/model
changes require migration, reindexing, and backfill plans; mismatches fail AI
configuration validation without silently changing schema. pgvector is the planned
PostgreSQL storage candidate; choose exact/approximate indexes using measured
latency and relevance requirements.

### Assistance and execution — AI-01, AI-05, AI-06

1. Authenticate author, validate ownership/input, reserve quota, and persist a job
   plus dispatch intent. Return 202 only after acceptance is durable.
2. Worker rechecks account/ownership and loads the requested revision. Call the
   provider outside a long-lived database transaction.
3. Validate output and conditionally persist only for a current, existing source.
   Duplicate delivery is idempotent; obsolete work becomes cancelled.
4. Expose owner-only queued/running/succeeded/failed/cancelled status and safe errors.
   Retry transient failures within attempt/time/budget limits, not permanent errors.
5. Approval is a separate authenticated mutation with atomic ownership/revision
   checks. Stale approval returns a documented conflict and preserves current text.

Author assistance is opt-in; suggestions never auto-apply on CRUD. Eligible
publication/edit events may refresh embeddings through durable dispatch. Queue
outages do not roll back normal content writes. AI-disabled deployments use core
CRUD without provider credentials or queue access. Backfill is a bounded, resumable
operator job rather than an unprotected HTTP scan of every author's posts.

### Retrieval and answers — AI-02 and AI-04

Only current-revision, published, non-hidden documents with compatible embeddings
are eligible. Filter before ranking/limiting and recheck before returning. Cache
entries track dependencies and invalidate on source edits, visibility changes,
and deletion; TTL alone cannot enforce privacy.

Raw cosine similarity is 1 - cosine_distance, with range [-1, 1] for nonzero
finite vectors and floating-point tolerance. A OpenSpec change specification chooses raw similarity
or an explicitly documented mapping to [0, 1], then defines thresholds/ordering.
Self-similarity compares a stored vector with itself within tolerance, not two
potentially different provider calls. Fixed-vector exact-search tests establish
ordering; approximate indexes require recall/quality evaluations.

Bound queries and selected text. Register static search paths before dynamic
post-ID routes. Specify anonymous-query authentication/quotas and provider errors
before exposing public AI endpoints. Related posts exclude the source. Answers
receive only eligible passages, cite supporting post/passage references, and
acknowledge insufficient evidence; revalidate sources before response delivery.

Treat post text as data, not authorization or tool instructions. Translations
require approval/publication and become stale after source edits. Moderation
classifications feed authorized human review rather than silently hiding content.

## Verification and traceability

OpenSpec change artifacts map requirement IDs to concrete acceptance examples and planned tests.
PRs report what was verified and material limitations.

| Area | Required evidence |
| --- | --- |
| BASE-* | CRUD, authentication, ownership, validation, and migration regression tests |
| CONTENT-* | Role/visibility matrix, transitions, tags/comments/votes, migration preservation |
| OPS-* | PostgreSQL constraints/migrations, clean container startup, health/config, restore |
| ACCOUNT-* | Expiry/replay, concurrent refresh, immediate revocation, role boundaries, deletion |
| AI-* | Adapter/job failure, stale/duplicate work, approval races, visibility/cache tests, quality evaluations |

Retain migration-built isolated test databases rather than replacing them with
metadata.create_all(). PostgreSQL/pgvector tests validate production vector
operators/indexes; SQLite does not. Mock providers and exercise real parsing,
validation, and ranking logic. Self-similarity alone is not evidence of retrieval
relevance. Add property tests for useful invariants without mandating a new test
dependency or blanket example count for every feature.
