# GOVERNANCE_FAILURE_SEMANTICS_V1

## Scope

This milestone introduces the first explicit governance failure semantics layer for AiGOL.

It defines deterministic failure classification for:

- contracts;
- authorization;
- routing;
- lineage replay;
- session continuity.

## Failure Semantics

Allowed failure semantics are:

- `FAIL_CLOSED`
- `REJECT`
- `INVALIDATE_LINEAGE`
- `TERMINATE_SESSION`
- `QUARANTINE_REQUIRED`

Allowed severity levels are:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

## Failure Evidence

Failure evidence contains:

- `failure_id`
- `failure_type`
- `severity`
- `related_session_id`
- `related_contract_id`
- `related_authorization_id`
- `reason`
- `created_at`
- `evidence_hash`

## Guarantees

- Failure semantics only.
- Deterministic failure classification.
- Replay-visible failure evidence.
- Append-only failure lineage.
- Immutable failure evidence.
- Fail-closed malformed failure handling.
- No recovery automation introduced.
- No orchestration introduced.
- No autonomous runtime introduced.

## Non-Goals

- Recovery automation.
- Retries.
- Orchestration.
- Async runtime.
- Workflow systems.
- Policy learning.
- Autonomous mitigation.
- Semantic reasoning.
- LLM integration.
- Provider execution.
- Process termination.

## Boundary

This layer defines what governance failure means. It does not recover runtime state, retry execution, mutate contracts, mutate authorization, invoke providers, terminate processes, or perform automatic mitigation.

## Certification

`GOVERNANCE_FAILURE_SEMANTICS_V1` certifies deterministic governance failure classification, replay-visible failure evidence, append-only failure lineage, immutable failure artifacts, and no recovery automation or autonomous runtime.
