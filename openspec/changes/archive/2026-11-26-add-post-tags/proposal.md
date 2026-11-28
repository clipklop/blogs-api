# Post tags

## Why

Readers need to find published posts by topic and author. CONTENT-02 adds an accepted, reusable taxonomy managed through each author's posts.

## What Changes

- Allow authors to replace a post's tags with normalized names.
- Return tag names on post responses and filter discovery by exact tag and author ID.
- Preserve existing post visibility, state transitions, and vote counts.

## Capabilities

### New Capabilities

- `tags` at `specs/tags/spec.md` defines tag assignment, permissions, and persistence.

### Modified Capabilities

- `posts` at `specs/posts/spec.md` adds tag representation and discovery filters.

## Impact

The API adds one endpoint, two optional query parameters, and a response field. The migration adds two tables without backfilling tags. This depends on the [implemented publishing contract](../../specs/publishing/spec.md). The change is ready for implementation after the specification commit.
