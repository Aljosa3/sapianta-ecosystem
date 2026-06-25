# ACLI_HARDENING_INTEGRATION_RUNTIME_V1

Status: READY

Target verdict:

```text
ACLI_HARDENING_INTEGRATION_RUNTIME_READY
```

## 1. Runtime Purpose

`ACLI_HARDENING_INTEGRATION_RUNTIME_V1` integrates `ACLI_HARDENING_RUNTIME_V1` into the live ACLI interaction lifecycle.

The integration converts normal completed ACLI turns into Platform Core Generation 1 hardening evidence without requiring the operator to run separate test scenarios.

Normal flow:

```text
Human
-> ACLI
-> Replay
-> Hardening Runtime
-> Replay Evidence
-> Conversation Ends
```

The integration is observational only.

## 2. Integration Boundary

The integration point is immediately after successful interactive ACLI turn completion evidence is recorded.

The runtime receives:

- session identifier;
- turn identifier;
- prompt identifier;
- completed turn summary;
- turn completion replay capture;
- session replay root;
- turn replay root;
- creation timestamp.

The runtime does not run before workflow selection, approval, execution, validation, or replay capture.

## 3. Automatic Hardening Capture

Every successful completed ACLI turn now records a hardening event.

Captured evidence includes:

- replay reference;
- workflow;
- routing decision;
- exercised runtime components;
- exercised contracts;
- exercised architectural invariants;
- exercised translation path;
- exercised approval path;
- exercised replay path;
- exercised provider path;
- exercised worker path;
- completion status.

The capture is best-effort and non-authoritative. A hardening failure is contained and must not invalidate an already completed ACLI workflow turn.

## 4. Replay Integration

Each hardening event creates replay-visible hardening evidence under the completed turn replay root:

```text
TURN-xxxxxx/acli_hardening/
TURN-xxxxxx/acli_hardening_integration/
```

Replay reconstruction verifies:

- hardening artifact type;
- wrapper replay hash;
- hardening artifact hash;
- authority flags;
- scenario classification;
- source replay reference;
- production metrics input.

Hardening replay explains:

- why the hardening event was created;
- which workflow produced it;
- which replay lineage it belongs to;
- which Platform Core components were exercised.

## 5. Persistent Metrics

The integration persists session-level hardening metrics across ACLI sessions:

```text
<session-root>/acli_hardening_metrics/latest_metrics.json
```

Immutable per-interaction metrics snapshots are also recorded in the metrics directory.

Persisted metrics include:

- Platform Core Hardening Progress;
- Scenario Coverage;
- Workflow Coverage;
- Contract Coverage;
- Translation Coverage;
- Replay Coverage;
- Approval Coverage;
- Provider Coverage;
- Worker Coverage;
- Regression Coverage.

No production readiness decision is made by this integration. Metrics are evidence only.

## 6. Operator Summary

After successful completion, ACLI may display a compact non-interrupting hardening summary:

```text
Hardening

Scenario: <scenario>
Coverage: <delta>
Replay: Recorded
Operator feedback: Optional
```

The summary does not request mandatory input and does not block the workflow.

## 7. Governance Boundaries

The integration shall never:

- approve;
- reject;
- execute;
- reroute;
- invoke workers;
- invoke providers;
- change source workflow replay;
- modify governance;
- modify Platform Core;
- change deterministic rules;
- produce improvement proposals.

Authority flags remain false for:

- execution authorization;
- dispatch authorization;
- worker invocation;
- provider invocation;
- governance mutation;
- replay mutation;
- lifecycle modification;
- approval creation;
- improvement proposal creation.

## 8. Future Compatibility

Hardening evidence includes metadata prepared for future:

- `PLATFORM_QUALITY_RUNTIME_V1`;
- `PLATFORM_IMPROVEMENT_RUNTIME_V1`.

This integration does not implement either future runtime.

Future runtimes may consume hardening evidence, but they must preserve:

- human authority;
- replay as source of truth;
- fail-closed behavior;
- approval boundaries;
- provider non-authority;
- worker boundary protections.

## 9. Implemented Files

Runtime:

```text
aigol/runtime/acli_hardening_integration_runtime.py
```

CLI integration:

```text
aigol/cli/aigol_cli.py
```

Tests:

```text
tests/test_acli_hardening_integration_runtime_v1.py
tests/test_acli_hardening_runtime_v1.py
tests/test_interactive_conversation_cli_v1.py
```

## 10. Validation Evidence

Validation commands:

```text
python -m pytest tests/test_acli_hardening_runtime_v1.py tests/test_acli_hardening_integration_runtime_v1.py -q
python -m pytest tests/test_interactive_conversation_cli_v1.py -q
python -m py_compile aigol/runtime/acli_hardening_runtime.py aigol/runtime/acli_hardening_integration_runtime.py aigol/cli/aigol_cli.py tests/test_acli_hardening_runtime_v1.py tests/test_acli_hardening_integration_runtime_v1.py
git diff --check
```

Verified:

- completed ACLI turns automatically create hardening events;
- replay lineage is preserved;
- hardening evidence reconstructs;
- hardening metrics persist across ACLI restart;
- hardening does not create approval, execution, provider, or worker authority;
- existing ACLI turn completion behavior remains intact with the added non-interrupting hardening summary.

## 11. Final Verdict

`ACLI_HARDENING_INTEGRATION_RUNTIME_V1` is ready as the passive live integration layer that turns normal ACLI usage into replay-governed hardening evidence.

Final verdict:

```text
ACLI_HARDENING_INTEGRATION_RUNTIME_READY
```
