# API diagnostics

## Purpose

Define api diagnostics behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: OPS-01 Safe structured errors

The API SHALL use a consistent error contract for validation, authentication, missing resources, conflicts, and internal failures without raw exception details.

#### Scenario: Database write failure

- **WHEN** a write fails internally
- **THEN** the transaction is rolled back and the response contains only safe error information.

### Requirement: OPS-01 Request observability

Logs SHALL carry request IDs, response status, and duration without passwords, tokens, or database credentials. Latency/error metrics SHALL be available.

#### Scenario: Failed authenticated request

- **WHEN** an authenticated request fails
- **THEN** operators can correlate safe logs and metrics without exposing the bearer token.
