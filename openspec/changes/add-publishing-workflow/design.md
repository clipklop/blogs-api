# Design: Publishing workflow

## Context

See [proposal.md](proposal.md), the capability delta specs in this change, and
[architecture notes](../../../docs/architecture.md). This is migrated design
intent, not an implementation-ready plan.

## Goals / Non-Goals

Refine CONTENT-01 into one independently reviewable delivery. This migration does not
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

Append Alembic revisions for selected persistence changes. Specify backfills, data preservation, schema agreement, supported downgrades, and rollback limitations before implementation.
No application migration runs as part of reorganizing these documents.

## Blocking Decisions

Specify state/filter request schemas, owner-list scope, allowed transition table, archive restoration target, and removal or deprecation of the published API field.

Finalize exact API paths, request/response examples, relevant permission matrix,
error status/bodies, verification locations, and any deployment settings. Split
this draft if refinement reveals independently deliverable changes. Do not create
tasks.md until these decisions are resolved.
