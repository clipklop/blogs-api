# publishing Specification

## Purpose

Define author-controlled publication states and preserve first publication time across edits, state changes, and data migration.

## Requirements

### Requirement: CONTENT-01 Publishing states

`PUT /posts/{post_id}/publication` SHALL accept exactly one required field, `state`, and return 200 with the updated post. Durably allowed transitions are draft to published or archived, published to draft or archived, and archived to draft. Requests for the current state SHALL succeed without writing. Archived to published SHALL return 409.

#### Scenario: Restore and publish

- **WHEN** an author puts `{"state":"draft"}` on their archived post and then puts `{"state":"published"}`
- **THEN** both requests return 200 and the post is publicly visible only after the second request.

#### Scenario: Direct publication of an archive

- **WHEN** an author requests published for an archived post
- **THEN** the API returns 409 with `{"detail":"Restore archived posts to draft before publishing"}` and leaves the post archived.

#### Scenario: Invalid publication payload

- **WHEN** an author sends missing, null, unknown, or additional fields for the publication contract
- **THEN** the API returns 422 and leaves the post unchanged.

#### Scenario: Repeated transition request

- **WHEN** an author requests the post's current state
- **THEN** the API returns 200 and preserves both timestamps.

### Requirement: CONTENT-01 Publication permissions

Only the authenticated author SHALL change a post's state. Missing or invalid credentials SHALL return 401 with a bearer challenge. A non-author SHALL receive 403 for a published post and the same 404 as an absent post for a private post.

#### Scenario: Non-author transition

- **WHEN** another authenticated user requests a state change for a published or private post
- **THEN** the API returns 403 or 404 respectively without updating either post.

#### Scenario: Anonymous transition

- **WHEN** a caller omits credentials on the publication endpoint
- **THEN** the API returns 401.

### Requirement: CONTENT-01 First publication timestamp

The service SHALL set `published_at` to the current UTC time on first publication and preserve it across later edits, unpublishing, archiving, restoration, and republication. State validation and timestamp assignment SHALL occur atomically against the latest locked state.

#### Scenario: First publication

- **WHEN** an author publishes a never-published draft
- **THEN** the response includes a non-null UTC first publication time.

#### Scenario: Republication

- **WHEN** the author edits, unpublishes, archives, restores, and republishes a previously published post
- **THEN** its original `published_at` is preserved through the sequence.

#### Scenario: Competing transitions

- **WHEN** an archive request commits before a competing publish request evaluates the same post
- **THEN** the publish request returns 409 and the committed archive state is preserved.

### Requirement: CONTENT-01 Publication migration

Upgrade SHALL map true to published with `published_at=created_at`, and false to draft with a null timestamp. Downgrade SHALL map only published to true and discard publication timestamps. Post identities, content, owners, slugs, ratings, timestamps, and votes SHALL survive either direction.

#### Scenario: Existing published post

- **WHEN** the migration upgrades an existing published post
- **THEN** its publication time equals its existing creation time and associated data is preserved.

#### Scenario: Existing unpublished post

- **WHEN** the migration upgrades an existing unpublished post
- **THEN** it is a draft with a null publication time and associated data is preserved.

#### Scenario: Downgrade of archived content

- **WHEN** a database with an archived post is downgraded
- **THEN** that row becomes unpublished under the old schema and its votes are preserved.
