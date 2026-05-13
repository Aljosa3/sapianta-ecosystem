# Collection Stabilization Summary

## Status

`REPO_WIDE_TEST_COLLECTION_STABILIZATION_V1` restored deterministic root pytest collection.

Validation command:

```bash
python -m pytest --collect-only
```

Result:

- Collection status: `PASSED`
- Collected tests: `398`
- Explicit optional skips: `1`
- Collection crashes: `0`

## Fixes Applied

- Added root `pytest.ini` with explicit collection surfaces:
  - `tests`
  - `sapianta-domain-credit/tests`
  - `sapianta-domain-trading/tests`
- Added explicit `pythonpath` entries for root, `sapianta_system`, credit domain, and trading domain packages.
- Added targeted root `conftest.py` collection ignores for generated and quarantine runtime artifact roots.
- Added root runtime package markers:
  - `runtime/__init__.py`
  - `runtime/governance/__init__.py`
- Added a source-specific optional guard for the legacy credit constitutional flow requiring the old `sapianta_core` proposal API.

## What Was Not Done

- No governance behavior was changed.
- No bridge protocol, enforcement, transport, observability, reflection, approval, or policy semantics were changed.
- No meaningful tests were deleted.
- No broad unconditional skip was added.
- No generated artifact was deleted automatically.

## Validation

Focused bridge governance suite:

```bash
pytest tests/test_protocol_validator.py tests/test_lifecycle.py tests/test_hashing.py tests/test_lineage.py tests/test_enforcement.py tests/test_cli_validation.py tests/test_quarantine.py tests/test_bridge_listener.py tests/test_codex_runner.py tests/test_task_queue.py tests/test_task_lock.py tests/test_replay_log.py tests/test_runtime_status.py tests/test_replay_reader.py tests/test_execution_summary.py tests/test_state_transitions.py tests/test_queue_inspector.py tests/test_observability_cli.py tests/test_advisory_proposals.py tests/test_capability_delta.py tests/test_governance_risk.py tests/test_reflection_cli.py tests/test_reflection_engine.py tests/test_reflection_reader.py tests/test_approval_cli.py tests/test_approval_queue.py tests/test_approval_reader.py tests/test_approval_storage.py tests/test_governance_decisions.py tests/test_policy_cli.py tests/test_policy_engine.py tests/test_policy_rules.py tests/test_admissibility.py tests/test_escalation.py tests/test_policy_evidence.py tests/test_policy_reader.py
```

Result: `108 passed`.

Repository-wide execution check:

```bash
python -m pytest
```

Result: `347 passed, 51 failed, 1 skipped`.

These are `TEST_EXECUTION_FAILURES`, not collection failures. The remaining failures are in the `sapianta-domain-trading` governance artifact surface, primarily missing domain finalization manifests/evidence files and manifest/document hash mismatches. No pytest collection crash remained.

Additional validation:

- `python -m py_compile` over `sapianta_bridge` Python modules: `passed`
- `git diff --check`: `passed`
- `git -C sapianta_system diff --check`: `passed`

## Passive Entropy Observability

Passive baseline evidence was recorded in `EXECUTION_ENTROPY_BASELINE.json`.

This observability is non-authoritative and does not affect execution, governance decisions, prompt behavior, provider routing, or orchestration.
