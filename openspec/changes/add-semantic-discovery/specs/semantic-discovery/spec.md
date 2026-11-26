# Semantic search and recommendations

## Purpose

Define semantic search and recommendations behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: AI-02 Shared semantic discovery

Semantic search and related-post recommendations SHALL reuse compatible current embeddings of eligible public published content while keyword search remains available.

#### Scenario: Related posts

- **WHEN** a public reader requests related posts
- **THEN** the response excludes the source post and all nonpublic posts.

### Requirement: AI-02 Visibility before retrieval

Visibility and embedding compatibility SHALL filter candidates before ranking/limiting and be rechecked before returning cached or uncached results. Embeddings/private artifacts SHALL NOT be exposed.

#### Scenario: Unpublished cached result

- **WHEN** a previously indexed post is unpublished before a cached search response is delivered
- **THEN** the response excludes that post.
