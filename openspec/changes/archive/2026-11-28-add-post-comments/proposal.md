# Post comments

## Why

CONTENT-03 gives readers a way to discuss published posts and authors a way to remove comments from their own posts.

## What Changes

- Add a nested endpoint for listing and creating comments.
- Let commenters edit and delete their own comments and post authors delete comments on their posts.
- Apply parent visibility to every comment operation and preserve comments across publication transitions.

## Capabilities

### New Capabilities

- `comments` at `specs/comments/spec.md` defines comment creation, reads, mutations, and retention.

### Modified Capabilities

None.

## Impact

The API gains nested routes with no changes to existing responses. An additive Alembic revision creates the comments table. This change depends on the [publishing visibility policy](../../specs/publishing/spec.md) and follows the verified tags migration.
