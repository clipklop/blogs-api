# Delivery and recovery

## Why

Deliver roadmap requirement OPS-03 from Phase 4 without presenting planned behavior as current functionality.

## What Changes

1. CI runs formatting, linting, tests, and disposable PostgreSQL migration/constraint
   checks alongside SQLite tests.
2. Images include Alembic assets and run as non-root. Run migrations once before
   application startup, not independently in each worker.
3. Test clean container deployment: migrations, readiness, registration, login,
   and authenticated creation.
4. Measure query counts/plans, eliminate per-post author queries, and justify indexes
   for visibility, author, tag, and comment access.
5. Document database backup/restore and verify restoration on a disposable database.

## Capabilities

### New Capabilities

- `delivery-recovery`: delivery and recovery.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

No prerequisite change is required for specification refinement.
