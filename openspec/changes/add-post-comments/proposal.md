# Post comments

## Why

Deliver roadmap requirement CONTENT-03 from Phase 3 without presenting planned behavior as current functionality.

## What Changes

1. Authenticated users can comment on published posts. Paginated reads respect
   parent visibility.
2. Commenters can edit/delete their own comments; post authors can delete comments
   on their posts, but cannot rewrite another user's comment.
3. Specify body limits, ordering, deletion/cascade behavior, errors, and tests for
   ownership and hidden/missing parents before implementation.

## Capabilities

### New Capabilities

- `comments`: post comments.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [Implemented publishing capability](../../specs/publishing/spec.md)
