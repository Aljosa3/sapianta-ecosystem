# RC_BATCH_03_STALE_LEXICAL_ASSERTIONS_IMPLEMENTATION_V1

## 1. Purpose

This artifact records implementation of `RC_BATCH_03_STALE_LEXICAL_ASSERTIONS_V1`.

The batch addressed stale lexical assertions that rejected safe diagnostic terminology or helper syntax instead of verifying the underlying governance invariant.

No runtime behavior, governance semantics, replay semantics, approval semantics, routing semantics, provider behavior, or workflow behavior was changed.

## 2. Root Cause Analysis

The remaining stale lexical assertion failures shared four root causes.

### 2.1 Lifecycle Vocabulary Misclassified As Autonomous Retry

Affected tests asserted that the literal word `retry` must not appear anywhere in CLI source.

Current Platform Core includes lifecycle command vocabulary and diagnostic evidence that may mention retry without introducing autonomous retry behavior.

The repaired assertions now verify the intended invariant:

- no attempt loops;
- no retry loops;
- no retry counter mutation;
- no sleep-based retry delay.

### 2.2 Diagnostic Capability Labels Misclassified As Hidden Runtime Behavior

Browser companion tests rejected words such as `serviceWorker` and `fallback` even when they appeared only as diagnostic labels or explicit negative evidence.

The repaired assertions now verify the intended invariant:

- no service worker registration is introduced;
- no navigator service worker path is introduced;
- no hidden endpoint or listener behavior is introduced;
- no fallback function path is introduced;
- no retry loop behavior is introduced.

### 2.3 Preview Boundary Evidence Misclassified As Provider Or Native Invocation

Preview tests rejected provider names and messaging labels even when they appeared inside non-execution preview boundaries or unrelated later functions.

The repaired assertions now verify the intended invariant:

- preview code does not invoke Native Messaging;
- preview code does not invoke Codex provider functions;
- preview code continues to display explicit non-dispatch evidence.

### 2.4 Generic JavaScript Mutator Ban Misclassified String Parsing

Replay session tests rejected every `.pop(` occurrence, including deterministic string parsing such as `split("-").pop()`.

The repaired assertions now verify the intended invariant:

- replay session arrays are append-only;
- replay session entries are not popped, shifted, spliced, unshifted, or reversed.

## 3. Files Changed

Regression tests updated:

- `tests/test_aigol_cli_foundation_v1.py`
- `tests/test_cli_controlled_execution_runtime_v1.py`
- `tests/test_canonical_bridge_result_artifact_export_import.py`
- `tests/test_chat_first_operator_flow.py`
- `tests/test_chatgpt_ingress_native_import_preview_v1.py`
- `tests/test_chatgpt_ingress_to_semantic_contract_preview_v1.py`
- `tests/test_governed_browser_companion_runtime.py`
- `tests/test_local_governed_transport_runtime_attachment.py`
- `tests/test_persistent_replay_session.py`

Governance record added:

- `docs/governance/RC_BATCH_03_STALE_LEXICAL_ASSERTIONS_IMPLEMENTATION_V1.md`

Validation side effects observed:

- `.runtime/aigol/evidence/...`
- `.runtime/aigol/ledger/governed_returns.jsonl`
- `runtime/decision_ledger.jsonl`

These side effects were produced by validation execution and were not required to implement RC_BATCH_03.

## 4. Implementation Rationale

The implementation replaces exact-string bans with semantic assertions that continue to enforce the certification intent.

Coverage was not weakened:

- hidden transport remains forbidden;
- provider invocation remains forbidden in preview paths;
- autonomous retry remains forbidden;
- hidden service worker registration remains forbidden;
- replay mutation remains forbidden;
- durable browser persistence remains forbidden.

The implementation is minimal and localized to tests whose failure category was stale lexical assertion.

## 5. Validation Results

### 5.1 Affected Regression Subset

Command:

```bash
python -m pytest tests/test_aigol_cli_foundation_v1.py::test_no_orchestration_introduced tests/test_cli_controlled_execution_runtime_v1.py::test_no_retries_introduced tests/test_canonical_bridge_result_artifact_export_import.py::test_sidepanel_import_is_operator_selected_only_without_endpoint_or_listener tests/test_chat_first_operator_flow.py::test_no_durable_persistence_or_endpoint_is_added tests/test_chatgpt_ingress_native_import_preview_v1.py::test_no_native_messaging_call_is_wired_to_preview_button tests/test_chatgpt_ingress_to_semantic_contract_preview_v1.py::test_preview_path_never_invokes_codex_provider tests/test_governed_browser_companion_runtime.py::test_no_retry_fallback_or_hidden_automation_surface_exists tests/test_local_governed_transport_runtime_attachment.py::test_no_endpoint_provider_execution_or_orchestration_behavior_is_added tests/test_persistent_replay_session.py::test_replay_session_is_bounded_in_memory_and_append_only -q --tb=short
```

Result:

```text
9 passed in 0.20s
```

### 5.2 Affected File Regression Set

Command:

```bash
python -m pytest tests/test_aigol_cli_foundation_v1.py tests/test_cli_controlled_execution_runtime_v1.py tests/test_canonical_bridge_result_artifact_export_import.py tests/test_chat_first_operator_flow.py tests/test_chatgpt_ingress_native_import_preview_v1.py tests/test_chatgpt_ingress_to_semantic_contract_preview_v1.py tests/test_governed_browser_companion_runtime.py tests/test_local_governed_transport_runtime_attachment.py tests/test_persistent_replay_session.py -q --tb=short
```

Result:

```text
115 passed in 0.50s
```

### 5.3 Full Pytest Suite

Command:

```bash
python -m pytest -q --tb=no -rf
```

Result:

```text
63 failed, 5525 passed, 2 skipped in 121.38s
```

Previous RC_BATCH_02 baseline:

```text
72 failed, 5516 passed, 2 skipped
```

RC_BATCH_03 reduced the full-suite failure count by nine failures.

## 6. Remaining Failure Categories

The remaining 63 full-suite failures are outside the stale lexical assertion batch.

Observed remaining categories:

- conversation and local preview runtime failures;
- governed provider activation failures;
- `sapianta-domain-trading` domain governance artifact failures.

These failures remain assigned to later RC batches or non-core/out-of-scope classifications from the Release Triage Program.

## 7. Certification Impact

RC_BATCH_03 does not alter Platform Core behavior.

Certification impact:

- stale lexical assertion blockers are removed;
- certification intent is preserved;
- governance guarantees are preserved;
- replay determinism is preserved;
- fail-closed behavior is preserved;
- evidence and certification artifacts remain semantically unchanged.

The remaining full-suite failures do not originate from this batch and require separate RC batch handling.

## 8. Final Verdict

`RC_BATCH_03_STALE_LEXICAL_ASSERTIONS_IMPLEMENTATION_READY`

