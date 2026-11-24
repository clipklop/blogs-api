# Posts

## Purpose

Define current post creation, discovery, stable lookup, validation, and author-owned mutation behavior for API consumers.

## Requirements

### Requirement: BASE-02 Bounded post discovery

GET /posts/ SHALL support limit from 1 through 100 (default 20), nonnegative offset, published filtering, literal case-insensitive title/content search, and newest/oldest ordering with ID as timestamp tie-breaker.

#### Scenario: Combined filters

- **WHEN** a reader supplies valid filtering, search, sorting, and pagination parameters
- **THEN** the response contains only matching posts in the requested stable order within the requested bounds.

#### Scenario: Invalid pagination

- **WHEN** limit is 0 or greater than 100, or offset is negative
- **THEN** the API returns 422.

### Requirement: BASE-02 Post visibility

The service SHALL expose published and unpublished posts through public listing and slug lookup. Numeric ID lookup SHALL require authentication. This records current behavior; private publishing is proposed separately.

#### Scenario: Current public lookup

- **WHEN** an anonymous reader lists posts or looks up an existing unpublished post by slug
- **THEN** the response may include that unpublished post.

#### Scenario: Numeric authentication

- **WHEN** an anonymous reader requests a post by numeric ID
- **THEN** the API returns 401.

### Requirement: BASE-02 Stable slugs

Created posts SHALL have unique slugs that remain unchanged when their titles change.

#### Scenario: Title edit

- **WHEN** an author changes a post title
- **THEN** the post retains its original slug and remains reachable through that slug.

### Requirement: BASE-02 Author-owned mutations

Creation SHALL derive the author from authentication and return 201. Only the author SHALL update or delete a post; non-owner mutations SHALL return 403. Successful deletion SHALL return 204 with no body.

#### Scenario: Authenticated creation

- **WHEN** a signed-in user creates a valid post while submitting another user's owner ID
- **THEN** the new post belongs to the signed-in user.

#### Scenario: Non-owner modification

- **WHEN** another signed-in user tries to update or delete a post
- **THEN** the API returns 403 and preserves the post.

#### Scenario: Author deletion

- **WHEN** an author deletes their post
- **THEN** the API returns 204 with an empty body and later lookup returns 404.

### Requirement: BASE-02 Update validation

PATCH SHALL reject empty updates, unknown fields, and explicit null values with 422. Lookup or modification of a missing post SHALL return 404 after required authentication.

#### Scenario: Empty update

- **WHEN** an author submits an empty PATCH body
- **THEN** the API returns 422 without modifying the post.

#### Scenario: Missing post

- **WHEN** an authenticated user requests a nonexistent post ID
- **THEN** the API returns 404.
