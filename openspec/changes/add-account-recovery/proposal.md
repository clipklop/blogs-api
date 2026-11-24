# Account verification and recovery

## Why

Deliver roadmap requirement ACCOUNT-01 from Phase 5 without presenting planned behavior as current functionality.

## What Changes

1. Verification/reset tokens expire and are single-use. Recovery responses do not
   disclose account existence; tests use fake/local email delivery.
2. Define verified-email permissions. Require authentication for profile/password
   changes, current password for sensitive changes, and new-email verification
   before replacing an email address.
3. Test expiry, reuse, account binding, and delivery failure without exposing tokens.

## Capabilities

### New Capabilities

- `account-recovery`: account verification and recovery.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

No prerequisite change is required for specification refinement.
