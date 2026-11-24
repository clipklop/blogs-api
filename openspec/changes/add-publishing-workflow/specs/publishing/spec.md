# Publishing workflow

## Purpose

Define publishing workflow behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: CONTENT-01 Publishing states

Posts SHALL support draft, published, and archived states. Only authors SHALL transition their posts; the transition contract SHALL be finalized before implementation.

#### Scenario: First publication

- **WHEN** an author first publishes a draft
- **THEN** published_at is set and subsequent edits or republication preserve it.

### Requirement: CONTENT-01 Publication migration

Existing published flags SHALL migrate true to published and false to draft. Existing published rows SHALL receive published_at from created_at.

#### Scenario: Existing published post

- **WHEN** a migration upgrades an existing published post
- **THEN** its content, owner, slug, and votes are preserved and published_at equals its previous created_at.

### Requirement: CONTENT-01 Private resource visibility

Public readers SHALL see only published content. Author-only draft/archive scope SHALL apply consistently to direct and nested reads and future retrieval results.

#### Scenario: Private lookup

- **WHEN** a non-owner attempts to read a draft or archived post by list, ID, or slug
- **THEN** the post is excluded from lists and direct lookup returns 404 after any required authentication.
