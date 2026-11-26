# Refresh sessions and revocation

## Purpose

Define refresh sessions and revocation behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: ACCOUNT-02 Refresh rotation

Refresh sessions SHALL support rotation, reuse detection, logout, and revoke-all with atomic single-use consumption.

#### Scenario: Replayed refresh

- **WHEN** a consumed refresh token is used again
- **THEN** the replay is detected and the specified session-family revocation policy is applied.

### Requirement: ACCOUNT-02 Immediate revocation

Password reset and account suspension SHALL invalidate refresh sessions and existing access credentials without waiting for normal token expiry.

#### Scenario: Reset then access

- **WHEN** a user resets a password and an earlier access token is submitted
- **THEN** the protected request is rejected.
