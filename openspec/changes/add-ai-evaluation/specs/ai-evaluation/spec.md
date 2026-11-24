# AI verification and evaluation

## Purpose

Define ai verification and evaluation behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: AI-07 Reproducible quality evaluation

AI changes SHALL be evaluated against a versioned dataset covering suggestion validity, relevance, supported answers, insufficient evidence and prompt injection with declared measurable thresholds.

#### Scenario: Candidate release

- **WHEN** an AI change is evaluated for delivery
- **THEN** its dataset version, metrics and comparison against declared thresholds are recorded.

### Requirement: AI-07 Realistic failure verification

Verification SHALL cover adapter parsing, provider/queue failures, stale/duplicate jobs, approval/deletion races, cache visibility, draft leakage and budget exhaustion. Normal tests SHALL mock provider calls.

#### Scenario: Production vector verification

- **WHEN** vector queries or indexes change
- **THEN** disposable PostgreSQL with pgvector verifies their behavior; SQLite alone is not accepted as evidence.
