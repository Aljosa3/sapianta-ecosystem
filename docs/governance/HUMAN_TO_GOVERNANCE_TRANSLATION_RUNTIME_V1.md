# HUMAN_TO_GOVERNANCE_TRANSLATION_RUNTIME_V1

Status: IMPLEMENTED

## 1. Runtime Purpose

HUMAN_TO_GOVERNANCE_TRANSLATION_RUNTIME_V1 implements the first deterministic Human -> Governance translation runtime for Universal ACLI.

The runtime exists to convert a natural-language operator request into a replay-visible Universal Translation Artifact without invoking providers, executing workflows, approving actions, or mutating governance state.

This runtime proves that human language can enter the governance stack as a bounded translation artifact before any authoritative workflow decision occurs.

## 2. Runtime Module

Runtime module:

`aigol/runtime/human_to_governance_translation_runtime.py`

Primary entrypoints:

- `translate_human_to_governance`
- `reconstruct_human_to_governance_translation_replay`

The runtime uses:

- `aigol/runtime/universal_translation_artifact_schema.py`
- `aigol/runtime/transport/serialization.py`
- `aigol/runtime/models.py`

## 3. Inputs

Required inputs:

- natural-language human request
- translation request identifier
- creation timestamp
- replay directory

Optional inputs:

- session context
- operator context
- available product identifiers
- available domain identifiers
- available workflow identifiers

All inputs must be JSON-safe after normalization. Malformed or missing required inputs fail closed.

## 4. Outputs

The runtime outputs a Universal Translation Artifact with:

- `source_direction`: `HUMAN_TO_GOVERNANCE`
- normalized intent
- extracted entities
- requested actions
- domain candidate
- workflow candidate
- ambiguity flags
- confidence
- deterministic fallback status
- replay reference
- authority-denial flags

The runtime also writes a deterministic replay wrapper:

`000_human_to_governance_translation_recorded.json`

## 5. Deterministic Translation Responsibilities

The runtime deterministically performs:

- request normalization
- action detection
- domain detection
- artifact identifier extraction
- target path extraction
- ambiguity detection
- confidence assignment
- governance payload population
- replay artifact persistence
- replay reconstruction validation

No LLM provider is used.

## 6. Governance Payload Semantics

The translated governance payload is a candidate only.

It may include:

- `governance_intent_status`: `TRANSLATION_CANDIDATE`
- `domain_candidate`
- `workflow_candidate`
- `intent_family`
- `requested_actions`
- `approval_required`
- `execution_requested`
- `entities`
- `clarification_required`
- `clarification_questions`

These fields do not authorize workflow execution. They provide evidence for downstream HIRR, ACLI, and governance routing logic.

## 7. HIRR And ACLI Integration

The runtime is designed to sit before or beside HIRR as deterministic translation evidence.

HIRR and ACLI remain authoritative for:

- clarification lifecycle
- workflow selection
- approval state
- execution authorization
- replay interpretation

This runtime may inform HIRR and ACLI, but it does not replace them.

## 8. Replay Integration

Replay is the source of truth for translation evidence.

Replay records:

- authoritative translation input metadata
- source natural-language payload hash
- normalized intent
- governance payload candidate
- ambiguity flags
- confidence
- provider non-use
- deterministic fallback status
- artifact hash
- wrapper replay hash

Replay reconstruction verifies:

- replay ordering
- wrapper hash
- Universal Translation Artifact schema validity
- artifact hash
- source direction

Tampered replay fails closed.

## 9. Authority Boundaries

The runtime cannot:

- invoke providers
- approve execution
- execute workflows
- mutate governance state
- mutate repository state
- grant worker authority
- mutate replay after persistence

All authority flags are false.

The constitutional invariant remains preserved:

LLM proposes.
AiGOL governs.
Worker executes.
Replay records.

This runtime adds:

Translation records.

## 10. Fail-Closed Requirements

The runtime fails closed when:

- the human request is empty
- translation metadata is malformed
- context lists contain non-string values
- session context is not a JSON object
- replay evidence is missing
- replay ordering is invalid
- replay hash verification fails
- Universal Translation Artifact validation fails
- replay source direction is not `HUMAN_TO_GOVERNANCE`

Fail-closed translation never proceeds to execution.

## 11. Validation Evidence

Focused validation covers:

- deterministic output
- stable artifact hashes
- governance artifact entity extraction
- ambiguity detection
- unsafe approval bypass detection
- malformed request failure
- replay reconstruction
- replay tamper detection
- schema compatibility

Validation commands:

```bash
python -m pytest tests/test_human_to_governance_translation_runtime_v1.py tests/test_universal_translation_artifact_schema_v1.py -q
python -m py_compile aigol/runtime/human_to_governance_translation_runtime.py aigol/runtime/universal_translation_artifact_schema.py
git diff --check
```

## 12. Final Verdict

HUMAN_TO_GOVERNANCE_TRANSLATION_RUNTIME_READY
