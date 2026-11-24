# Grounded blog answers

## Why

Deliver roadmap requirement AI-04 from Phase 6 without presenting planned behavior as current functionality.

## What Changes

1. Retrieve currently public published passages; return answers with supporting
   post/passage references or an explicit insufficient-information response.
2. Recheck visibility before generation and response delivery. Invalidate cached
   answers when sources change, are unpublished/hidden, or are deleted.
3. Treat posts as untrusted input: embedded instructions cannot change permissions,
   disclose private content, or trigger unrelated actions.

## Capabilities

### New Capabilities

- `blog-answers`: grounded blog answers.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [add-semantic-discovery](../add-semantic-discovery/proposal.md)
- [add-ai-evaluation](../add-ai-evaluation/proposal.md)
