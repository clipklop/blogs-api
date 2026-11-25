# Voting correctness

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
