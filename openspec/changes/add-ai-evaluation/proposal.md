# AI verification and evaluation

## Why

Deliver roadmap requirement AI-07 from Phase 6 without presenting planned behavior as current functionality.

## What Changes

1. Mock providers in normal tests; exercise adapter validation, malformed responses,
   authentication, rate limits, timeouts, and provider failures.
2. Version an evaluation dataset covering suggestion validity, search relevance,
   supported answers, insufficient evidence, and prompt injection.
3. Test draft leakage, cached visibility changes, stale/duplicate jobs, approval
   races, deletion, budget exhaustion, and provider/queue outages.
4. Validate vector queries/indexes on PostgreSQL with pgvector; SQLite does not
   establish production search correctness. Define measurable quality thresholds
   in the feature spec before release.

## Capabilities

### New Capabilities

- `ai-evaluation`: ai verification and evaluation.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

No prerequisite change is required for specification refinement.
