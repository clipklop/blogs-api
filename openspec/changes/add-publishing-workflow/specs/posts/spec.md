# Post visibility delta

## MODIFIED Requirements

### Requirement: BASE-02 Post visibility

The service SHALL expose only published posts through public listing and slug
lookup. Authors SHALL explicitly select their own scope to read drafts and archives.
Numeric ID lookup SHALL still require authentication and apply the same visibility
policy. Non-owner private reads SHALL not disclose resource existence.

#### Scenario: Current public lookup

- **WHEN** an anonymous reader lists posts or looks up a draft or archived post by slug
- **THEN** private posts are excluded from lists and direct private lookup returns 404.

#### Scenario: Author private scope

- **WHEN** an authenticated author explicitly selects their own draft or archive scope
- **THEN** only that author's matching private posts can be returned.

#### Scenario: Numeric authentication

- **WHEN** an anonymous reader requests a post by numeric ID
- **THEN** the API returns 401.
