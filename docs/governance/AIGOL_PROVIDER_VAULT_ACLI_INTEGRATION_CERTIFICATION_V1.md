# AIGOL_PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFICATION_V1

Status: CERTIFIED

Final verdict: PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFIED

## Purpose

Certify that Provider Credential Vault lifecycle operations are reachable from ACLI, update the vault deterministically, preserve approval boundaries, remain replay-safe, and support vault-backed first-live cognition provider execution without environment-variable fallback.

## Governing Inputs

- AIGOL_PROVIDER_CREDENTIAL_VAULT_V1
- AIGOL_PROVIDER_GOVERNANCE_RUNTIME_V1
- Provider Credential Registry V1
- Operator Environment Bootstrap V1
- Provider Governance Certification V1
- FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED

## ACLI Commands Certified

The following deterministic ACLI command routes are implemented:

```bash
aigol provider credential add <provider>
aigol provider credential verify <provider>
aigol provider credential rotate <provider>
aigol provider credential disable <provider>
aigol provider credential delete <provider>
aigol provider credential history <provider>
```

The command surface also supports:

```bash
aigol provider credential status <provider>
```

Credential values are supplied through the operator process environment using `AIGOL_PROVIDER_CREDENTIAL_INPUT`. The value is consumed by the vault runtime and is not written to replay, governance artifacts, certification reports, or git-tracked files.

## Approval Boundaries

Human approval is enforced for:

- ROTATE
- DISABLE
- DELETE
- REPLACE

Certification verified fail-closed behavior when approval was omitted for ROTATE, DISABLE, and DELETE.

## Vault Source

Canonical provider credential reference:

```text
vault://provider/openai
```

Default operator vault path:

```text
$HOME/.config/aigol/provider-credentials.json
```

Certification used a temporary operator-safe vault path under `/tmp` to avoid writing test credentials to the operator home vault.

## Evidence

Certification root:

```text
runtime/provider_vault_acli_integration_certification_v1/CERT-000003/
```

Evidence package:

```text
runtime/provider_vault_acli_integration_certification_v1/CERT-000003/evidence_package/000_provider_vault_acli_integration_evidence_package.json
```

Coverage report:

```text
runtime/provider_vault_acli_integration_certification_v1/CERT-000003/evidence_package/001_provider_vault_acli_integration_coverage_report.json
```

Replay package:

```text
runtime/provider_vault_acli_integration_certification_v1/CERT-000003/replay_package/000_provider_vault_acli_integration_replay_package.json
```

Certification report:

```text
runtime/provider_vault_acli_integration_certification_v1/CERT-000003/certification_report/000_provider_vault_acli_integration_certification_report.json
```

## Certified Observations

- ACLI lifecycle commands routed deterministically.
- Vault lifecycle operations updated provider credential state.
- Operator-safe display identifiers were produced.
- Approval-required lifecycle operations failed closed without approval.
- Replay artifacts remained secret-free.
- A vault credential file was created.
- First-live cognition provider certification ran with OpenAI environment variables removed.
- First-live credential source was replay-visible as `vault://provider/openai`.
- Environment fallback was not required for the certified vault-backed execution.

## Migration Status

First-live certification now supports explicit vault-backed execution through the provider credential vault. The historical environment-variable path remains temporarily available for backward compatibility and previously certified evidence continuity.

## Certification Criteria

Certification passes only when all of the following are true:

- Required provider credential ACLI commands are reachable.
- Vault file creation is observed.
- Credential source resolves to `vault://provider/openai`.
- First-live provider execution succeeds with OpenAI environment variables removed.
- Provider response is received.
- Human confirmation is recorded.
- Replay reconstruction succeeds.
- No credential value, credential hash, or authorization header appears in replay-visible evidence.
- Approval boundaries fail closed for protected lifecycle operations.

## Final Verdict

PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFIED
