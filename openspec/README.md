# OpenSpec for Blogs API

This repository uses OpenSpec's `spec-driven` schema. Read
[CONTRIBUTING.md](../CONTRIBUTING.md), [AGENTS.md](../AGENTS.md), and the
[architecture notes](../docs/architecture.md) before planning a change.

## Layout

- `config.yaml`: project context, artifact rules, and apply/archive guidance.
- `specs/<capability>/spec.md`: authoritative implemented behavior.
- `changes/<change-name>/proposal.md`: motivation, scope, capabilities, and dependencies.
- `changes/<change-name>/specs/<capability>/spec.md`: proposed requirement deltas.
- `changes/<change-name>/design.md`: technical decisions and migration design.
- `changes/<change-name>/tasks.md`: concrete implementation and verification tasks,
  created only after blocking decisions are resolved.
- `changes/<change-name>/.openspec.yaml`: schema and creation metadata.
- `changes/archive/<date>-<change-name>/`: completed change history.

## Implemented capability inventory

| Capability | Original requirement IDs | Contract |
| --- | --- | --- |
| Persistence | BASE-01 | [spec](specs/persistence/spec.md) |
| Posts | BASE-02 | [spec](specs/posts/spec.md) |
| Users and authentication | BASE-03 | [spec](specs/user-auth/spec.md) |
| Publishing | CONTENT-01 | [spec](specs/publishing/spec.md) |
| Post tags | CONTENT-02 | [spec](specs/tags/spec.md) |
| Voting | Existing voting baseline and CONTENT-01 visibility | [spec](specs/voting/spec.md) |

Public post discovery and voting require published content. Authors can read their own
private posts. See the [publishing archive](changes/archive/2026-11-25-add-publishing-workflow/proposal.md) for the implementation change.
The [post tags archive](changes/archive/2026-11-26-add-post-tags/proposal.md) records assignment and discovery behavior.
Known vote-removal and concurrent-creation gaps are recorded explicitly.

## Draft change inventory

All migrated proposals below are **drafts**, not implemented or ready to apply.
Their original requirement IDs remain traceable. Each preserves the previous
requirements and records blocking decisions; implementation tasks are deliberately
absent until the design and contracts are complete. Split broader drafts into
smaller independently reviewable changes during refinement.

| Phase | Requirement ID | Change |
| --- | --- | --- |
| 3 | CONTENT-03 | [Post comments](changes/add-post-comments/proposal.md) |
| 3 | CONTENT-04 | [Voting correctness](changes/complete-voting/proposal.md) |
| 4 | OPS-01 | [API diagnostics](changes/add-api-diagnostics/proposal.md) |
| 4 | OPS-02 | [Runtime health and configuration](changes/harden-service-runtime/proposal.md) |
| 4 | OPS-03 | [Delivery and recovery](changes/improve-delivery-and-recovery/proposal.md) |
| 5 | ACCOUNT-01 | [Account verification and recovery](changes/add-account-recovery/proposal.md) |
| 5 | ACCOUNT-02 | [Refresh sessions and revocation](changes/add-refresh-sessions/proposal.md) |
| 5 | ACCOUNT-03 | [Reports and moderation](changes/add-content-moderation/proposal.md) |
| 5 | ACCOUNT-04 | [Account deactivation and deletion](changes/add-account-deactivation/proposal.md) |
| 6 | AI-01 | [AI author assistance](changes/add-author-assistance/proposal.md) |
| 6 | AI-02 | [Semantic search and recommendations](changes/add-semantic-discovery/proposal.md) |
| 6 | AI-03 | [AI moderation assistance](changes/add-ai-moderation-assistance/proposal.md) |
| 6 | AI-04 | [Grounded blog answers](changes/add-blog-question-answering/proposal.md) |
| 6 | AI-05 | [AI post translations](changes/add-post-translations/proposal.md) |
| 6 | AI-06 | [AI jobs and artifact lifecycle](changes/add-ai-job-infrastructure/proposal.md) |
| 6 | AI-07 | [AI verification and evaluation](changes/add-ai-evaluation/proposal.md) |

[TODO.md](../TODO.md) keeps delivery order and verified completion. Do not treat an
OpenSpec artifact-completion status as implementation completion. Existing drafts
can acquire additional deltas when refined against changed baseline contracts.

## Authoring conventions

Use `### Requirement: <stable name>`, SHALL/MUST language, and at least one
`#### Scenario: <name>` with explicit WHEN and THEN steps per requirement.
Current capability specs use `## Purpose` and `## Requirements`. Change deltas
use `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`,
or `## RENAMED Requirements` as appropriate.

A MODIFIED block must use the exact current requirement name and include the full
updated requirement and all scenarios. For a new capability, include its Purpose
in the delta. Read the current capability before creating a delta; synchronize
dependencies before applying changes that overlap.

For new changes, prefer the CLI-generated artifacts over copying a project-specific
feature template. Do not edit current behavioral specs to claim a proposed feature
before it is implemented and verified. Then synchronize the deltas and archive the
completed change on its delivery branch, including both in the PR to main.
Archiving does not merge a PR or deploy the service.

## CLI and agent setup

Install the official OpenSpec CLI as documented in the
[installation guide](https://openspec.dev/docs/installation). This repository uses
the format validated with OpenSpec 2.2.0. The CLI is a development tool, not an
application runtime dependency.

From the repository root:

```shell
openspec init --scope project --tools codex
openspec list --specs
openspec list
openspec new change <change-name>
openspec validate --all --strict --no-interactive
```

The init command installs the official agent workflows; the specification
reorganization itself does not vendor generated third-party skills. Review any
generated files and preserve this repository's stricter spec-before-code and
branch/PR rules. See the official [setup guide](https://openspec.dev/docs/setup).

Use the agent's propose workflow to complete the proposal, delta specs, design
when needed, and tasks; verify before archive. Enable the optional verification
workflow through OpenSpec profiles if it is not installed. CLI validation checks
document structure, not authorization correctness or code/spec agreement.

Do not archive the migrated drafts to make them appear shipped.
