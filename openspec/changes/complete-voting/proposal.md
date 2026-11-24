# Voting correctness

## Why

Deliver roadmap requirement CONTENT-04 from Phase 3 without presenting planned behavior as current functionality.

## What Changes

1. Derive voter identity from authentication; remove client-supplied user_id.
2. Persist creation and removal. Enforce one vote per user/post at database level.
3. Translate concurrent duplicate insertion to a documented conflict and roll back
   failed transactions; do not return an unhandled database error.
4. Reject interactions with private posts. Test authentication, visibility, duplicate
   races, counts, and removal verified through a fresh database session.

**BREAKING**: Existing API, error, request, or authentication behavior may change; finalize compatibility in the design before implementation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `voting`: complete persistent, visibility-aware voting.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [add-publishing-workflow](../add-publishing-workflow/proposal.md)
