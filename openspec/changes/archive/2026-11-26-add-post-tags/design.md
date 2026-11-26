# Post tags design

## Context

CONTENT-02 builds on the [publishing contract](../../specs/publishing/spec.md) and existing post routes. Tags describe posts in any state the author can manage.

## Decisions

- Use `PUT /posts/{post_id}/tags` for atomic replacement and return `{"tags":["fastapi","python"]}`. The body uses the same shape. An empty array clears assignments. Keep content and publication writes focused on their existing fields.
- Accept up to ten raw names. Strip leading and trailing whitespace, require 1–32 ASCII letters, digits, or single hyphen separators, lowercase, then deduplicate and sort. Apply the same normalization to the single `tag` filter. Use `author_id` with the positive PostgreSQL integer range.
- Reuse the author mutation check and post-row lock for writes. Add a tag table keyed by name and an association with a composite primary key, cascading foreign keys, and a tag-first index. Keep unused names for reuse. Use conflict-safe inserts in sorted name order on PostgreSQL and SQLite so concurrent posts can share newly created tags. Replace associations and commit within the same transaction.
- Apply filters to the existing post query through an association existence predicate so each post still contributes one row. Eager-load tags in the same query for list and lookup responses so they share the post visibility snapshot. Preserve post timestamps for tag-only updates.

## Migration plan

Append a migration after `61d07bfb923e` that creates the tag and association tables. Existing posts start with empty tags. Downgrade drops associations and names and preserves all previously existing tables and data. Changes to tags are lost on downgrade.

## Risks

The ASCII alphabet intentionally bounds the initial taxonomy. The release adds a response field to all post representations. Applications with strict response schemas need to accept that field.
