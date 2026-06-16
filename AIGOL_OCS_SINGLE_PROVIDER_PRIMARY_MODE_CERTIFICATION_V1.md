# AIGOL_OCS_SINGLE_PROVIDER_PRIMARY_MODE_CERTIFICATION_V1

## Objective

Design certification for deterministic single-provider primary operation in conversational OCS.

Goal:

```text
OCS_LLM_COGNITION
-> exactly one successful provider cognition artifact
-> deterministic single-provider primary mode
-> no standard multi-provider comparison requirement
-> replay-visible evidence
-> human-facing cognition result
```

No new governance layer is introduced.

## Current One-Provider Path Reconstruction

Conversational OCS dispatch currently enters:

```text
aigol/cli/aigol_cli.py
-> _run_conversational_ocs_llm_cognition(...)
-> run_ocs_llm_cognition_end_to_end(...)
```

The conversational provider contract factory returns one provider contract:

```text
_conversation_ocs_cognition_provider_contracts(...)
-> [openai]
```

The contract is explicitly marked:

```text
single_provider_only = True
multi_provider_cognition_scope = False
```

The conversational call already passes:

```text
single_provider_primary_mode = True
```

The end-to-end runtime then executes:

```text
OCS context assembly
-> multi-provider cognition runtime with one provider contract
-> provider cognition availability gate
-> single-provider primary comparison compatibility artifact
-> continuity and clarification
-> end-to-end artifact
```

The single-provider compatibility artifact records:

```text
comparison_method = single_provider_primary_mode_no_comparison
comparison_created = False
single_provider_primary_mode = True
comparison_performed = False
human_review_required = True
non_authoritative = True
```

## Why Standard Comparison Is Selected In The Unsafe Path

The lower-level end-to-end runtime defaults to:

```text
single_provider_primary_mode = False
```

After provider availability certification, the gate allows comparison whenever:

```text
successful_provider_count > 0
```

Therefore, if a direct caller provides exactly one successful provider and does not set `single_provider_primary_mode=True`, the current runtime path is:

```text
successful_provider_count = 1
provider_availability_status = PROVIDER_COGNITION_AVAILABLE
selected_next_stage = COGNITION_COMPARISON
single_provider_primary_mode = False
-> run_cognition_comparison_runtime(...)
-> FAILED_CLOSED: at least two cognition artifacts are required for comparison
```

This is deterministic and fail-closed, but the mode-selection reason is not replay-visible as its own stage.

## Deterministic Mode-Selection Rules

Add an explicit mode-selection decision between provider availability and comparison execution:

```text
OCS_PROVIDER_COGNITION_AVAILABILITY_GATE
-> OCS_SINGLE_PROVIDER_PRIMARY_MODE_SELECTION
-> COGNITION_COMPARISON or SINGLE_PROVIDER_PRIMARY_COMPATIBILITY
```

Rules:

| Condition | Selected mode | Selected next stage |
| --- | --- | --- |
| `successful_provider_count == 0` | none | fail closed at provider availability gate |
| `successful_provider_count == 1` and all provider contracts are `single_provider_only == True` | `SINGLE_PROVIDER_PRIMARY` | single-provider compatibility artifact |
| `successful_provider_count == 1` and caller explicitly requires multi-provider comparison | `MULTI_PROVIDER_COMPARISON_REQUIRED` | fail closed before comparison |
| `successful_provider_count == 1` and provider contract mode is ambiguous | `MODE_SELECTION_FAILED_CLOSED` | fail closed before comparison |
| `successful_provider_count >= 2` | `MULTI_PROVIDER_COMPARISON` | standard cognition comparison |

The existing boolean can remain as a compatibility input, but certification should make the deterministic decision replay-visible and derivable from provider contracts plus successful provider count.

## Architecture Impact

Runtime impact is local to OCS cognition end-to-end orchestration.

Affected surfaces:

```text
aigol/runtime/ocs_llm_cognition_end_to_end_runtime.py
aigol/cli/aigol_cli.py
tests/test_ocs_llm_cognition_end_to_end_runtime_v1.py
tests/test_conversational_ocs_cognition_binding_v1.py
tests/test_real_openai_conversational_attachment_v1.py
```

No changes are required to:

```text
governance conformance
PPP
authorization
worker lifecycle
provider registry
provider adapter contracts
OCS comparison semantics
```

The comparison runtime remains unchanged: standard comparison still requires at least two cognition artifacts.

## Runtime Modifications

Add:

```text
OCS_SINGLE_PROVIDER_PRIMARY_MODE_SELECTION_ARTIFACT_V1
```

The mode-selection artifact should be created after provider availability and before comparison.

Minimum fields:

```text
artifact_type
runtime_version
mode_selection_id
multi_provider_result_bundle_reference
multi_provider_result_bundle_hash
provider_availability_artifact_hash
provider_count
successful_provider_count
failed_provider_count
successful_provider_ids
provider_contract_hashes
provider_contract_mode_flags
requested_single_provider_primary_mode
selected_mode
selected_next_stage
comparison_required
comparison_performed
fail_closed
failure_reason
authority_flags
approval_created
worker_invoked
execution_requested
dispatch_requested
governance_modified
replay_modified
created_at
artifact_hash
```

Selection outputs:

```text
selected_mode = SINGLE_PROVIDER_PRIMARY
selected_next_stage = SINGLE_PROVIDER_PRIMARY_COMPATIBILITY
comparison_required = False
```

or:

```text
selected_mode = MULTI_PROVIDER_COMPARISON
selected_next_stage = COGNITION_COMPARISON
comparison_required = True
```

or:

```text
selected_mode = MODE_SELECTION_FAILED_CLOSED
selected_next_stage = FAILED_CLOSED
fail_closed = True
```

End-to-end artifact should include:

```text
mode_selection_artifact_hash
selected_cognition_mode
mode_selection_status
comparison_required
comparison_performed
lineage_refs.mode_selection_artifact_hash
```

Replay reconstruction should include:

```text
stage_replay.mode_selection
selected_cognition_mode
mode_selection_status
comparison_required
comparison_performed
```

## Replay Artifacts

Add stage path:

```text
stages/mode_selection/000_ocs_single_provider_primary_mode_selection_recorded.json
```

Replay reconstruction must verify:

```text
mode_selection.provider_availability_artifact_hash == end_to_end.provider_availability_artifact_hash
mode_selection.multi_provider_result_bundle_hash == end_to_end.multi_provider_result_bundle_hash
mode_selection.successful_provider_count == end_to_end.successful_provider_count
mode_selection.selected_mode == end_to_end.selected_cognition_mode
mode_selection.comparison_required == end_to_end.comparison_required
```

Mode selection must be append-only and hash-verified.

## Fail-Closed Requirements

Fail closed before comparison when:

1. `successful_provider_count == 1` and no deterministic single-provider basis exists.
2. `successful_provider_count == 1` and any provider contract contradicts single-provider operation.
3. `successful_provider_count == 1` and caller explicitly requires true multi-provider comparison.
4. Mode-selection artifact hash does not verify.
5. Mode-selection replay does not match provider availability replay.
6. Any authority flag is elevated.

Failure classification:

```text
first_failed_stage = OCS_SINGLE_PROVIDER_PRIMARY_MODE_SELECTION
failure_reason = OCS single-provider mode selection failed closed: <reason>
comparison_attempted = False
comparison_performed = False
```

Zero successful providers must continue to fail closed at:

```text
OCS_PROVIDER_COGNITION_AVAILABILITY_GATE
```

## Acceptance Tests

Add focused tests for:

1. Conversational OCS one-provider path records mode-selection evidence.
2. One successful provider with `single_provider_only=True` selects `SINGLE_PROVIDER_PRIMARY`.
3. One successful provider with `single_provider_primary_mode=True` completes with:

```text
comparison_required = False
comparison_performed = False
selected_cognition_mode = SINGLE_PROVIDER_PRIMARY
```

4. Two successful providers select `MULTI_PROVIDER_COMPARISON` and execute standard comparison.
5. Two successes and one provider failure still select `MULTI_PROVIDER_COMPARISON`.
6. Zero successes still fail closed at provider availability gate and do not create comparison.
7. One success with no single-provider basis fails closed at mode selection before comparison.
8. Replay reconstruction includes and verifies mode-selection stage.
9. Tampered mode-selection replay fails closed.
10. Authority boundary flags remain false.

## Certification Tests

Certification should prove:

1. Real conversational OCS uses one provider contract marked `single_provider_only=True`.
2. Real conversational OCS selects `SINGLE_PROVIDER_PRIMARY`.
3. Standard comparison is not attempted in single-provider primary mode.
4. Single-provider primary result remains non-authoritative and human-review-bound.
5. Multi-provider comparison paths remain unchanged.
6. Provider availability fail-closed behavior remains unchanged.
7. Replay lineage includes:

```text
context
multi_provider_cognition
provider_cognition_availability
mode_selection
cognition_comparison or single-provider compatibility
continuity_and_clarification
```

8. No approval, worker invocation, execution request, dispatch request, governance mutation, or replay mutation is introduced.

## Migration Impact On Existing Multi-Provider Paths

Expected impact:

```text
multi-provider comparison semantics: unchanged
comparison runtime API: unchanged
provider availability gate: unchanged
conversation routing: unchanged
worker lifecycle: unchanged
authorization: unchanged
```

Replay shape changes by adding one deterministic stage:

```text
mode_selection
```

Existing tests that assert stage names must be updated to include the new stage. Existing multi-provider tests should continue to assert standard comparison behavior.

Existing single-provider tests should assert the mode-selection artifact rather than relying only on the `single_provider_primary_mode` boolean.

## Implementation Plan

1. Add constants and stage path for `OCS_SINGLE_PROVIDER_PRIMARY_MODE_SELECTION_ARTIFACT_V1`.
2. Implement deterministic mode-selection artifact creation.
3. Persist mode-selection artifact after provider availability.
4. Replace direct branch on `single_provider_primary_mode` with branch on `selected_mode`.
5. Add mode-selection hash fields to the end-to-end artifact.
6. Extend replay reconstruction and stage hash verification.
7. Add acceptance tests for one-provider, multi-provider, zero-provider, and ambiguous one-provider paths.
8. Add conversational certification test proving ACLI OCS records `SINGLE_PROVIDER_PRIMARY`.
9. Re-run OCS comparison, OCS end-to-end, conversational OCS binding, and HIRR-relevant conversational tests.

## Certification Readiness Statement

Current conversational OCS appears operational for one-provider primary mode because the CLI explicitly supplies:

```text
single_provider_primary_mode = True
```

and its provider contract is marked:

```text
single_provider_only = True
multi_provider_cognition_scope = False
```

However, certification should not rely on an implicit boolean. Certification should require replay-visible mode-selection evidence proving why single-provider primary mode was selected.

## Final Fields

```text
CURRENT_CONVERSATIONAL_ONE_PROVIDER_PATH_RECONSTRUCTED = YES
STANDARD_COMPARISON_SELECTION_CAUSE_IDENTIFIED = YES
DETERMINISTIC_MODE_SELECTION_RULES_DEFINED = YES
GOVERNANCE_ARCHITECTURE_PRESERVED = YES
FAIL_CLOSED_INVALID_STATES_DEFINED = YES
REPLAY_VISIBLE_MODE_SELECTION_DEFINED = YES
ACCEPTANCE_TESTS_DEFINED = YES
CERTIFICATION_TESTS_DEFINED = YES
MULTI_PROVIDER_MIGRATION_IMPACT_DEFINED = YES
OCS_SINGLE_PROVIDER_PRIMARY_MODE_CERTIFICATION_READY_FOR_IMPLEMENTATION = YES
```
