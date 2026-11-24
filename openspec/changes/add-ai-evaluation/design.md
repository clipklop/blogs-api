# Design: AI verification and evaluation

## Context

See [proposal.md](proposal.md), the capability delta specs in this change, and
[architecture notes](../../../docs/architecture.md). This is migrated design
intent, not an implementation-ready plan.

## Goals / Non-Goals

Refine AI-07 into one independently reviewable delivery. This migration does not
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

Define dataset ownership, representative examples, measurable thresholds per capability, evaluation commands and deterministic provider mocks; evidence tests are implemented with their corresponding features.

Finalize exact API paths, request/response examples, relevant permission matrix,
error status/bodies, verification locations, and any deployment settings. Split
this draft if refinement reveals independently deliverable changes. Do not create
tasks.md until these decisions are resolved.
