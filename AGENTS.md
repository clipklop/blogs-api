# Repository instructions

## Specification-first development with OpenSpec

- Read `openspec/README.md`, applicable `openspec/specs/<capability>/spec.md`,
  `docs/architecture.md`, and the relevant change artifacts before feature work.
- Use OpenSpec's `spec-driven` schema. Every behavior change starts in
  `openspec/changes/<change-name>/` with `proposal.md`, capability deltas under
  `specs/<capability>/spec.md`, design when needed, and `tasks.md`.
- Complete contracts, permissions, validation, failure cases, migrations, and
  testable WHEN/THEN scenarios **before implementation code, migrations, or feature
  tests**. Resolve blocking decisions before creating implementation tasks.
- The migrated roadmap changes are drafts. Missing tasks or a Blocking Decisions
  section means the change is not ready to implement; artifact presence alone
  never grants readiness.
- Commit the spec before its implementation. Update the change artifacts first
  when scope/behavior changes. Contract-changing bug fixes follow this rule too.
- Current capability specs describe implemented behavior. Keep proposed behavior
  in change deltas until implemented and verified, then sync and archive it.
  Preserve complete requirement blocks and exact names in MODIFIED deltas.
- Validate with `openspec validate --all --strict --no-interactive`; verify code
  against scenarios separately. Keep TODO.md completion honest.
- Follow CONTRIBUTING.md and openspec/config.yaml. Do not maintain duplicate
  requirement baselines or revive the superseded top-level specs/ template.

## Branches and pull requests

- Develop new features on dedicated `feat/<change-name>` branches from up-to-date
  `main`; use `fix/`, `docs/`, or `chore/` for corresponding work.
- Never implement/commit feature work on main or push directly to main. Deliver
  through a pull request targeting main.
- Put the specification before implementation in branch history. A spec-only PR
  can precede a dependent implementation PR; otherwise use ordered commits in one PR.
- Link the OpenSpec change, capability/requirement names, scenarios, and spec commit
  in the PR. Report verification, migration effects, and remaining limitations.
- Include verified spec synchronization/archive in the delivery PR. Archiving
  does not authorize a merge or deployment.
- Preserve unrelated working-tree edits. Do not merge, force-push, or change remote
  branch protection without explicit authorization. Report branch/PR tooling
  blockers instead of bypassing the workflow.

## Project constraints

- Use Alembic for schema changes; append migrations without rewriting deployed
  history. Test data preservation and supported rollback behavior.
- Keep authentication, ownership, and visibility consistent across direct/nested
  lookup, discovery, and AI paths.
- Keep README focused on project overview, setup, configuration, and current API
  behavior. Put phases, implementation history, and process in their own documents.
- Run verification appropriate to the change. Documentation-only updates need
  OpenSpec validation, link/consistency and whitespace checks, not tests mirroring prose.
