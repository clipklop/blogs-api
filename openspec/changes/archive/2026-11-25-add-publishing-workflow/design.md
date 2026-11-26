# Design: Publishing workflow

## Context

The post API currently stores a mutable publication flag and returns unpublished posts through list and slug lookups. The vote endpoint also looks up posts without restricting publication state. Reuse the synchronous FastAPI and SQLAlchemy routers and the existing Alembic chain.

## Goals / Non-Goals

Deliver private drafts and archives, first publication timestamps, and consistent visibility across existing read and vote paths. Later comments, tags, moderation, and AI changes can reuse the policy. Changes to vote identity, duplicate insert handling, and removal persistence belong to the separate voting change.

## Decisions

| Operation | Anonymous | Author | Other authenticated user |
| --- | --- | --- | --- |
| Public list | Published only | Published only | Published only |
| Owner list with `scope=mine` | 401 | Own posts, all states by default | Own posts only |
| Slug lookup | Published only | Published or own private | Published only |
| Numeric lookup | 401 | Published or own private | Published only |
| Content PATCH, delete, publication PUT | 401 | Allowed subject to validation | 403 published, 404 private |
| Existing vote endpoint | 401 | Published targets only | Published targets only |

- Use one shared publication policy at the database query boundary so state cannot be bypassed by search, pagination, or alternate lookup. Existing private and missing posts use identical route-specific 404 responses. Keep current detail bodies for 401, 403 and 404 and standard FastAPI validation details for 422. Keep the public list credential-independent. The owner list uses required authentication and the slug route uses optional authentication, rejecting invalid supplied credentials with 401.
- Use `GET /posts/?scope=mine&state=draft` for author access. Public scope accepts omitted state or `state=published`. Reject the retired `published` query key explicitly so older clients cannot silently get a broader result. Preserve search length 1–1000, pagination bounds and ordering. Read payloads retain vote counts alongside the normal post fields.
- Use a dedicated `PUT /posts/{post_id}/publication` with a strict JSON target state. Accepted values are `draft`, `published`, and `archived`. The publication payload rejects extras. POST and content PATCH reject the three publication keys, while POST keeps existing handling for unrelated extras such as supplied ownership. Keep existing title/content/rating validation. The row's current state controls the following transition table.

| Current / requested | draft | published | archived |
| --- | --- | --- | --- |
| draft | No write | Publish | Archive |
| published | Unpublish | No write | Archive |
| archived | Restore to draft | 409 | No write |

- Return the normal post response on transitions, for example `{"id":7,"state":"published","published_at":"2026-11-25T09:00:00Z",...}` (excerpt). Update `updated_at` on a real transition. Owner content edits remain available in every state and preserve the publication timestamp.
- In PostgreSQL, lock the post row before checking ownership and current state for post mutations. Use the same row lock before checking vote eligibility and performing the existing vote operation. This serializes authorization and publication checks with competing transitions. SQLite ignores row locks, so use it for contract and migration tests and verify transaction ordering on PostgreSQL.

## Risks / Trade-offs

- Replacing the boolean requires coordinated client rollout. Clients switch reads and filters to `state` and use the dedicated PUT for transitions.
- Downgrade cannot preserve archival state or first publication timestamps. Older API versions also expose unpublished rows through public paths, so disable those public routes or keep the service offline during rollback until the data and routing are safe to expose.

## Migration Plan

Append a revision after `a10b62d839ef`. Add a portable state string with a named check constraint, a non-null draft default, and a nullable timezone-aware `published_at`. Backfill from `published` and `created_at` before removing the boolean. Reject a published row without a first publication timestamp at the database level. Run migrations before starting the new API.

Downgrade recreates the boolean from state and removes both new fields and their constraints. Use SQLite batch operations where required and preserve dependent vote rows when a table rebuild would cascade them, following the existing ownership migration. Verify stable IDs, slugs, ownership, existing timestamps, and vote counts on clean upgrade and upgrade/downgrade fixtures. Use isolated SQLite and disposable PostgreSQL with foreign-key enforcement.
