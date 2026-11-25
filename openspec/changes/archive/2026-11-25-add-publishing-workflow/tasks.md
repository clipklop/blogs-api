# Publishing workflow tasks

## 1. Schema and migration

- [x] 1.1 Append an Alembic revision and update the post model with constrained `state` and `published_at`. Backfill publication state and timestamp, preserve votes during SQLite batch rebuilds, and implement the documented downgrade.
- [x] 1.2 Extend `tests/test_migrations.py` for fresh upgrade and upgrade/downgrade fixtures with published, unpublished, and archived rows and existing votes. Verify schema constraints, preserved columns, timestamp backfill, and foreign keys on SQLite and disposable PostgreSQL.

## 2. API and visibility

- [x] 2.1 Update post creation, response, content PATCH, and list schemas. Reject obsolete publication fields and filters, preserve existing content validation and response fields, and add `scope` and `state` to the list contract.
- [x] 2.2 Apply shared publication visibility before filtering and pagination, to both direct lookup routes, and to ownership checks. Keep numeric authentication, validate supplied slug credentials, and require credentials for `scope=mine`.
- [x] 2.3 Add the publication PUT route. Implement the transition table and error responses, preserve the first publication time, and handle repeated targets without a write. Use a PostgreSQL post-row lock when authorizing post mutations and checking vote eligibility.
- [x] 2.4 Restrict the existing vote endpoint to published targets in both directions. Return its missing-target response for private posts and leave existing vote counts intact.

## 3. Verification and delivery

- [x] 3.1 Verify scenario coverage in `tests/test_posts.py` and `tests/test_auth.py` for anonymous, author, and other-user access, all list and lookup paths, combined search and pagination, invalid filters and bodies, stable slugs, ownership, and vote totals.
- [x] 3.2 Test every transition pair, timestamp behavior, 401/403/404/409/422 responses, and published/private voting. Verify competing archive/publish and unpublish/vote operations with independent PostgreSQL sessions.
- [x] 3.3 Run the regression suite and PostgreSQL migration/concurrency checks. Review generated OpenAPI and document the current client contract and rollback precautions in the appropriate project docs.
- [x] 3.4 Verify all OpenSpec scenarios against implementation, validate the artifacts, sync and archive the verified change, reconcile the overlapping vote-visibility draft and its dependency link, and update only completed roadmap items. Include the verification evidence in the PR to `main`.
