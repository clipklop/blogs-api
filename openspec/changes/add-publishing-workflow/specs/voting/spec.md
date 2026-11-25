# Voting visibility delta

## MODIFIED Requirements

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
