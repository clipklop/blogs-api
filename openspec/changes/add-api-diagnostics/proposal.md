# API diagnostics

## Why

Deliver roadmap requirement OPS-01 from Phase 4 without presenting planned behavior as current functionality.

## What Changes

1. Keep existing routers; extract shared visibility, ownership, and transaction
   policies into services where reuse requires it.
2. Define consistent errors for validation, credentials, missing resources,
   conflicts, and internal failure without exposing exception internals.
3. Log request IDs, statuses, and durations; exclude passwords, tokens, and database
   credentials. Expose latency and error metrics.

**BREAKING**: Existing API, error, request, or authentication behavior may change; finalize compatibility in the design before implementation.

## Capabilities

### New Capabilities

- `diagnostics`: api diagnostics.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

No prerequisite change is required for specification refinement.
