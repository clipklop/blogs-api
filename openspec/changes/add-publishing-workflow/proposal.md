# Publishing workflow

## Why

Implement Phase 3 requirement CONTENT-01 so authors can prepare and archive posts privately and readers only discover published content.

## What Changes

- Create posts as drafts. Authors use a dedicated endpoint to publish, unpublish, archive, and restore posts.
- Restrict listing, numeric lookup, slug lookup, and voting by publication state. Authors can explicitly list their own posts.
- Record when a post was first published and backfill existing published posts.
- **BREAKING**: Replace the `published` field and query parameter with state-aware contracts. Use the publication endpoint to change state. Private post reads and attempts to modify another author's private post return 404.

## Capabilities

### New Capabilities

- `publishing`: state transitions, first publication time, and migration behavior.

### Modified Capabilities

- `posts`: post schemas, state-aware discovery, and visibility.
- `voting`: published-only targets on the existing vote endpoint.

## Impact

Updates post and vote routers, schemas, persistence, Alembic, OpenAPI, and tests. The existing [complete-voting](../complete-voting/proposal.md) change still owns removal persistence, request identity cleanup, and duplicate-race handling. Its visibility delta should be reconciled after publishing ships.

Planning is ready for review. See [design.md](design.md) and [tasks.md](tasks.md).
