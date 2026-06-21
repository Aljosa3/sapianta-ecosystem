# AIGOL_PROVIDER_ACLI_CONNECTIVITY_AUDIT_V1

Status: EXECUTED

Date: 2026-06-21

Governing inputs:

- AIGOL_PROVIDER_GOVERNANCE_RUNTIME_V1
- AIGOL_PROVIDER_CREDENTIAL_VAULT_V1
- AIGOL_PROVIDER_CREDENTIAL_VAULT_ONBOARDING_CERTIFICATION_V1
- Provider Governance Certification V1
- Provider Credential Vault Certification V1
- ACLI command parser

## 1. Purpose

Audit every provider-related runtime capability and determine whether it is reachable from ACLI.

The audit distinguishes:

- implemented runtime capability;
- argparse/ACLI command registration;
- operator usability;
- certification status;
- first-live certification vault migration readiness.

## 2. Executed Audit

Runtime:

```text
aigol/runtime/provider_acli_connectivity_audit_v1.py
```

Command:

```bash
python -m aigol.runtime.provider_acli_connectivity_audit_v1
```

Certification root:

```text
runtime/provider_acli_connectivity_audit_v1/CERT-000001/
```

Artifacts:

```text
runtime/provider_acli_connectivity_audit_v1/CERT-000001/coverage_report/000_provider_acli_connectivity_coverage_report.json
runtime/provider_acli_connectivity_audit_v1/CERT-000001/evidence_package/000_provider_acli_connectivity_evidence_package.json
runtime/provider_acli_connectivity_audit_v1/CERT-000001/replay_package/000_provider_acli_connectivity_replay_package.json
runtime/provider_acli_connectivity_audit_v1/CERT-000001/audit_report/000_provider_acli_connectivity_audit_report.json
```

## 3. Capability Inventory

Provider governance capabilities:

- provider status
- provider credentials
- provider usage
- provider failures
- provider costs
- provider participation

Credential vault capabilities:

- provider credential add
- provider credential verify
- provider credential rotate
- provider credential disable
- provider credential delete
- provider credential history

Natural operator phrases probed:

- show provider credentials
- show provider credential history

## 4. Reachability Summary

Reachable:

| Runtime Capability | ACLI Reachable | Routing Path | Certified | Operator Usable |
| --- | --- | --- | --- | --- |
| provider status | yes | `provider governance status` | yes | yes |
| provider credentials | yes | `provider governance credentials` | yes | yes |
| provider usage | yes | `provider governance usage` | yes | yes |
| provider failures | yes | `provider governance failures` | yes | yes |
| provider costs | yes | `provider governance costs` | yes | yes |
| provider participation | yes | `provider governance participation` | yes | yes |

Unreachable:

| Runtime Capability | ACLI Reachable | Routing Path | Certified | Operator Usable |
| --- | --- | --- | --- | --- |
| provider credential add | no | none | yes | no |
| provider credential verify | no | none | yes | no |
| provider credential rotate | no | none | yes | no |
| provider credential disable | no | none | yes | no |
| provider credential delete | no | none | yes | no |
| provider credential history | no | none | no | no |
| show provider credentials | no | none | no | no |
| show provider credential history | no | none | no | no |

## 5. Missing ACLI Registrations

Missing command registrations:

```text
provider credential add openai
provider credential verify openai
provider credential rotate openai
provider credential disable openai
provider credential delete openai
provider credential history openai
show provider credentials
show provider credential history
```

## 6. Dead-End Certified Runtimes

Certified runtime capabilities with no ACLI route:

```text
provider credential add
provider credential verify
provider credential rotate
provider credential disable
provider credential delete
```

These are dead-end certified runtimes from an operator perspective.

## 7. First-Live Vault Migration

Observed:

```text
vault_migration_ready = false
credential_source = env:AIGOL_OPENAI_API_KEY
provider_invoked = false
provider_response_received = false
failure_reason = AIGOL_OPENAI_API_KEY_MISSING
```

Conclusion:

The first-live cognition provider certification cannot yet be considered vault-backed.

## 8. Remediation Plan

Priority order:

1. Preserve `provider governance status` and add natural phrase alias if required.
2. Preserve `provider governance credentials` and add natural phrase alias if required.
3. Preserve `provider governance usage` and add natural phrase alias if required.
4. Preserve `provider governance failures` and add natural phrase alias if required.
5. Preserve `provider governance participation` and add natural phrase alias if required.
6. Register `provider credential add <provider>` and bind to vault onboarding runtime.
7. Register `provider credential verify <provider>` and bind to vault verification runtime.
8. Register `provider credential rotate <provider>` with approval enforcement.
9. Register `provider credential disable <provider>` with approval enforcement.
10. Register `provider credential delete <provider>` with approval enforcement.
11. Migrate first-live credential preflight and live boundary credential retrieval to vault-backed lookup while preserving env fallback only as compatibility.

## 9. Final Verdict

```text
PROVIDER_ACLI_CONNECTIVITY_GAPS_FOUND
```
