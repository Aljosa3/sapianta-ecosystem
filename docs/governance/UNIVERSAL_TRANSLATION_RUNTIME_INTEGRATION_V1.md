# UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1

Status: IMPLEMENTED

## 1. Integration Purpose

UNIVERSAL_TRANSLATION_RUNTIME_INTEGRATION_V1 integrates the Universal Translation Runtime as the canonical translation layer for AiGOL.

The integration establishes translation evidence before HIRR-compatible workflow routing and before operator-facing explanation.

Canonical flow:

```text
Human
-> Universal Translation Runtime
-> HIRR
-> Workflow Resolution
```

Canonical explanation flow:

```text
Governance
-> Universal Translation Runtime
-> Operator Explanation
```

## 2. Runtime Modules

Integration runtime:

`aigol/runtime/universal_translation_runtime_integration.py`

Operational ACLI routing integration:

`aigol/runtime/conversational_cli_runtime.py`

Primary integration entrypoints:

- `route_human_request_through_universal_translation`
- `create_operator_explanation_through_universal_translation`
- `reconstruct_universal_translation_runtime_integration_replay`

The existing ACLI router now records Human -> Governance Universal Translation evidence before workflow classification.

## 3. Human -> HIRR Integration

The operational ACLI routing path now performs:

```text
human_prompt
-> translate_human_to_governance
-> _classify_workflow
-> workflow selection
```

The routing decision artifact records:

- Universal Translation replay reference
- Universal Translation artifact hash
- Universal Translation source direction
- Universal Translation confidence

The routing result remains deterministic and preserves the existing workflow selection logic.

## 4. Governance -> Human Integration

The integration runtime performs:

```text
governance_state
-> translate_governance_to_human
-> deterministic operator explanation
-> optional LLM-assisted explanation
```

The Universal Translation Artifact remains the canonical explanation input.

Optional LLM-assisted explanation remains advisory and is invoked only after the deterministic Governance -> Human translation exists.

## 5. Compatibility Layer

The compatibility layer preserves existing operational interfaces while adding canonical translation evidence.

Compatibility is provided for:

- ACLI routing
- HIRR-compatible workflow resolution
- deterministic operator explanation
- optional LLM-assisted explanation
- replay reconstruction

Deprecated direct paths:

- Human -> HIRR without Universal Translation evidence
- Governance -> ACLI explanation without Universal Translation evidence

Deprecation means the direct path should no longer be treated as the canonical evidence path. It does not remove existing runtimes in this milestone.

## 6. Migration Plan

Phase 1: Additive Evidence Integration

- record Human -> Governance translation before ACLI workflow routing
- include translation reference and hash in routing artifacts
- provide wrapper runtime for canonical integration replay
- keep existing deterministic routing behavior unchanged

Phase 2: Explanation Integration

- route Governance -> Human explanation through Universal Translation Artifact generation
- preserve optional LLM-assisted explanation as advisory augmentation
- preserve deterministic fallback

Phase 3: Consumer Migration

- migrate downstream ACLI callsites to consume Universal Translation artifacts directly
- keep compatibility adapters until older direct explanation calls are removed
- require replay evidence for both translation directions

Phase 4: Deprecation Closure

- mark direct Human -> HIRR and direct Governance -> explanation callsites as legacy-only
- retain reconstruction support for old replay
- certify no operational path bypasses Universal Translation evidence

## 7. Replay Model

Human -> Governance integration writes:

`000_universal_human_to_governance_integration_recorded.json`

Governance -> Human integration writes:

`000_universal_governance_to_human_integration_recorded.json`

Operational ACLI routing also writes nested Universal Translation evidence under:

`universal_translation/human_to_governance`

Replay records:

- translation replay reference
- translation artifact hash
- routing replay reference
- routing decision hash
- workflow selection hash
- optional LLM-assisted explanation reference
- optional LLM-assisted explanation hash
- compatibility mode
- deprecated direct path
- authority-denial flags

Replay reconstruction verifies:

- wrapper replay hash
- integration artifact hash
- integration direction
- authority boundaries

## 8. ERR Integration

ERR evidence is passed through Governance -> Human translation inputs when supplied.

The integration layer records the translation artifact hash and explanation lineage. ERR remains evidence context only and does not authorize routing, approval, execution, or mutation.

## 9. Authority Boundaries

The integration runtime does not:

- approve proposals
- execute workflows
- invoke workers
- mutate governance state
- mutate repository state
- grant provider authority
- grant replay authority

LLM-assisted explanation remains optional and advisory.

ACLI runtime state remains authoritative for workflow state.

Replay remains the source of truth.

## 10. Fail-Closed Behavior

The integration fails closed when:

- Universal Translation artifact generation fails
- routing replay already exists
- routing artifacts cannot record translation references
- Governance -> Human translation input is malformed
- optional provider output violates explanation provider constraints
- integration replay is tampered
- authority flags are set

Failure does not authorize execution or mutate governance state.

## 11. Regression Coverage

Focused regression coverage verifies:

- ACLI conversational routing records Universal Translation reference and hash
- Human -> Governance integration routes through HIRR-compatible workflow resolution
- Governance -> Human integration emits operator explanation through Universal Translation
- optional provider-assisted explanation remains advisory
- integration replay reconstruction works
- tampered integration replay fails closed

Validation commands:

```bash
python -m pytest tests/test_universal_translation_runtime_integration_v1.py -q
python -m pytest tests/test_human_to_governance_translation_runtime_v1.py tests/test_governance_to_human_translation_runtime_v1.py tests/test_adaptive_translation_escalation_runtime_v1.py tests/test_replay_derived_translation_learning_runtime_v1.py tests/test_universal_translation_runtime_integration_v1.py tests/test_universal_translation_artifact_schema_v1.py -q
python -m py_compile aigol/runtime/universal_translation_runtime_integration.py aigol/runtime/conversational_cli_runtime.py aigol/runtime/human_to_governance_translation_runtime.py aigol/runtime/governance_to_human_translation_runtime.py aigol/runtime/adaptive_translation_escalation_runtime.py aigol/runtime/replay_derived_translation_learning_runtime.py aigol/runtime/universal_translation_artifact_schema.py
git diff --check
```

## 12. Final Verdict

UNIVERSAL_TRANSLATION_RUNTIME_FULLY_INTEGRATED
