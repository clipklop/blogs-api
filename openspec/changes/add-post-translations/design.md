# Design: AI post translations

## Context

See [proposal.md](proposal.md), the capability delta specs in this change, and
[architecture notes](../../../docs/architecture.md). This is migrated design
intent, not an implementation-ready plan.

## Goals / Non-Goals

Refine AI-05 into one independently reviewable delivery. This migration does not
implement the feature or require a phase-wide implementation PR.

## Decisions

Preserve existing routers, migration history, and test isolation. Reuse shared
ownership/visibility policies. Confirm feature-specific contracts before tasks.

## Risks / Trade-offs

- Incomplete contracts could produce inconsistent implementations; keep this change
  a draft until all blocking choices and acceptance scenarios are concrete.
- Dependent changes may alter capability requirements; rebase delta blocks against
  the current main specs and synchronize dependencies before applying or archiving.

## Migration Plan

Confirm persistence impact during refinement; document any required migration/backfill and rollback limitations before implementation.
No application migration runs as part of reorganizing these documents.

## Blocking Decisions

Specify locales, fallback/public stale behavior, translation approval/publication API, revision checks and rejection/error contracts.

Finalize exact API paths, request/response examples, relevant permission matrix,
error status/bodies, verification locations, and any deployment settings. Split
this draft if refinement reveals independently deliverable changes. Do not create
tasks.md until these decisions are resolved.
