# Reports and moderation

## Purpose

Define reports and moderation behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: ACCOUNT-03 Restricted moderation

Moderators SHALL review reported posts/comments without unrestricted account access or implicit private-draft visibility.

#### Scenario: Moderator private lookup

- **WHEN** a moderator requests an unrelated private draft
- **THEN** the role alone does not grant access.

### Requirement: ACCOUNT-03 Reports and audit

Reporting and a paginated moderation queue SHALL record review decisions, reasons, and audit history.

#### Scenario: Hide reported content

- **WHEN** an authorized moderator hides a reported post
- **THEN** the action and reason are recorded and the post leaves public direct, nested, discovery, and AI results.
