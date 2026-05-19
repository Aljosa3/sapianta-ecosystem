# AGOL Bridge Transport Spec v1

# Status

Draft v1

# Purpose

This specification defines the AGOL Bridge v1 transport model for moving ChatGPT-generated governed task packages to execution providers such as Codex and returning deterministic result packages.

The purpose is to replace manual copy and paste with replay-safe transport while preserving governance guarantees, explicit approval boundaries, lifecycle visibility, and deterministic result return.

This specification defines transport guarantees and lifecycle behavior. It does not define autonomous cognition.

# Core Principle

- ChatGPT performs reasoning.
- Codex performs execution.
- AGOL governs transport and lifecycle.

# Non-Goals

AGOL Bridge v1 explicitly excludes:

- semantic planning;
- autonomous reasoning;
- hidden orchestration;
- self-modifying governance;
- unrestricted execution.

# Architecture

The governed transport flow is:

Human
-> ChatGPT
-> Governed Task Package
-> AGOL Bridge
-> Codex
-> Result Package
-> AGOL Bridge
-> ChatGPT

Each transition must preserve replay identity, lifecycle state, approval status, and deterministic evidence.

# Transport Model

AGOL Bridge v1 uses file-based transport. Task packages and result packages move through deterministic directories according to lifecycle state.

Transport guarantees:

- package movement is deterministic;
- package contents are represented as canonical JSON;
- replay events are appended to replay logs;
- dispatched packages are immutable;
- unknown or invalid packages fail closed into quarantine.

# Directory Structure

The bridge transport directory contains:

- `incoming/` - newly received governed task packages.
- `approved/` - packages with explicit approval recorded.
- `dispatched/` - immutable packages sent to execution.
- `results/` - result packages returned from execution providers.
- `replay_log/` - append-only JSONL replay records.
- `quarantine/` - invalid, unknown, malformed, or unsafe packages.

# Task Package Schema

Each governed task package is JSON and must include:

- `task_id` - stable task identity.
- `governance_mode` - declared governance mode for the task.
- `risk_class` - bounded risk classification.
- `approval_required` - boolean approval requirement.
- `codex_prompt` - execution prompt intended for Codex.
- `constraints` - execution and governance constraints.
- `expected_outputs` - expected result shape or artifacts.
- `metadata` - replay, source, lineage, and operator context.

Packages missing required fields are invalid and must fail closed.

# Result Package Schema

Each result package is JSON and must include:

- `status` - execution result status.
- `tests` - test commands and outcomes when applicable.
- `files_changed` - changed file list when applicable.
- `artifacts` - generated artifacts or artifact references.
- `summary` - concise execution summary.
- `requires_human_review` - boolean review requirement.

Results that cannot be validated must remain visible and must not be silently finalized.

# Lifecycle States

AGOL Bridge v1 recognizes these lifecycle states:

- `CREATED`
- `NORMALIZED`
- `WAITING_FOR_APPROVAL`
- `APPROVED`
- `DISPATCHED`
- `EXECUTING`
- `RETURNED`
- `VALIDATED`
- `FINALIZED`
- `QUARANTINED`
- `FAILED`

# Lifecycle Rules

- Dispatched tasks are immutable.
- Tasks requiring approval may not be dispatched before approval is recorded.
- Unknown states fail closed.
- Invalid state transitions fail closed.
- Every lifecycle transition must append a replay log entry.
- Replay logs must identify the package, prior state, next state, timestamp, and content hash.
- Quarantined packages may not be dispatched.
- Failed packages remain replay-visible.

# Replay Format

Replay is recorded as append-only JSONL. Each line is one canonical JSON object.

Each replay record must include:

- `event_id`
- `task_id`
- `event_type`
- `previous_state`
- `next_state`
- `package_hash`
- `timestamp`
- `actor`
- `reason`

Replay records must not be rewritten or silently removed.

# Deterministic Guarantees

AGOL Bridge v1 requires:

- canonical JSON serialization;
- append-only replay logs;
- SHA-256 package hashes;
- no silent overwrite;
- no hidden execution;
- deterministic lifecycle transition records;
- visible quarantine for invalid or unsafe packages.

# Failure Semantics

Failure handling is fail-closed.

- Schema invalidation moves the package to `quarantine/`.
- Unknown lifecycle states move the package to `quarantine/`.
- Missing approval blocks dispatch.
- Partial results are stored in `results/` and marked as requiring human review.
- Execution failure produces a result package with failure status.
- Malformed results are quarantined or marked as requiring human review.

# Security Boundary

AGOL Bridge may not directly execute arbitrary ChatGPT commands.

ChatGPT output is treated as reasoning output and proposed task material. Execution requires governed packaging, schema validation, lifecycle controls, replay logging, and approval boundaries before dispatch.

# Acceptance Criteria

AGOL Bridge v1 is acceptable when:

- task packages are schema-validated before movement;
- result packages are schema-validated before finalization;
- replay JSONL entries are generated for every lifecycle transition;
- lifecycle transitions follow the defined state model;
- missing approval blocks dispatch;
- invalid packages enter quarantine;
- dispatched packages are immutable;
- no hidden execution path exists.
