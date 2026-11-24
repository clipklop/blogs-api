# Users and Authentication

## Purpose

Define registration, credential validation, bearer authentication, and authenticated profile behavior without exposing password data.

## Requirements

### Requirement: BASE-03 User registration

POST /users/ SHALL register unique usernames and email addresses, hash passwords with bcrypt, and return 201. Passwords SHALL contain 6–71 characters and at most 72 UTF-8 bytes. Duplicate identifiers SHALL return 400 and invalid input SHALL return 422.

#### Scenario: Successful registration

- **WHEN** a caller registers valid unused identifiers
- **THEN** the API returns 201 and stores a password hash rather than the submitted password.

#### Scenario: Duplicate identifiers

- **WHEN** a caller registers an existing username or email
- **THEN** the API returns 400 and subsequent valid registration remains possible.

#### Scenario: Multibyte limit

- **WHEN** a submitted password exceeds 72 UTF-8 bytes
- **THEN** the API returns 422.

### Requirement: BASE-03 Bearer login

POST /login SHALL accept form username containing the user's email and password and return access_token and token_type bearer. Invalid credentials SHALL consistently return 401 with a bearer challenge.

#### Scenario: Valid login

- **WHEN** a registered user submits the correct email and password
- **THEN** the response contains a signed bearer access token.

#### Scenario: Invalid login

- **WHEN** the email is unknown or the password is incorrect
- **THEN** the API returns 401 with the same invalid-credentials message.

### Requirement: BASE-03 Credential validation

Protected operations SHALL validate token signatures using the configured algorithm, require UTC expiration and a positive integer user ID, and resolve an existing user. Missing, malformed, expired, or deleted-user credentials SHALL return 401 with a bearer challenge.

#### Scenario: Deleted user

- **WHEN** a formerly valid token references a deleted user
- **THEN** the protected operation returns 401.

#### Scenario: Invalid claims

- **WHEN** a token is expired, has no expiration, or has a noninteger user ID
- **THEN** the protected operation returns 401 rather than a server error.

### Requirement: BASE-03 Profile privacy

GET /users/me SHALL return the authenticated user's profile. User responses, including nested post authors, SHALL exclude passwords and hashes.

#### Scenario: Current profile

- **WHEN** an authenticated user requests /users/me
- **THEN** the response contains that user's profile without password data.

#### Scenario: Nested author

- **WHEN** a post response includes its author
- **THEN** the nested author contains neither password nor password hash.
