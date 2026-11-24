# AI jobs and artifact lifecycle

## Why

Deliver roadmap requirement AI-06 from Phase 6 without presenting planned behavior as current functionality.

## What Changes

1. Persist queued/running/succeeded/failed/cancelled job states. Distinguish artifact
   freshness, job failure, and pending work.
2. Bound retries/timeouts, deduplicate work, enforce per-user usage/cost budgets,
   and report failures safely. Provider/queue outages do not block normal CRUD.
3. Bind jobs/artifacts to source revision, model/prompt version, and embedding
   schema. Discard late results for changed/deleted content; recheck authority.
4. Source edits invalidate derived artifacts; unpublish/archive/hide excludes them
   immediately from public retrieval; deletion removes searchable artifacts.
5. AI-disabled deployments need no provider settings. Validate structured output,
   vector dimensions, finite values, and nonzero vectors; redact provider error bodies.
6. Author job/status endpoints require authentication/ownership. Backfills are
   restricted, bounded, resumable jobs, not public all-post operations.

## Capabilities

### New Capabilities

- `ai-jobs`: ai jobs and artifact lifecycle.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [add-publishing-workflow](../add-publishing-workflow/proposal.md)
