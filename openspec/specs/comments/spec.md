# comments Specification

## Purpose

Let readers discuss posts and let commenters and post authors manage comments within the parent post's visibility rules.

## Requirements

### Requirement: CONTENT-03 Comment creation and listing

`POST /posts/{post_id}/comments` SHALL create comments only for authenticated callers on published posts and return 201. The author SHALL come from authentication. `GET /posts/{post_id}/comments` SHALL allow anonymous access to published posts and allow only the authenticated post author to list a private post's comments. GET SHALL return 200 with an array, newest first by creation time and then descending ID.

#### Scenario: Create and read

- **WHEN** an authenticated user posts `{"body":" Hello "}` on a published post and an anonymous reader lists its comments
- **THEN** creation returns 201 and the list includes the stored body `Hello` with the authenticated author's ID.

#### Scenario: Pagination

- **WHEN** a reader lists a visible post with equal-timestamp comments using offset and limit
- **THEN** the selected page follows decreasing creation time and ID. Limit defaults to 20 and accepts 1 through 100. Offset defaults to 0 and accepts 0 through 2147483647. An empty page returns `[]`.

#### Scenario: Parent visibility

- **WHEN** an author lists comments after moving a published post to draft or archive
- **THEN** the author can still read those comments and other callers receive the same 404 as for an absent parent. Creating a new comment on a private or absent parent returns that same 404 even for the post author.

#### Scenario: Credentials

- **WHEN** a caller supplies invalid credentials to the listing endpoint or omits valid credentials on a write
- **THEN** the service returns 401 with a bearer challenge.

### Requirement: CONTENT-03 Comment ownership

`PATCH /posts/{post_id}/comments/{comment_id}` SHALL allow only the commenter to replace the body, return 200, preserve creation time, and set the update time. DELETE at that path SHALL allow the commenter or parent post author and return 204 with an empty body. Both SHALL require the caller to be able to read the parent and the comment to belong to that parent.

#### Scenario: Published comment mutation

- **WHEN** the commenter edits or deletes their comment on a published post
- **THEN** the edit is visible to later readers or the comment is removed, respectively.

#### Scenario: Post-author moderation

- **WHEN** the post author tries to edit another user's comment and then deletes it on their own visible post
- **THEN** the edit returns 403 and preserves the body, and deletion succeeds even if that post is now private.

#### Scenario: Wrong owner or parent

- **WHEN** an unrelated authenticated user attempts to mutate an existing comment on a published post
- **THEN** the API returns 403. A missing or mismatched comment under a visible parent returns 404, and a hidden or missing parent returns the same parent 404 before checking comment existence.

### Requirement: CONTENT-03 Comment validation and representation

Create and edit SHALL require exactly `body`, a string with 1–1000 Unicode characters after trimming outer whitespace, excluding U+0000 and invalid Unicode scalar values. Invalid body or pagination input SHALL return 422 and leave stored comments unchanged. Responses SHALL expose only `id`, `post_id`, `author_id`, `body`, `created_at`, and `updated_at`, with timestamps in UTC.

#### Scenario: Invalid input

- **WHEN** the body is missing, blank, null, overlong, contains an invalid character, or supplies extra fields such as `author_id`
- **THEN** create and edit return 422 without a write. An out-of-range limit or offset returns 422.

#### Scenario: Timestamp fields

- **WHEN** a comment is created and then edited
- **THEN** creation returns equal UTC timestamps, and editing retains the creation time and sets the UTC update time.

### Requirement: CONTENT-03 Comment retention

The service SHALL retain comments across publication transitions, cascade deletion when their parent post or author account is deleted, and check the committed parent state before a concurrent comment mutation. Migration SHALL create an empty comments table. Downgrade SHALL drop only comment data.

#### Scenario: Concurrent unpublication

- **WHEN** unpublication commits before a waiting comment creation checks the parent state
- **THEN** creation returns 404 and no comment is inserted.

#### Scenario: Cascade and rollback

- **WHEN** a post or commenter is deleted or the comments revision is downgraded
- **THEN** dependent comments are removed and downgrade preserves pre-existing post, account, tag, and vote records.
