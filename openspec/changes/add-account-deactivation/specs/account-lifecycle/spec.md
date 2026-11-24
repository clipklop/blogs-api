# Account deactivation and deletion

## Purpose

Define account deactivation and deletion behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: ACCOUNT-04 Explicit data policy

Account deactivation/deletion SHALL follow a documented retention, deletion, or anonymization policy for posts, comments, votes, reports, sessions, audit records, and AI artifacts.

#### Scenario: Account deletion

- **WHEN** an account is deleted according to the approved policy
- **THEN** all related data follows that policy and active credentials stop authorizing requests.
