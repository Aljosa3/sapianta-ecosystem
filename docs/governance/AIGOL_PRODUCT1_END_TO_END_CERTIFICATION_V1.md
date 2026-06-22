# AIGOL_PRODUCT1_END_TO_END_CERTIFICATION_V1

Status: prepared and executable.

## Goal

Perform the first complete Product 1 end-to-end certification.

The certified path is:

```text
Human
-> Natural Language Prompt
-> ACLI
-> HIRR
-> Cognition
-> Clarification if required
-> Execution Summary
-> Human Approval
-> Authorization
-> Worker
-> Side Effect
-> Verification
-> Replay
-> Audit Review
```

## Governing Evidence

- `HIRR_REAL_WORLD_READY`
- `CERT-000009`
- `PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFIED`
- `ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_CERTIFIED`
- `PROVIDER_GOVERNANCE_CERTIFIED`
- replay infrastructure

## Representative Scenarios

| Scenario | Coverage | Expected Evidence |
| --- | --- | --- |
| P1-E2E-001 | Direct execution | Normal prompt reaches approved worker side effect and verification. |
| P1-E2E-002 | Clarification path | Ambiguous prompt is clarified before worker execution. |
| P1-E2E-003 | Cognition path | Proposal-only cognition uses the certified live OpenAI path and invokes no worker. |
| P1-E2E-004 | Approval path | Human approval produces authorization and governed worker handoff. |
| P1-E2E-005 | Rejection path | Human rejection blocks authorization and side effect. |
| P1-E2E-006 | Fail-closed path | Invalid worker target fails closed without side effect. |

## Runtime

Run:

```bash
python -m aigol.runtime.product1_end_to_end_certification_v1
```

Artifacts are written under:

```text
runtime/product1_end_to_end_certification_v1/CERT-XXXXXX/
```

Required outputs:

- coverage report;
- evidence package;
- replay package;
- audit review;
- certification report.

## Pass Criteria

The certification verdict is `AIGOL_PRODUCT1_END_TO_END_CERTIFIED` only if:

- HIRR real-world readiness is certified;
- live cognition provider path is certified;
- provider governance is certified;
- provider vault ACLI integration is certified;
- ACLI live-session real worker execution is certified;
- all representative Product 1 scenarios certify;
- governance boundaries are preserved;
- authorization is enforced;
- worker side effects are verified;
- cognition continuity is observed;
- replay reconstruction succeeds;
- audit review can reconstruct the evidence chain.

Otherwise the verdict is:

```text
AIGOL_PRODUCT1_END_TO_END_GAPS_FOUND
```
