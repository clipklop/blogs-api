# Account verification and recovery

## Purpose

Define account verification and recovery behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: ACCOUNT-01 Single-use account tokens

Verification/reset tokens SHALL expire, bind to one account and purpose, and be usable once. Recovery responses SHALL NOT reveal account existence.

#### Scenario: Token replay

- **WHEN** a caller reuses a consumed reset token
- **THEN** the reset is rejected without changing account state.

### Requirement: ACCOUNT-01 Sensitive profile changes

Profile/password updates SHALL require authentication and sensitive changes SHALL require the current password. Email replacement SHALL require verification of the new address.

#### Scenario: Unverified replacement

- **WHEN** a user proposes a new email but has not verified it
- **THEN** the existing account email remains effective.
