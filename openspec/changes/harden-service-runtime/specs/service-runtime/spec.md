# Runtime health and configuration

## Purpose

Define runtime health and configuration behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: OPS-02 Liveness and readiness

Liveness SHALL work without the database. Readiness SHALL use a bounded database check and return 503 on database failure without exception text.

#### Scenario: Database outage

- **WHEN** the database is unavailable
- **THEN** liveness remains successful and readiness returns 503 within the configured bound.

### Requirement: OPS-02 Production configuration

Production SHALL require an explicit signing secret, validated algorithms, configured CORS origins, and disabled debug/reload and SQL echo. Environment examples SHALL match actual setting names.

#### Scenario: Unsafe configuration

- **WHEN** production startup receives a missing signing secret or a forbidden setting
- **THEN** configuration validation rejects startup with a safe actionable message.

### Requirement: OPS-02 Shared rate limiting

Registration, login, and write quotas SHALL be enforced across workers with consistent 429 responses.

#### Scenario: Cross-worker quota

- **WHEN** a caller exceeds a quota while requests are served by multiple workers
- **THEN** the shared limit is enforced rather than reset per worker.
