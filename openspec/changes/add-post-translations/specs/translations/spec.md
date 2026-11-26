# AI post translations

## Purpose

Define ai post translations behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: AI-05 Separate approved translations

Author-requested translations SHALL be stored separately, bound to the source revision, and require explicit approval before publication.

#### Scenario: Translation generated

- **WHEN** a worker generates translated content
- **THEN** the original remains unchanged and the translation is not automatically public.

### Requirement: AI-05 Translation freshness

Source edits SHALL mark related translations stale.

#### Scenario: Edited source

- **WHEN** an author edits a translated post
- **THEN** its translations are marked stale according to the finalized public fallback policy.
