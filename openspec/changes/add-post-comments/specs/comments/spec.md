# Post comments

## Purpose

Define post comments behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: CONTENT-03 Comment creation and listing

Authenticated users SHALL create comments only on published posts. Comment listing SHALL be paginated and respect parent visibility.

#### Scenario: Hidden parent

- **WHEN** a reader requests comments on a post they cannot read
- **THEN** the response does not reveal that post's comments.

### Requirement: CONTENT-03 Comment ownership

Commenters SHALL edit/delete their own comments. Post authors SHALL be allowed to delete comments on their posts but SHALL NOT rewrite another user's comment.

#### Scenario: Post-author edit

- **WHEN** a post author tries to rewrite another user's comment
- **THEN** the operation is denied and the comment remains unchanged.
