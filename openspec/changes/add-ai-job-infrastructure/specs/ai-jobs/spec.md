# AI jobs and artifact lifecycle

## Purpose

Define ai jobs and artifact lifecycle behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: AI-06 Durable bounded jobs

AI jobs SHALL expose queued/running/succeeded/failed/cancelled states, safe failures, bounded retries/timeouts, deduplication and per-user usage/cost budgets.

#### Scenario: Exhausted attempts

- **WHEN** a transient provider failure exhausts the retry budget
- **THEN** the job becomes failed with a safe error rather than remaining pending forever.

### Requirement: AI-06 Revision-bound artifacts

Jobs/artifacts SHALL bind to source revision, model/prompt version and embedding schema; obsolete or deleted-source results SHALL NOT overwrite current artifacts.

#### Scenario: Late worker

- **WHEN** a worker finishes after the source was edited or deleted
- **THEN** its obsolete output is discarded and cannot reappear in public retrieval.

### Requirement: AI-06 Optional resilient AI

Normal CRUD SHALL remain available without AI settings and during provider/queue outages. Structured outputs and nonzero finite vectors of the correct dimension SHALL be validated.

#### Scenario: AI outage

- **WHEN** the provider or queue is unavailable while a user creates a normal post
- **THEN** the post operation succeeds independently of AI availability.

### Requirement: AI-06 Restricted job access

Author job/status operations SHALL require ownership. Backfills SHALL be restricted, bounded, resumable work.

#### Scenario: Unauthorized job status

- **WHEN** another user requests a private job result
- **THEN** the result and source content are not disclosed.
