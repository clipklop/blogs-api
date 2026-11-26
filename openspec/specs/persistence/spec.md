# Persistence

## Purpose

Define migration-managed storage and ownership guarantees that preserve existing blog data across schema evolution.

## Requirements

### Requirement: BASE-01 Migration-managed schema

The service SHALL manage schema evolution through Alembic using the same DATABASE_URL as the API. Application startup SHALL NOT create or update tables.

#### Scenario: Fresh database

- **WHEN** all migrations are applied to an empty database
- **THEN** the database contains the schema required by the application.

#### Scenario: Application startup

- **WHEN** the API starts against an existing database
- **THEN** startup does not create or alter tables.

### Requirement: BASE-01 Data preservation

Schema evolution SHALL preserve existing posts, author assignments, and votes unless a change explicitly documents a different data policy and rollback limitations.

#### Scenario: Ownership backfill

- **WHEN** the author requirement migration upgrades posts without authors
- **THEN** those posts receive a generated disabled author account and existing posts, owners, and votes remain present.

#### Scenario: Schema consistency

- **WHEN** migrations have reached head
- **THEN** stored post content and author IDs are non-null and post slugs are uniquely indexed.
