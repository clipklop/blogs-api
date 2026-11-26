# AI moderation assistance

## Purpose

Define ai moderation assistance behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: AI-03 Human-reviewed classifications

Model classifications SHALL flag eligible posts/comments for authorized human review with recorded model version and reasons, without independently changing policy or roles.

#### Scenario: Flagged comment

- **WHEN** the model flags a comment
- **THEN** a signal is recorded for human review rather than silently granting permissions or changing policy.

### Requirement: AI-03 Classification boundaries

Safety classifications SHALL remain distinct from spam/community-rule logic, and review queues SHALL NOT disclose private drafts beyond the approved moderation scope.

#### Scenario: Private draft signal

- **WHEN** assistance processes content outside a moderator's authorized scope
- **THEN** that content does not become readable through the moderation queue.
