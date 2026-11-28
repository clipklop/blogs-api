# Post comments design

## Context

The existing publishing contract makes a draft or archived post visible only to its author. Comments remain attached across publication changes so a published discussion can resume after republication.

## Decisions

- Mount a focused router under `/posts/{post_id}/comments`. Collection GET uses the optional bearer policy from slug reads. Missing or invisible parents return `{"detail":"Post not found"}`; missing or mismatched child IDs under a visible parent return `{"detail":"Comment not found"}`. Authorization failures use 401 with a bearer challenge or 403 with `{"detail":"Not authorized to modify this comment"}`.
- Use the shared SQL visibility predicate and fetch a bounded page with its visible parent in one statement. The outer join retains a visible parent with no page rows. Sort descending by creation time and ID.
- Use the shared post-row lock on PostgreSQL for writes. Resolve the committed parent state before fetching a child. Create requires a published parent. Edit and delete require a readable parent as well as comment ownership or the post author's delete permission. Commit each successful mutation before returning.
- Accept a strict JSON body with only `body`. Trim outer whitespace and accept 1–1000 Unicode characters without U+0000 or invalid Unicode scalar values. Compute the author and UTC timestamps on the server. Responses expose only `id`, `post_id`, `author_id`, `body`, `created_at`, and `updated_at`.

## Migration plan

Append one Alembic revision after `b67257fc1b08`. Create a comments table with an integer primary key, required cascading foreign keys to posts and users, a body length check, and indexes for parent pagination and author cascade. Start with no comment rows. Downgrade drops comment data while preserving pre-existing posts, accounts, tags, and votes.

## Risks

Offset pagination can shift between requests when comments are inserted or deleted. The post-row lock serializes writes to each post; public reads use a single statement without acquiring that lock.
