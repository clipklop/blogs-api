# AI author assistance

## Why

Deliver roadmap requirement AI-01 from Phase 6 without presenting planned behavior as current functionality.

## What Changes

1. Authors request title/summary/existing-tag suggestions, writing feedback,
   outlines, and selected-text rewrites for their own posts, including drafts.
2. Validate structured output and tag IDs. Store suggestions separately; generated
   text/tags never replace accepted content without explicit author approval.
3. Approval atomically checks ownership and source revision; stale results cannot
   overwrite a newer revision. Preserve originals until acceptance.

## Capabilities

### New Capabilities

- `author-assistance`: ai author assistance.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [add-ai-job-infrastructure](../add-ai-job-infrastructure/proposal.md)
- [add-post-tags](../add-post-tags/proposal.md)
