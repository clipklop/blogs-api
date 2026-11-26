## Change

Describe the concrete problem and resulting behavior.

## OpenSpec

- Change: `openspec/changes/<change-name>/` (or its archive path)
- Capability paths and requirement/scenario names:
- Roadmap requirement IDs:
- Specification commit preceding implementation (or prior spec PR):
- Spec synchronization/archive status (or why this is a spec-only draft):

## Validation

Report `openspec validate --all --strict --no-interactive`, relevant application
checks, scenarios verified, and any remaining limitations.

## Data and compatibility

Describe migrations/backfills, rollback limitations, configuration, and API changes,
or state that none apply.

## Review checklist

- [ ] This PR targets main from a dedicated feature, fix, docs, or chore branch.
- [ ] Change artifacts preceded implementation, migrations, and feature tests.
- [ ] Blocking design decisions are resolved before implementation.
- [ ] Applicable scenarios and relevant regressions were verified.
- [ ] Main capability specs describe verified behavior; proposals remain in changes.
- [ ] Completed changes are synchronized/archived and roadmap/docs updated, or this PR is explicitly spec-only.
