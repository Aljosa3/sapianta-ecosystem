# AIGOL_PROVIDER_CREDENTIAL_VAULT_ONBOARDING_CERTIFICATION_V1

Status: EXECUTED

Date: 2026-06-21

Governing inputs:

- AIGOL_PROVIDER_CREDENTIAL_VAULT_V1
- AIGOL_PROVIDER_GOVERNANCE_RUNTIME_V1
- AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1
- AIGOL_OPERATOR_ENVIRONMENT_BOOTSTRAP_V1
- CERT-000009
- Provider Governance Certification V1

## 1. Purpose

Determine whether the Provider Credential Vault is currently the actual source of truth for live OpenAI cognition-provider execution, or whether AiGOL remains dependent on the temporary environment-variable fallback path.

## 2. Executable Certification

Runtime:

```text
aigol/runtime/provider_credential_vault_onboarding_certification_v1.py
```

Command:

```bash
python -m aigol.runtime.provider_credential_vault_onboarding_certification_v1
```

## 3. Executed Evidence

Certification root:

```text
runtime/provider_credential_vault_onboarding_certification_v1/CERT-000001/
```

Evidence package:

```text
runtime/provider_credential_vault_onboarding_certification_v1/CERT-000001/evidence_package/000_provider_credential_vault_onboarding_evidence_package.json
```

Replay package:

```text
runtime/provider_credential_vault_onboarding_certification_v1/CERT-000001/replay_package/000_provider_credential_vault_onboarding_replay_package.json
```

Coverage report:

```text
runtime/provider_credential_vault_onboarding_certification_v1/CERT-000001/coverage_report/000_provider_credential_vault_onboarding_coverage_report.json
```

Certification report:

```text
runtime/provider_credential_vault_onboarding_certification_v1/CERT-000001/certification_report/000_provider_credential_vault_onboarding_certification_report.json
```

## 4. Scenario Results

### Scenario 1: Empty Operator Config

Observed:

```text
provider_credentials_json_exists = false
credential_present = false
credential_enabled = false
```

Expected behavior was observed.

### Scenario 2: Onboard OpenAI Credential

Observed:

```text
onboarding_method = runtime_api
provider_credentials_json_created = true
vault_file_mode = 0o600
```

The vault file is created by:

```text
aigol.runtime.provider_credential_vault.add_provider_credential
```

No ACLI onboarding command is currently registered.

### Scenario 3: Vault Credential Lookup

Observed:

```text
credential_source = vault://provider/openai
credential_reference = vault://provider/openai
credential_value_recorded = false
credential_hash_recorded = false
```

Vault lookup works at the vault runtime boundary.

### Scenario 4: Vault-Only ProviderConfig Lookup

Observed:

```text
OPENAI_API_KEY removed = true
AIGOL_OPENAI_API_KEY removed = true
provider_config_resolved_from_vault = true
credential_source = vault://provider/openai
```

The simple provider configuration path can resolve OpenAI credentials from the vault without provider environment variables.

### Scenario 5: First Live Cognition Certification Vault-Only

Observed:

```text
OPENAI_API_KEY removed = true
AIGOL_OPENAI_API_KEY removed = true
aborted_before_certification = true
failure_reason = AIGOL_OPENAI_API_KEY_MISSING
provider_invoked = false
provider_response_received = false
credential_source = env:AIGOL_OPENAI_API_KEY
```

The first-live cognition certification path remains environment-bound.

### Scenario 6: Replay Secret Safety

Observed:

```text
replay_secret_free = true
```

### Scenario 7: Approval Boundary

Observed:

```text
ROTATE without approval failed closed
approval_boundaries_preserved = true
```

## 5. Answers

### 1. How does an operator onboard a new OpenAI credential?

Current implemented path:

```text
aigol.runtime.provider_credential_vault.add_provider_credential(provider_id="openai", ...)
```

There is no operator-facing ACLI onboarding command yet.

### 2. Which ACLI command performs onboarding?

Defined target command:

```bash
python -m aigol.cli.aigol_cli provider credential add openai
```

Current status:

```text
NOT IMPLEMENTED
```

Parser evidence:

```text
aigol provider: invalid choice: 'credential' (choose from 'invoke', 'governance')
```

### 3. When is provider-credentials.json created?

It is created when the vault runtime writes the first provider record through `add_provider_credential`.

It is not created automatically by operator bootstrap or first-live certification.

### 4. What is the canonical vault initialization workflow?

Current implemented workflow:

```text
runtime API add_provider_credential
→ local vault file creation
→ chmod 0600
→ secret-free vault event replay
→ verify_provider_credential
```

Required future workflow:

```text
ACLI provider credential add <provider>
→ secret input boundary
→ vault add
→ verification
→ replay-safe evidence
```

### 5. What is the canonical credential storage format?

Secret-bearing local JSON file outside the repository:

```text
$HOME/.config/aigol/provider-credentials.json
```

Required permission:

```text
0600
```

Replay and governance artifacts record only secret-free diagnostics.

### 6. How does the operator verify successful onboarding?

Current implemented path:

```text
provider_credential_diagnostic(provider_id="openai")
```

Target ACLI command:

```bash
python -m aigol.cli.aigol_cli provider credential verify openai
```

Current ACLI status:

```text
NOT IMPLEMENTED
```

### 7. How verify vault://provider/openai instead of env?

Replay evidence from Scenario 3:

```text
credential_source = vault://provider/openai
credential_reference = vault://provider/openai
```

### 8. Can vault function when provider environment variables are removed?

Yes, at the vault runtime and `ProviderConfig` layer.

### 9. Can OpenAI certification succeed using only the vault?

No.

### 10. Can OpenAI certification succeed after unsetting OPENAI_API_KEY and AIGOL_OPENAI_API_KEY?

No. It aborts before certification with:

```text
AIGOL_OPENAI_API_KEY_MISSING
```

### 11. What replay-visible evidence proves credential source?

Scenario 3 records:

```text
credential_source = vault://provider/openai
retrieval_artifact_hash = sha256:1a5f5acc84163abe2c167e761754b687e4d248d4a4c72186b6c26c78dcdc6a87
```

Scenario 5 records:

```text
credential_source = env:AIGOL_OPENAI_API_KEY
```

### 12. Is provider-credentials.json created automatically or manually?

Not automatically by current operator bootstrap or first-live certification.

It is created programmatically by the vault runtime when `add_provider_credential` is called.

### 13. If automatically, which ACLI command creates it?

No ACLI command currently creates it.

### 14. If manually, document exact onboarding procedure.

Current non-ACLI procedure:

```text
Call aigol.runtime.provider_credential_vault.add_provider_credential
with provider_id="openai", credential_value=<secret>, and vault_path=$HOME/.config/aigol/provider-credentials.json.
```

This must be replaced by an ACLI secret-input command before declaring the vault fully operational for operators.

## 6. Gap Analysis

Confirmed gaps:

1. ACLI provider credential onboarding command is not implemented.
2. First live cognition certification still requires environment credential preflight.
3. First live cognition certification does not record `vault://provider/openai` as credential source.

## 7. Migration Status

```text
VAULT_RUNTIME_WORKS_BUT_FIRST_LIVE_CERTIFICATION_REMAINS_ENV_BOUND
```

## 8. Final Verdict

```text
PROVIDER_CREDENTIAL_VAULT_FALLBACK_DEPENDENT
```
