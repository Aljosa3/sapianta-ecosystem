# ADAPTIVE_TRANSLATION_ESCALATION_RUNTIME_V1

Status: IMPLEMENTED

## 1. Runtime Purpose

ADAPTIVE_TRANSLATION_ESCALATION_RUNTIME_V1 implements adaptive provider escalation for the Universal Bidirectional Translation Runtime.

The runtime starts with a deterministic Universal Translation Artifact and escalates to optional translation providers only when policy requires additional assistance.

The runtime preserves deterministic translation as the baseline and records every escalation decision as replay-visible evidence.

## 2. Runtime Module

Runtime module:

`aigol/runtime/adaptive_translation_escalation_runtime.py`

Primary entrypoints:

- `run_adaptive_translation_escalation`
- `reconstruct_adaptive_translation_escalation_replay`

The runtime integrates with:

- `aigol/runtime/universal_translation_artifact_schema.py`
- deterministic Human -> Governance translation artifacts
- deterministic Governance -> Human translation artifacts
- replay serialization
- ERR evidence references
- non-authoritative provider contracts

## 3. Escalation Order

The runtime evaluates translation in this order:

1. deterministic translation
2. low-cost translation provider
3. medium-capability translation provider
4. high-capability translation provider

Provider candidates are sorted by tier before invocation.

Allowed provider tiers:

- `LOW_COST_TRANSLATION_PROVIDER`
- `MEDIUM_CAPABILITY_TRANSLATION_PROVIDER`
- `HIGH_CAPABILITY_TRANSLATION_PROVIDER`

## 4. Escalation Triggers

Escalation occurs only when one or more policy reasons are present:

- ambiguity exceeds threshold
- confidence is below threshold
- fidelity requirements fail
- translation completeness is insufficient
- operator requests improved explanation

If no escalation reason exists, the deterministic translation artifact remains selected and no provider is invoked.

## 5. Provider Interface

Provider candidates are supplied as bounded runtime objects:

```text
provider_id
provider_tier
cost_class
estimated_cost
provider
```

The provider may be:

- a callable accepting a provider request artifact;
- an object exposing `translate(request_artifact)`.

Provider request artifacts include:

- deterministic translation artifact
- deterministic translation hash
- source direction
- bounded translation task
- preservation requirements
- escalation reasons
- forbidden claims
- advisory-only flags

Provider response payloads must include:

- translation candidate
- confidence
- limitations
- preserved authoritative references
- cost metrics
- advisory-only flag
- authority-denial flags

Malformed or authority-claiming provider output is rejected.

## 6. Authority Invariants

Provider output is never authoritative.

The runtime rejects provider output that claims:

- governance authority
- approval authority
- execution authority
- mutation authority
- provider authority

Provider output cannot:

- approve execution
- execute workflows
- mutate governance state
- mutate repository state
- mutate replay state
- alter deterministic source evidence

LLM role:

- translation assistance only
- never authority
- never execution
- never approval
- never governance

## 7. Provider Output Validation

Provider output is checked against deterministic authoritative references.

For `HUMAN_TO_GOVERNANCE`, preserved references are derived from the deterministic governance payload entity set.

For `GOVERNANCE_TO_HUMAN`, preserved references are derived from the deterministic human-readable payload's authoritative state references.

If provider-preserved references differ from deterministic references, provider output is rejected and replay records the rejection reason.

## 8. Selected Translation Artifact

The runtime returns:

- deterministic translation artifact
- selected translation artifact
- provider attempt evidence
- escalation reasons
- fallback reason, if any
- cost metrics
- replay reference

When provider output is accepted, the selected translation artifact is a Universal Translation Artifact with provider metadata and authority flags still false.

When providers are unavailable, malformed, rejected, or absent, the selected artifact remains deterministic and the fallback reason is replay-visible.

## 9. Cost Metrics

Replay records:

- provider attempt count
- estimated total cost
- cost units
- per-provider cost metrics
- provider tier
- provider cost class

Cost metrics are observational only. They do not grant provider authority or alter workflow execution.

## 10. Replay Model

Replay writes:

`000_adaptive_translation_escalation_recorded.json`

Replay records:

- deterministic stage decision
- escalation policy
- escalation reasons
- provider request artifacts
- provider response artifacts
- provider rejection reasons
- accepted provider translation artifact, if any
- deterministic fallback reason, if any
- selected translation artifact
- cost metrics
- ERR evidence hash, if provided
- authority-denial flags

Replay reconstruction verifies:

- wrapper replay hash
- adaptive escalation artifact hash
- deterministic translation artifact hash
- selected translation artifact hash
- nested provider request and response hashes
- provider translation artifact validity
- authority-denial flags

Tampered replay fails closed.

## 11. ERR Integration

ERR evidence may be supplied as context.

The runtime records:

- ERR evidence snapshot
- ERR evidence hash

ERR evidence does not authorize provider escalation. It only becomes replay-visible context for audit and later review.

## 12. Fail-Closed Behavior

The runtime fails closed when:

- deterministic translation artifact is malformed
- provider candidates are malformed
- provider tier is invalid
- provider output is malformed
- provider output claims authority
- provider output fails authoritative-reference fidelity
- provider-produced Universal Translation Artifact is invalid
- replay evidence is missing or tampered
- nested provider artifact hashes do not verify

Provider failures do not execute workflows or mutate governance state. The safe fallback remains deterministic translation.

## 13. Validation Evidence

Focused validation covers:

- deterministic selection when no escalation is required
- low-cost provider first ordering
- accepted provider translation artifact creation
- provider authority-claim rejection
- escalation to the next provider tier
- deterministic fallback on unavailable providers
- operator-requested explanation escalation
- replay reconstruction
- malformed deterministic artifact failure
- replay tamper detection

Validation commands:

```bash
python -m pytest tests/test_adaptive_translation_escalation_runtime_v1.py -q
python -m pytest tests/test_human_to_governance_translation_runtime_v1.py tests/test_governance_to_human_translation_runtime_v1.py tests/test_adaptive_translation_escalation_runtime_v1.py tests/test_universal_translation_artifact_schema_v1.py -q
python -m py_compile aigol/runtime/adaptive_translation_escalation_runtime.py aigol/runtime/human_to_governance_translation_runtime.py aigol/runtime/governance_to_human_translation_runtime.py aigol/runtime/universal_translation_artifact_schema.py
git diff --check
```

## 14. Final Verdict

ADAPTIVE_TRANSLATION_ESCALATION_RUNTIME_READY
