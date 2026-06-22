# HIRR_REAL_WORLD_GAPS_REMEDIATION_V1

Status: prepared and executable.

## Purpose

Remediate the gaps identified by `HIRR_REAL_WORLD_GAPS_FOUND` in
`AIGOL_HIRR_REAL_WORLD_DOGFOOD_CERTIFICATION_V2` and determine whether a
normal human can reliably enter the correct governed workflow using natural
language without knowledge of AiGOL internals.

## Governing Evidence

- `HIRR_REAL_WORLD_DOGFOOD_CERTIFICATION_V2`
- `FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED`
- `ACLI_LIVE_SESSION_REAL_WORKER_EXECUTION_CERTIFIED`
- `PROVIDER_GOVERNANCE_CERTIFIED`
- `PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFIED`

## Gap Classes

The failing/gap scenarios from the pre-remediation dogfood run were grouped
into these root-cause classes:

- bounded file/proof wording in Slovenian did not consistently route to the
  bounded file-write worker path;
- advisory and uncertainty follow-up phrasing did not always refine to
  proposal-only cognition;
- post-clarification cognition routing selected `OCS_LLM_COGNITION` without
  consistently invoking the cognition path;
- secret-like follow-up content did not always fail closed;
- live provider readiness evidence was not distinguished from local
  dependency fail-closed behavior during dogfood scoring.

## Remediation Scope

The remediation is intentionally minimal and deterministic:

- add focused natural-language signals for bounded proof-file requests;
- add focused advisory/uncertainty continuation signals;
- preserve clarification-first behavior before workflow selection;
- preserve fail-closed handling for unsafe or secret-like content;
- invoke proposal-only cognition after human-intent clarification resolves to
  `OCS_LLM_COGNITION`;
- preserve replay-visible evidence for local provider dependency fail-closed
  behavior while referencing the already-certified live cognition provider path.

## Preserved Boundaries

- Human approval remains required before execution.
- Worker governance remains unchanged.
- Provider output remains non-authoritative.
- Replay remains secret-free.
- Fail-closed behavior remains the default for unsafe or unresolved execution
  requests.

## Execution Runtime

The remediation evidence packager is:

```bash
python -m aigol.runtime.hirr_real_world_gaps_remediation_v1
```

It records:

- before/after comparison;
- coverage report;
- evidence package;
- replay package;
- certification report.

Runtime artifacts are written under:

```text
runtime/hirr_real_world_gaps_remediation_v1/CERT-XXXXXX/
```

## Certification Criteria

The final verdict is `HIRR_REAL_WORLD_READY` only if:

- the post-remediation HIRR V2 certification verdict is `HIRR_REAL_WORLD_READY`;
- aggregate score is `360/360`;
- all scenarios are certified;
- no remaining HIRR gaps are reported;
- approval boundaries, fail-closed behavior, replay visibility, and worker
  governance are preserved.

Otherwise the final verdict is:

```text
HIRR_REAL_WORLD_GAPS_FOUND
```
