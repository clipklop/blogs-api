# Grounded blog answers

## Purpose

Define grounded blog answers behavior for the Blogs API while preserving authorization, data integrity, and observable failure handling.

## ADDED Requirements

### Requirement: AI-04 Source-supported answers

Answers SHALL use currently public published passages and include supporting post/passage references or explicitly report insufficient information.

#### Scenario: Unsupported question

- **WHEN** retrieved evidence does not support an answer
- **THEN** the response acknowledges insufficient information instead of inventing support.

### Requirement: AI-04 Source visibility lifecycle

Answer generation and response delivery SHALL recheck source visibility; cached answers SHALL invalidate on source edits, unpublish/hide, and deletion.

#### Scenario: Source hidden

- **WHEN** a cited source becomes hidden before an answer is delivered
- **THEN** the answer is regenerated from eligible evidence or withheld without exposing hidden content.

### Requirement: AI-04 Untrusted source instructions

Retrieved content SHALL NOT change authorization, expose private content, or trigger unrelated actions.

#### Scenario: Injected post

- **WHEN** a retrieved passage instructs the assistant to reveal drafts
- **THEN** the instruction does not grant access or disclose private content.
