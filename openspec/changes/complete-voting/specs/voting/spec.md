# Voting correctness

## Purpose

Define voting correctness behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: CONTENT-04 Vote removal persistence

Vote removal SHALL commit its transaction so removal survives subsequent independent requests and database sessions.

#### Scenario: Remove vote

- **WHEN** a voter removes an existing vote and the post is read through a fresh database session
- **THEN** the vote is absent and the aggregate count is reduced.

### Requirement: CONTENT-04 Vote identity and uniqueness

The vote request SHALL NOT require user_id. Authentication SHALL supply identity, and concurrent duplicate creation SHALL return a documented conflict without an unhandled database error.

#### Scenario: Concurrent duplicate

- **WHEN** two requests by the same user race to create a vote for one post
- **THEN** at most one row is stored and the conflicting request returns 409.

### Requirement: CONTENT-04 Vote visibility

Voting SHALL be allowed only on published posts visible to the caller.

#### Scenario: Private target

- **WHEN** a signed-in user attempts to vote on a draft or archived post
- **THEN** the vote is not created and the response does not disclose private content.
