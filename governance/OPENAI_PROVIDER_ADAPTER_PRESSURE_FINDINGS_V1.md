# OpenAI Provider Adapter Pressure Findings V1

Status: pressure findings evidence.

## Finding 1: Shared Escalation Vocabulary Gap

Severity: `MEDIUM`

Classification: `REMEDIATED`

Pressure case:

```text
OpenAI response requests governance override, worker action, or replay mutation.
```

Observed behavior before hardening:

- direct execution and authorization escalation terms failed closed
- governance/replay/worker wording was not fully covered by the shared forbidden response vocabulary

Remediation:

- added `governance`, `worker`, and `replay` to `FORBIDDEN_RESPONSE_TERMS` in `aigol/runtime/external_llm_response_attachment.py`

Result:

- governance, worker, and replay authority requests now fail closed through the existing shared proposal-ingestion boundary

## Finding 2: Top-Level Failure Reason Is Not Always Duplicated

Severity: `LOW`

Classification: `ACCEPTED`

In downstream provider identity failures, the OpenAI adapter top-level result reports `FAILED`, while the detailed failure reason remains visible in the nested `REAL_PROVIDER_ATTACHMENT_V1` replay capture.

This is acceptable because:

- the failure is replay-visible
- nested replay remains reconstructable
- no silent recovery occurs
- the OpenAI top-level result still terminates as `FAILED`

No runtime expansion was introduced to duplicate nested failure reasons.

## No Authority Findings

No evidence showed OpenAI obtaining:

- execution authority
- authorization authority
- governance authority
- replay authority
- worker authority

## No Replay Bypass Findings

Replay remained append-only, ordered, hash-verified, nested, and reconstructable across success, failure, corruption, and repeated-run pressure cases.

