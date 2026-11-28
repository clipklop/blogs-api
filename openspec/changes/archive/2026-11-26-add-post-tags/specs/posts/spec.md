# Posts delta

## MODIFIED Requirements

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
