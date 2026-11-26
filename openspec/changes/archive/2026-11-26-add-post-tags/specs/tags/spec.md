# Post tags

## Purpose

Provide a reusable taxonomy of normalized tag names and let authors manage how it applies to their posts.

## ADDED Requirements

### Requirement: CONTENT-02 Normalized tag assignment

`PUT /posts/{post_id}/tags` SHALL accept exactly a `tags` array with up to 10 strings. Each trimmed name SHALL have 1–32 ASCII letters or digits with optional single hyphens between groups. The service SHALL lowercase names, deduplicate them, atomically replace prior assignments, and return 200 with the sorted names in `{"tags":[...]}`. An empty array SHALL clear assignments. Invalid input SHALL return 422.

#### Scenario: Normalized replacement

- **WHEN** an author replaces an assigned tag with `{"tags":[" Python ","python","Fast-API"]}`
- **THEN** the response and stored assignments contain exactly `fast-api` and `python` in that order and the post timestamps are preserved.

#### Scenario: Clear and repeat

- **WHEN** an author sends `{"tags":[]}` twice
- **THEN** both requests return 200 with an empty array and the post has no assigned tags.

#### Scenario: Invalid replacement

- **WHEN** the body omits the array, includes extra fields, exceeds ten input entries, or contains null, a non-string, a blank name, an overlong name, or unsupported characters
- **THEN** the API returns 422 and all previous assignments remain.

### Requirement: CONTENT-02 Tag assignment permissions

Only a post's authenticated author SHALL replace its tags, in any publication state. Missing or invalid credentials SHALL return 401 with a bearer challenge. An authenticated non-author SHALL receive 403 for a published post and the same 404 as an absent post for a private post.

#### Scenario: Author and non-author replacement

- **WHEN** an author assigns tags to a draft or archive and another authenticated user attempts replacement on a published post, a private post, and an absent post
- **THEN** the author receives 200 and the other user receives 403, 404, and 404 respectively.

#### Scenario: Missing or invalid token

- **WHEN** the request has no bearer token or an invalid token
- **THEN** the service returns 401 with a bearer challenge.

### Requirement: CONTENT-02 Tag persistence

A normalized name SHALL be shared across posts, with at most one assignment per post and name. Post deletion SHALL remove its assignments and preserve the shared names. Existing posts SHALL start without tags after upgrade. Downgrade SHALL remove tag data while preserving posts, accounts, and votes.

#### Scenario: Concurrent assignment of a new name

- **WHEN** authors concurrently assign the same new normalized name to different posts
- **THEN** both requests succeed and the database contains one name and an assignment for each post.

#### Scenario: Post deletion and schema rollback

- **WHEN** an author deletes a tagged post or a database with tags is downgraded
- **THEN** deletion removes only that post's assignments and downgrade discards tags while preserving remaining posts, users, and votes.
