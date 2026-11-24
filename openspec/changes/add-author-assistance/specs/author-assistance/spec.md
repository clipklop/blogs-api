# AI author assistance

## Purpose

Define ai author assistance behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: AI-01 Author-only suggestions

Authors SHALL request title/summary/tag suggestions, feedback, outlines, and selected-text rewrites for their own posts, including drafts. Structured output and existing tag IDs SHALL be validated.

#### Scenario: Another author's draft

- **WHEN** a user requests assistance for another author's draft
- **THEN** the request is denied without exposing draft text.

### Requirement: AI-01 Explicit revision-safe approval

Suggestions SHALL be stored separately and SHALL NOT replace accepted content without explicit author approval. Approval SHALL atomically check ownership and source revision.

#### Scenario: Stale approval

- **WHEN** a post changes after a suggestion was generated and the author tries to approve it
- **THEN** approval reports a conflict and the newer content remains unchanged.
