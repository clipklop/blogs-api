# Post comment tasks

## Implementation

- [ ] 1.1 Append the comments migration and model with body length and referential constraints.
- [ ] 1.2 Implement comment creation, paginated listing, edit, and delete with bounded input, shared publication policy, and parent-first authorization.

## Verification and delivery

- [ ] 2.1 Verify permissions, parent visibility, serialization, validation, pagination, and persisted mutations through HTTP integration tests.
- [ ] 2.2 Verify migration preservation, cascades, and competing publication and comment operations on disposable PostgreSQL and applicable SQLite tests.
- [ ] 2.3 Document the API, run regression and strict OpenSpec validation, update fulfilled roadmap items, and sync and archive verified specs for the PR.
