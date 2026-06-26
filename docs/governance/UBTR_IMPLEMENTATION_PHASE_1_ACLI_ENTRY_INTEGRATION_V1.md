# UBTR Implementation Phase 1 ACLI Entry Integration V1

Status: implementation record.

This artifact records Phase 1 of the Generation 2 UBTR migration:

```text
Human
  |
  v
ACLI Entry
  |
  v
Human -> Governance Translation
  |
  v
Canonical Semantic Artifact
  |
  v
ACLI / HIRR Compatibility Routing
```

## 1. Objective

Integrate UBTR at the ACLI human-input entry point before semantic routing.

Phase 1 does not remove existing ACLI or HIRR marker logic.
Existing marker logic remains active as a compatibility fallback.

## 2. Implemented Changes

Runtime changes:

- added `aigol/runtime/canonical_semantic_artifact_runtime.py`;
- updated `aigol/runtime/conversational_cli_runtime.py` to create a Canonical
  Semantic Artifact after Human -> Governance translation;
- updated conversational routing evidence to record:
  - canonical semantic artifact replay reference;
  - canonical semantic artifact hash;
  - semantic routing source;
  - canonical artifact type;
- added semantic-first routing for decisive governed development candidates;
- preserved existing `_classify_workflow(...)` marker logic as fallback.

Test changes:

- added `tests/test_canonical_semantic_artifact_runtime_v1.py`;
- extended `tests/test_universal_translation_runtime_integration_v1.py`.

## 3. Behavior

### 3.1 Decisive UBTR Semantic Route

When Human -> Governance translation produces a high-confidence
`GOVERNED_DEVELOPMENT_WORKFLOW` candidate with no material ambiguity, ACLI uses
the Canonical Semantic Artifact as the routing source.

Recorded routing source:

```text
CANONICAL_SEMANTIC_ARTIFACT
```

### 3.2 Compatibility Fallback

When UBTR translation is present but marks the request ambiguous, ACLI retains
existing compatibility marker behavior.

Recorded routing source:

```text
COMPATIBILITY_FALLBACK
```

This preserves Generation 1 behavior while making the semantic source
replay-visible.

## 4. Authority Boundaries

No authority boundary changed.

UBTR / Canonical Semantic Artifact:

- may translate;
- may provide semantic workflow candidate evidence;
- may record replay-visible semantic evidence;
- may not approve;
- may not authorize execution;
- may not invoke providers;
- may not dispatch workers;
- may not mutate governance;
- may not mutate replay.

ACLI / HIRR compatibility routing:

- still performs workflow selection;
- still owns compatibility fallback during migration.

Replay:

- remains source of truth;
- records translation, canonical semantic artifact, routing decision, workflow
  selection, and returned routing artifact.

## 5. Replay Impact

Every successful conversational routing replay now includes:

- Universal Translation replay reference;
- Universal Translation artifact hash;
- Canonical Semantic Artifact replay reference;
- Canonical Semantic Artifact hash;
- semantic routing source.

The Canonical Semantic Artifact is stored under:

```text
<routing-replay>/canonical_semantic_artifact/
```

The Human -> Governance translation remains stored under:

```text
<routing-replay>/universal_translation/human_to_governance/
```

## 6. Governance Impact

No governance semantics changed.

The implementation adds evidence only:

- it does not change approval rules;
- it does not change execution authorization;
- it does not change provider rules;
- it does not change worker behavior;
- it does not change replay semantics;
- it does not remove compatibility logic.

## 7. Regression Coverage

Added or extended regression coverage verifies:

- Canonical Semantic Artifact generation from Human -> Governance translation;
- stable replay reconstruction;
- tampered replay fails closed;
- ACLI routing records the canonical artifact reference and hash;
- decisive UBTR semantic route selects `GOVERNED_DEVELOPMENT_WORKFLOW`;
- ambiguous UBTR route preserves compatibility fallback;
- no provider, worker, approval, execution, governance mutation, or replay
  mutation authority is granted.

## 8. Validation Results

Executed:

```text
python -m py_compile aigol/runtime/canonical_semantic_artifact_runtime.py aigol/runtime/conversational_cli_runtime.py aigol/runtime/human_to_governance_translation_runtime.py
```

Result:

```text
PASS
```

Executed:

```text
python -m pytest tests/test_canonical_semantic_artifact_runtime_v1.py tests/test_universal_translation_runtime_integration_v1.py -q
```

Result:

```text
8 passed
```

Executed:

```text
python -m pytest tests/test_acli_certified_continuation_orchestration_v1.py tests/test_acli_end_to_end_human_prompt_certification_v1.py tests/test_conversation_native_development_context_integration_v1.py tests/test_universal_intake_layer_v1.py tests/test_conversational_cli_runtime_v1.py tests/test_universal_translation_runtime_integration_v1.py tests/test_canonical_semantic_artifact_runtime_v1.py -q
```

Result:

```text
183 passed
```

Executed:

```text
python -m pytest -q
```

Result:

```text
5391 passed, 4 skipped
```

## 9. Full Pytest Feasibility

Full pytest was feasible and passed.

## 10. Final Verdict

UBTR_IMPLEMENTATION_PHASE_1_ACLI_ENTRY_INTEGRATION_READY
