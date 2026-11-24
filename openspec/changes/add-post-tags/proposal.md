# Post tags

## Why

Deliver roadmap requirement CONTENT-02 from Phase 3 without presenting planned behavior as current functionality.

## What Changes

1. Store unique normalized tags in a many-to-many post/tag relationship and prevent
   duplicate assignments. Define normalization and assignment limits in the feature spec.
2. Add tag/author filters compatible with search, pagination, and sorting.
3. Test normalization collisions, combined filters, and assignment permissions.
   Later AI tag suggestions reference this accepted taxonomy.

## Capabilities

### New Capabilities

- `tags`: post tags.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [add-publishing-workflow](../add-publishing-workflow/proposal.md)
