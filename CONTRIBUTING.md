# Contributing

## Develop from OpenSpec changes

Read the [OpenSpec index](openspec/README.md), relevant
[implemented capability specs](openspec/specs/), and
[architecture notes](docs/architecture.md). [TODO.md](TODO.md) is the delivery
roadmap. Current specs describe implemented behavior; changes describe proposals.

1. Inspect the working tree and preserve unrelated edits. Start a dedicated branch
   from up-to-date main: `feat/<change-name>`, or `fix/`, `docs/`, `chore/`.
2. Run `openspec new change <change-name>` or use the agent's propose workflow.
   Write proposal.md with Why, What Changes, Capabilities, and Impact.
3. Write scenario-based delta specs at
   `openspec/changes/<change-name>/specs/<capability>/spec.md`. Use ADDED,
   MODIFIED, REMOVED, or RENAMED Requirements. A modified requirement includes its
   exact name and complete updated content, including all scenarios.
4. Complete design.md where architecture, dependencies, migrations, security,
   concurrency, or other complexity needs decisions. Resolve blocking questions
   and concrete API/permission/error contracts before creating tasks.md.
5. Commit those artifacts before implementation code, migrations, or feature tests.
   A separate spec-only PR is welcome for complex changes; ordered specification
   and implementation commits in one PR are also valid.
6. Implement tasks and verify scenarios and relevant regressions. Update and commit
   the specs first if behavior changes. Check off only completed, verified tasks.
7. Validate with `openspec validate --all --strict --no-interactive` and verify the
   code against the scenarios, using the optional agent verification workflow when
   available. Structural validation alone does not prove feature correctness.
8. Once implementation is complete and verified, synchronize delta specs and
   archive the change on the feature branch, using the official workflow or
   `openspec archive <change-name>`. Inspect the resulting capability specs.
   Include synchronization/archive and updated roadmap/docs in the delivery PR.
9. Open the PR to main with change links, scenario evidence, migration effects,
   compatibility changes, and limitations. Merge only after review/checks and
   appropriate merge authorization. Never push directly to main.

Do not archive planned changes as if implemented. The migrated roadmap proposals
are drafts: their Blocking Decisions sections must be resolved and concrete tasks
written before apply. Keep changes independently reviewable rather than shipping
an entire phase as one implementation PR. Later overlapping changes must rebase
their deltas against the synchronized capability specs.

Internal refactors can reference unchanged contracts. Pure documentation/tooling
changes can use OpenSpec's `skip_specs: true` metadata when a change folder is
needed; do not invent runtime requirements just to satisfy validation. Updating
existing specification documentation does not require a recursive feature spec.

## Definition of done

- Change artifacts preceded implementation and match the delivered behavior.
- Blocking decisions are resolved and applicable WHEN/THEN scenarios verified,
  including validation, authorization, visibility and material failure cases.
- Alembic changes preserve intended data and document rollback limitations.
- Capability specs reflect verified behavior; completed changes are archived and
  TODO.md and current-behavior documentation agree.
- The delivery is a reviewable PR to main, with the specification commit and
  validation evidence linked.

## Verification and tooling

See [OpenSpec setup](openspec/README.md) for CLI/agent integration. This repository's
artifact format is validated with OpenSpec 2.2.0. Run:

```shell
openspec validate --all --strict --no-interactive
uv run pytest -q -p no:cacheprovider
git diff --check
```

Run application tests for runtime changes. For documentation-only changes, check
OpenSpec structure, local links, requirement references, and whitespace. Tests use
isolated databases and must not connect to the developer's .env database. Use
disposable PostgreSQL for PostgreSQL-specific migrations/constraints and vector
tests. Normal AI tests mock providers.

README stays focused on project overview and usage. Contributor process lives here,
agent instructions in [AGENTS.md](AGENTS.md), architecture in docs/, and behavioral
contracts and proposed changes in openspec/. Do not maintain a parallel specs/
baseline or custom feature template.

## Repository-host enforcement

These files define the contributor/agent workflow. Host enforcement requires an
administrator to protect main with required PR reviews, CI checks once configured,
and restrictions on direct/force pushes. Documentation and templates do not
configure GitHub branch protection.
