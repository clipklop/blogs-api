# Voting

## Purpose

Define existing authenticated vote creation and aggregate counts while keeping the planned vote-removal and race-handling fixes explicit.

## Requirements

### Requirement: Authenticated vote creation

POST /vote/ SHALL derive the voter from authentication and persist a vote for an existing post when dir is 1. A detected existing vote SHALL return 409, and a missing post SHALL return 404.

#### Scenario: Create vote

- **WHEN** a signed-in user votes for an existing post without a prior vote
- **THEN** the stored vote uses the authenticated user's ID.

#### Scenario: Detected duplicate

- **WHEN** the same user repeats a vote after the first has committed
- **THEN** the API returns 409.

### Requirement: Aggregate vote counts

Post listing and ID/slug lookup SHALL include the number of stored votes for each post, including zero when no votes exist.

#### Scenario: Post without votes

- **WHEN** a reader retrieves an existing post without stored votes
- **THEN** the response reports votes as zero.

## Known gaps

Vote removal currently omits the commit call, the request schema unnecessarily
requires user_id, and a concurrent duplicate can escape the precheck. These gaps
are proposed in the complete-voting change; they are not claimed as implemented.
