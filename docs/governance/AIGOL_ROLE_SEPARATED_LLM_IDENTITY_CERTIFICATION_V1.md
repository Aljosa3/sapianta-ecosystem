# AIGOL_ROLE_SEPARATED_LLM_IDENTITY_CERTIFICATION_V1

Status: prepared for executable certification.

## Goal

Certify that the same external LLM provider can participate in multiple strictly separated architectural roles without receiving authority and without collapsing governance, metrics, lifecycle, or replay evidence into a single ambiguous identity.

## Certified Role Identities

- `vault://provider/openai-cognition`
- `vault://worker/openai-translation`
- `vault://worker/openai-repair`

Each identity is treated as a separate governed identity even though the external provider family is `openai`.

## Certification Scope

The certification verifies:

- independent credential identity artifacts;
- independent lifecycle records;
- independent usage metrics;
- independent cost hooks;
- independent participation records;
- independent enable/disable controls;
- replay-visible distinction between cognition provider, translation worker, and repair worker;
- preservation of human authority and governance authority;
- no transfer of authority to an LLM identity.

## Replay Artifacts

The runtime produces:

- `ROLE_SEPARATED_LLM_CREDENTIAL_IDENTITY_ARTIFACT_V1`
- `ROLE_SEPARATED_LLM_LIFECYCLE_ARTIFACT_V1`
- `ROLE_SEPARATED_LLM_USAGE_METRIC_ARTIFACT_V1`
- `ROLE_SEPARATED_LLM_PARTICIPATION_ARTIFACT_V1`
- `ROLE_SEPARATED_LLM_AUTHORITY_BOUNDARY_ARTIFACT_V1`

Secret values, credential contents, credential hashes, and authorization headers are never recorded.

## Certification Output

Artifacts are written under:

```text
runtime/role_separated_llm_identity_certification_v1/
  CERT-XXXXXX/
    coverage_report/
    evidence_package/
    replay_package/
    certification_report/
```

## Success Criteria

The final verdict is `ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED` only when all assertions pass:

- role-separated credential identities created;
- credential references are unique;
- same external provider is shared safely across roles;
- lifecycle, metrics, costs, participation, and enable/disable controls remain independent;
- replay distinguishes all three roles;
- governance treats each role as a distinct identity;
- no authority transfer occurs;
- replay reconstructs;
- evidence remains secret-free.

## Final Verdict

Executable runtime determines:

- `ROLE_SEPARATED_LLM_IDENTITY_CERTIFIED`
- `ROLE_SEPARATED_LLM_IDENTITY_GAPS_FOUND`
