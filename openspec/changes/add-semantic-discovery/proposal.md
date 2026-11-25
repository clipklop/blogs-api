# Semantic search and recommendations

## Why

Deliver roadmap requirement AI-02 from Phase 6 without presenting planned behavior as current functionality.

## What Changes

1. Generate embeddings for eligible published content and reuse them for search and
   recommendations. Keep keyword search available.
2. Define query/pagination limits and scoring semantics in the feature spec. Filter
   current compatible embeddings and visibility before ranking/limiting; recheck
   visibility before returning results, including cached results.
3. Public responses exclude embeddings/private artifacts. Recommendations exclude
   the source post and all nonpublic content.

## Capabilities

### New Capabilities

- `semantic-discovery`: semantic search and recommendations.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [add-ai-job-infrastructure](../add-ai-job-infrastructure/proposal.md)
- [Implemented publishing capability](../../specs/publishing/spec.md)
- [add-ai-evaluation](../add-ai-evaluation/proposal.md)
