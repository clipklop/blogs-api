# Refresh sessions and revocation

## Why

Deliver roadmap requirement ACCOUNT-02 from Phase 5 without presenting planned behavior as current functionality.

## What Changes

1. Refresh sessions support rotation, replay detection, logout, and revoke-all.
2. Reset/suspension invalidate existing sessions including access tokens. Specify
   how every authenticated request observes revocation.
3. Test concurrent refresh, replay, expiry, and immediate revoked-access rejection.

**BREAKING**: Existing API, error, request, or authentication behavior may change; finalize compatibility in the design before implementation.

## Capabilities

### New Capabilities

- `sessions`: refresh sessions and revocation.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

- [add-account-recovery](../add-account-recovery/proposal.md)
