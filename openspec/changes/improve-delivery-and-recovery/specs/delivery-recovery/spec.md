# Delivery and recovery

## Purpose

Define delivery and recovery behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: OPS-03 Deployment verification

CI SHALL check formatting, linting, tests, and disposable PostgreSQL migrations/constraints alongside SQLite. Clean container deployment SHALL verify migration, readiness, registration, login, and post creation.

#### Scenario: Clean deployment

- **WHEN** the packaged service starts with an empty database
- **THEN** a single migration step precedes workers and the smoke workflow succeeds.

### Requirement: OPS-03 Recoverable operations

Operators SHALL have documented database backup/restore procedures verified against a disposable database.

#### Scenario: Restore rehearsal

- **WHEN** a backup is restored into a disposable database
- **THEN** required schema and representative application data can be read.

### Requirement: OPS-03 Measured query efficiency

Post-list author loading SHALL avoid per-post queries and new indexes SHALL be justified by measured query plans.

#### Scenario: Larger page

- **WHEN** a list page includes several post authors
- **THEN** author lookup does not add a separate database query per post.
