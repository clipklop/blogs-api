# Publishing workflow

## Why

Deliver roadmap requirement CONTENT-01 from Phase 3 without presenting planned behavior as current functionality.

## What Changes

1. Replace published with draft/published/archived states; migrate true to published
   and false to draft. Specify the filter/schema compatibility change.
2. Public readers see only published content. Authors explicitly list their own
   drafts/archives. Apply one visibility policy across lists, ID/slug lookups,
   comments, votes, and later AI endpoints/caches.
3. Authors can publish, unpublish, archive, and restore their own posts. The feature
   spec must enumerate transitions and invalid-transition responses.
4. Set published_at on first publication and preserve it on edits/republication.
   Backfill existing published rows from created_at.
5. Test anonymous, owner, and other-user access on every lookup path, all state
   transitions, and migration backfills.

**BREAKING**: Existing API, error, request, or authentication behavior may change; finalize compatibility in the design before implementation.

## Capabilities

### New Capabilities

- `publishing`: explicit post state transitions and publication timestamps.

### Modified Capabilities

- `posts`: private draft/archive access and state-aware discovery.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

No prerequisite change is required for specification refinement.
