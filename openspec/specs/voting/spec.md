# Voting

## Purpose

Define existing authenticated vote creation and aggregate counts while keeping the planned vote-removal and race-handling fixes explicit.

## Requirements

### Requirement: Authenticated vote creation

POST /vote/ SHALL derive the voter from authentication and persist a vote for an existing published post when dir is 1. An existing vote detected on a published post SHALL return 409. For either direction, a draft, archived, or missing target SHALL return the same 404 before vote lookup or mutation, including for the post author.

#### Scenario: Create vote

- **WHEN** a signed-in user votes for an existing published post without a prior vote
- **THEN** the stored vote uses the authenticated user's ID.

#### Scenario: Detected duplicate

- **WHEN** the same user repeats a vote on a published post after the first has committed
- **THEN** the API returns 409.

#### Scenario: Private vote target

- **WHEN** an authenticated caller submits either vote direction for a draft or archive
- **THEN** the API returns the same 404 as for a missing target and preserves existing votes.

#### Scenario: Concurrent unpublish

- **WHEN** unpublishing commits before a competing vote acquires the post row lock
- **THEN** the vote receives the missing-target response and does not change vote counts.

### Requirement: Aggregate vote counts

Post listing and ID/slug lookup SHALL include the number of stored votes for each post, including zero when no votes exist.

#### Scenario: Post without votes

- **WHEN** a reader retrieves an existing post without stored votes
- **THEN** the response reports votes as zero.

## Known gaps

Vote removal currently omits the commit call, the request schema unnecessarily
requires user_id, and a concurrent duplicate can escape the precheck. These gaps
are proposed in the complete-voting change; they are not claimed as implemented.
