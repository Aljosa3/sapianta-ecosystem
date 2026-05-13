# Repo-Wide Collection Stabilization Acceptance Evidence v1

## Milestone

`FINALIZE_REPO_WIDE_TEST_COLLECTION_STABILIZATION_V1`

## Collection Evidence

Command:

```bash
python -m pytest --collect-only
```

Result:

- Status: `PASSED`
- Collected tests: `398`
- Explicit optional skips: `1`
- Collection crashes: `0`

## Focused Governance Bridge Suite

Command:

```bash
pytest tests/test_protocol_validator.py tests/test_lifecycle.py tests/test_hashing.py tests/test_lineage.py tests/test_enforcement.py tests/test_cli_validation.py tests/test_quarantine.py tests/test_bridge_listener.py tests/test_codex_runner.py tests/test_task_queue.py tests/test_task_lock.py tests/test_replay_log.py tests/test_runtime_status.py tests/test_replay_reader.py tests/test_execution_summary.py tests/test_state_transitions.py tests/test_queue_inspector.py tests/test_observability_cli.py tests/test_advisory_proposals.py tests/test_capability_delta.py tests/test_governance_risk.py tests/test_reflection_cli.py tests/test_reflection_engine.py tests/test_reflection_reader.py tests/test_approval_cli.py tests/test_approval_queue.py tests/test_approval_reader.py tests/test_approval_storage.py tests/test_governance_decisions.py tests/test_policy_cli.py tests/test_policy_engine.py tests/test_policy_rules.py tests/test_admissibility.py tests/test_escalation.py tests/test_policy_evidence.py tests/test_policy_reader.py
```

Result: `108 passed`

## Stabilization Suite

Command:

```bash
python -m pytest tests/test_collection_audit.py tests/test_optional_dependency_policy.py tests/test_stale_artifact_guard.py tests/test_entropy_observability.py
```

Result: `10 passed`

## Static Validation

- `python -m py_compile` over `sapianta_bridge` Python modules: `PASSED`
- `git diff --check`: `PASSED`
- `git -C sapianta_system diff --check`: `PASSED`

## Execution Failure Classification

Full repo execution remains separate from collection certification.

Command:

```bash
python -m pytest
```

Result:

- Passed: `347`
- Failed: `51`
- Skipped: `1`
- Status: `TEST_EXECUTION_FAILURES_PRESENT`

The remaining failures are execution-time domain governance artifact failures in `sapianta-domain-trading`, primarily missing finalization manifests/evidence files and manifest/document hash mismatches.

These failures are not hidden, not skipped, and not reclassified as collection stabilization failures.

## Certification Claim

This evidence certifies deterministic repo-wide pytest collection integrity only.

It does not certify repo-wide execution correctness.
