# Post tags

## Purpose

Define post tags behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: CONTENT-02 Normalized tag assignment

Tags SHALL have unique normalized names and duplicate post/tag assignments SHALL be rejected or deduplicated according to the finalized contract.

#### Scenario: Repeated assignment

- **WHEN** an author assigns the same normalized tag twice
- **THEN** only one association is stored.

### Requirement: CONTENT-02 Tag and author filtering

Tag and author filters SHALL compose with search, ordering, pagination, and post visibility without granting private access.

#### Scenario: Combined discovery

- **WHEN** a public reader filters by tag and author
- **THEN** only matching published posts are returned within pagination bounds.
