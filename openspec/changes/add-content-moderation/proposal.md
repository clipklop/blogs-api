# Reports and moderation

## Why

Deliver roadmap requirement ACCOUNT-03 from Phase 5 without presenting planned behavior as current functionality.

## What Changes

1. Define author/moderator permissions. Moderators can hide reported posts/comments
   without unrestricted account access or implicit access to private drafts.
2. Add reporting, paginated review, recorded reasons, and action audit history.
3. Hidden content leaves public lookup, nested resources, discovery, and AI results.
   Test role boundaries and alternate-endpoint bypass attempts.

## Capabilities

### New Capabilities

- `moderation`: reports and moderation.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [Implemented comments capability](../../specs/comments/spec.md)
- [Implemented publishing capability](../../specs/publishing/spec.md)
