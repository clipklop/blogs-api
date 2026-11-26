# AI moderation assistance

## Why

Deliver roadmap requirement AI-03 from Phase 6 without presenting planned behavior as current functionality.

## What Changes

1. Model classifications flag posts/comments for authorized human review, recording
   model version and reasons. They do not independently change policy or roles.
2. Separate model safety categories from spam/community-rule logic. Do not expose
   private drafts through a queue beyond the approved moderation scope.

## Capabilities

### New Capabilities

- `moderation-assistance`: ai moderation assistance.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [add-content-moderation](../add-content-moderation/proposal.md)
- [add-ai-job-infrastructure](../add-ai-job-infrastructure/proposal.md)
