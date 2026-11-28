# Post tags tasks

## 1. Persistence and API

- [x] 1.1 Add the tag relationship and Alembic revision with uniqueness, cascade, and a reversible schema change.
- [x] 1.2 Implement authenticated replacement and tag representation. Reuse ownership checks and cover normalized shared names, replacement, clearing, validation, and unchanged timestamps.
- [x] 1.3 Add discovery filters and verify visibility, pagination, ordering, and invalid values alongside existing post behavior.

## 2. Verification and delivery

- [x] 2.1 Verify data preservation, downgrade, delete cascade, and concurrent shared names with SQLite and disposable PostgreSQL where applicable.
- [x] 2.2 Run the regression suite and OpenSpec validation, document the API, update the roadmap, and synchronize and archive verified requirements for the delivery PR.
