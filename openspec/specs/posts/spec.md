# Posts

## Purpose

Define current post creation, discovery, stable lookup, validation, and author-owned mutation behavior for API consumers.

## Requirements

### Requirement: BASE-02 Bounded post discovery

`GET /posts/` SHALL keep limit 1–100 (default 20), nonnegative offset (default 0), literal case-insensitive title/content search, and newest/oldest ordering with ID as timestamp tie-breaker. Scope and state filters SHALL apply before pagination. The API SHALL accept an exact normalized `tag` and a positive 32-bit integer `author_id`. Both filters SHALL combine with scope, state, and search before pagination and SHALL preserve visibility. Invalid filter values SHALL return 422.

#### Scenario: Combined filters

- **WHEN** an author requests `scope=mine&state=draft&search=python&sort=oldest&limit=1`
- **THEN** the response contains at most one matching draft owned by that author, ordered by ascending creation time and ID.

#### Scenario: Invalid pagination

- **WHEN** limit is 0 or greater than 100, or offset is negative
- **THEN** the API returns 422.

#### Scenario: Invalid list filters

- **WHEN** a caller supplies the removed `published` filter, an unknown state or scope, or a private state with public scope
- **THEN** the API returns 422.

#### Scenario: Tag and author discovery

- **WHEN** a reader supplies `tag=Python&author_id=1` with search, sorting, and pagination
- **THEN** only matching visible posts by author 1 appear once each, in the requested order and within the pagination bounds.

#### Scenario: Private discovery with tag filters

- **WHEN** a reader filters by a name shared between published and private posts
- **THEN** public scope returns only matching published posts, and authenticated owner scope returns only the caller's matching posts.

#### Scenario: Invalid tag and author filters

- **WHEN** the tag fails the tag name rules or the author ID is invalid or out of range
- **THEN** the API returns 422.

### Requirement: BASE-02 Post visibility

The API SHALL list published posts by default using `scope=public`. Explicit `scope=mine` SHALL require authentication and return only the caller's posts in all states unless filtered by `state`. Slug reads SHALL allow anonymous published access. Numeric reads SHALL require authentication. A draft or archive SHALL be readable by its author only.

#### Scenario: Current public lookup

- **WHEN** a reader uses public scope or requests a draft or archived post by slug without author credentials
- **THEN** the list contains only published posts and the private slug returns the same 404 as an absent slug.

#### Scenario: Author private scope

- **WHEN** an authenticated author lists `scope=mine` or requests their draft or archived post by ID or slug
- **THEN** the list contains only their own posts and their direct lookup returns 200.

#### Scenario: Numeric authentication

- **WHEN** an anonymous reader requests a post by numeric ID
- **THEN** the API returns 401.

#### Scenario: Non-author private lookup

- **WHEN** an authenticated non-author requests a draft or archive by ID or slug
- **THEN** each lookup returns the same 404 as its corresponding absent post.

#### Scenario: Credentials for owner scope and slug lookup

- **WHEN** a caller requests `scope=mine` without credentials or sends invalid credentials to that scope or the slug endpoint
- **THEN** the API returns 401 with a bearer challenge.

### Requirement: BASE-02 Stable slugs

Created posts SHALL have unique slugs that remain unchanged when their titles change.

#### Scenario: Title edit

- **WHEN** an author changes a post title
- **THEN** the post retains its original slug and remains reachable through that slug.

### Requirement: BASE-02 Author-owned mutations

Creation SHALL derive the owner from authentication and return 201 with state `draft`. Only the author SHALL update or delete a post. A non-author mutation SHALL return 403 for published posts and 404 for private posts. Successful deletion SHALL return 204 with no body.

#### Scenario: Authenticated creation

- **WHEN** a signed-in user creates a valid post while submitting another user's owner ID
- **THEN** the new post is a draft owned by the signed-in user.

#### Scenario: Non-owner modification

- **WHEN** another signed-in user attempts to update or delete a published post or a private post
- **THEN** the API returns 403 for the published post and the same 404 as an absent post for the private post, preserving both.

#### Scenario: Author deletion

- **WHEN** an author deletes their post
- **THEN** the API returns 204 with an empty body and later lookup returns 404.

### Requirement: BASE-02 Update validation

Content PATCH SHALL reject empty updates, unknown fields, and explicit null values with 422. Lookup or modification of a missing post SHALL return 404 after required authentication.

#### Scenario: Empty update

- **WHEN** an author submits an empty PATCH body
- **THEN** the API returns 422 without modifying the post.

#### Scenario: Missing post

- **WHEN** an authenticated user requests a nonexistent post ID
- **THEN** the API returns 404.

#### Scenario: Publication fields in content PATCH

- **WHEN** an author sends `state`, `published`, or `published_at` to `PATCH /posts/{post_id}`
- **THEN** the API returns 422 without updating the post.

### Requirement: CONTENT-01 Post representation

Post responses SHALL expose `state` and nullable UTC `published_at` in place of `published`. Post creation SHALL reject client-supplied publication fields with 422. List and lookup responses SHALL retain vote counts. Post responses SHALL include a `tags` array of unique normalized names sorted in ascending order, or an empty array.

#### Scenario: Draft representation

- **WHEN** an author creates a post with title and content
- **THEN** the response includes `"state":"draft"` and `"published_at":null` and omits `published`.

#### Scenario: Client-supplied state

- **WHEN** a create request includes `state`, `published`, or `published_at`
- **THEN** the API returns 422 and creates no row.

#### Scenario: Tags on post responses

- **WHEN** a caller creates, reads, updates, lists, or changes the publication state of a post
- **THEN** the post representation includes all assigned tags in sorted order, or an empty array for an untagged post.
