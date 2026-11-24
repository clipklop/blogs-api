# Runtime health and configuration

## Why

Deliver roadmap requirement OPS-02 from Phase 4 without presenting planned behavior as current functionality.

## What Changes

1. /health/live does not call the database. /health/ready performs a bounded database
   check and returns 503 on failure. Replace the root handler's exception disclosure
   and tuple response.
2. Production requires an explicit signing secret, validated algorithm choices,
   explicit CORS origins, and disabled debug/reload and SQL echo.
3. Align .env.example with actual settings, including SQL_ECHO and SECRET_KEY, and
   document reproducible setup without real credentials.
4. Registration/login/write rate limits operate across workers and return 429.
   Define quotas, keys, and shared-store failure behavior in the feature spec.

## Capabilities

### New Capabilities

- `service-runtime`: runtime health and configuration.

### Modified Capabilities

None at this draft stage; add full delta blocks for any existing contracts changed during refinement.

## Impact

See [design.md](design.md) and [architecture notes](../../../docs/architecture.md). No runtime change is included in this specification migration.

## Dependencies and Readiness

Status: **Draft**. This migrated proposal has no implementation task list yet.
Resolve blocking contracts and design choices before producing tasks or code.

No prerequisite change is required for specification refinement.
