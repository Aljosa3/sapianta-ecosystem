# REPLAY_DERIVED_TRANSLATION_LEARNING_RUNTIME_V1

Status: IMPLEMENTED

## 1. Runtime Purpose

REPLAY_DERIVED_TRANSLATION_LEARNING_RUNTIME_V1 implements replay-derived learning for the Universal Bidirectional Translation Runtime.

The runtime analyzes completed translation replay evidence and identifies repeated translation patterns that may be suitable for future deterministic rule promotion.

The runtime does not modify deterministic rules. It emits improvement proposals only.

## 2. Runtime Module

Runtime module:

`aigol/runtime/replay_derived_translation_learning_runtime.py`

Primary entrypoints:

- `analyze_replay_derived_translation_learning`
- `reconstruct_replay_derived_translation_learning_replay`

The runtime integrates with:

- Universal Translation Artifact Schema
- replay history
- provider explanation evidence
- deterministic translation evidence
- human confirmation evidence
- clarification history
- ERR evidence
- PPP improvement proposal governance

## 3. Inputs

Required inputs:

- Universal Translation Artifacts
- learning identifier
- creation timestamp
- replay directory

Optional inputs:

- replay history wrappers
- provider explanations
- deterministic translations
- human confirmations
- clarification history
- ERR evidence
- promotion policy

All translation artifacts are validated through the Universal Translation Artifact Schema before analysis.

## 4. Responsibilities

The runtime deterministically performs:

- translation replay artifact validation
- repeated pattern detection
- equivalent human expression clustering
- stable governance mapping detection
- human confirmation counting
- clarification history counting
- provider evidence summarization
- promotion confidence calculation
- deterministic translation candidate proposal generation
- replay persistence
- replay reconstruction

## 5. Pattern Detection

Patterns are grouped by:

- source direction
- stable mapping signature

For Human -> Governance artifacts, equivalent expressions are derived from the replayed human request or normalized text.

For Governance -> Human artifacts, equivalent expressions are derived from the human-readable summary or operator action text.

Artifact identifiers and target paths are normalized during expression comparison so repeated operator phrasing can be detected without binding the pattern to a single artifact name.

## 6. Stable Governance Mapping

A stable governance mapping means multiple replayed translation artifacts produced the same deterministic mapping signature.

Mapping signatures are derived from the target translation payload:

- `translated_governance_payload` for Human -> Governance
- `human_readable_payload` for Governance -> Human

Volatile explanation and reference fields are excluded from the mapping signature where appropriate.

## 7. Promotion Confidence

Promotion confidence uses:

- occurrence count
- human confirmation count
- equivalent expression count
- mapping stability ratio
- clarification penalty

Default promotion policy:

- minimum occurrences: 3
- minimum human confirmations: 1
- minimum equivalent expressions: 2
- minimum promotion confidence: 0.8

The runtime may identify no promotion candidates when evidence is insufficient.

## 8. Improvement Proposal Generation

When a cluster satisfies promotion policy, the runtime emits:

`TRANSLATION_DETERMINISTIC_RULE_IMPROVEMENT_PROPOSAL_V1`

The proposal includes:

- source cluster
- source direction
- canonical expression
- equivalent expressions
- mapping signature
- proposed rule kind
- promotion confidence
- supporting translation artifact hashes
- policy used
- PPP route requirement
- human approval requirement

The proposal is not an implementation. It is an input to the governed improvement pipeline.

## 9. PPP And Human Approval Boundary

Every generated proposal records:

- `ppp_route_required`: true
- `human_approval_required`: true
- `implementation_authorized`: false
- `deterministic_rule_modified`: false
- `runtime_behavior_modified`: false

Deterministic rules may change only after:

Replay-derived proposal
-> PPP routing
-> governance review
-> explicit human approval
-> governed implementation workflow
-> validation
-> replay

## 10. Replay Model

Replay writes:

`000_replay_derived_translation_learning_recorded.json`

Replay records:

- translation artifact hashes
- pattern clusters
- improvement proposals
- provider evidence summary
- clarification history summary
- human confirmation summary
- ERR evidence hash
- PPP requirement
- authority-denial flags

Replay reconstruction verifies:

- replay ordering
- wrapper replay hash
- learning artifact hash
- proposal artifact hashes
- proposal-only authority boundaries

Tampered replay fails closed.

## 11. Authority Rules

Replay-derived translation learning cannot:

- change deterministic runtime rules
- mutate governance state
- mutate repository state
- approve promotion
- execute workers
- request execution
- mutate replay after persistence

Learning output is proposal-only.

Human authority and governance workflows remain mandatory before any deterministic rule promotion.

## 12. Fail-Closed Requirements

The runtime fails closed when:

- no translation artifacts are available
- translation artifacts are malformed
- replay history entries are malformed
- optional evidence lists are malformed
- promotion policy is malformed
- replay evidence is missing during reconstruction
- replay hash verification fails
- learning artifact hash verification fails
- proposal artifact hash verification fails
- any artifact attempts to grant authority

## 13. Validation Evidence

Focused validation covers:

- repeated confirmed pattern proposal generation
- unconfirmed pattern non-promotion
- unstable mappings remaining separate clusters
- replay history wrapper ingestion
- replay reconstruction
- malformed translation artifact fail-closed behavior
- replay tamper detection
- proposal-only authority boundaries

Validation commands:

```bash
python -m pytest tests/test_replay_derived_translation_learning_runtime_v1.py -q
python -m pytest tests/test_human_to_governance_translation_runtime_v1.py tests/test_governance_to_human_translation_runtime_v1.py tests/test_adaptive_translation_escalation_runtime_v1.py tests/test_replay_derived_translation_learning_runtime_v1.py tests/test_universal_translation_artifact_schema_v1.py -q
python -m py_compile aigol/runtime/replay_derived_translation_learning_runtime.py aigol/runtime/adaptive_translation_escalation_runtime.py aigol/runtime/human_to_governance_translation_runtime.py aigol/runtime/governance_to_human_translation_runtime.py aigol/runtime/universal_translation_artifact_schema.py
git diff --check
```

## 14. Final Verdict

REPLAY_DERIVED_TRANSLATION_LEARNING_RUNTIME_READY
