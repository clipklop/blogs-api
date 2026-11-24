# Account deactivation and deletion

## Why

Deliver roadmap requirement ACCOUNT-04 from Phase 5 without presenting planned behavior as current functionality.

## What Changes

1. Before implementation, define retention/deletion/anonymization for posts,
   comments, votes, reports, sessions, audit records, and AI artifacts.
2. Test the chosen policy, cascades, migrations, and session invalidation.

## Capabilities

### New Capabilities

- `account-lifecycle`: account deactivation and deletion.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [add-refresh-sessions](../add-refresh-sessions/proposal.md)
- [add-content-moderation](../add-content-moderation/proposal.md)
