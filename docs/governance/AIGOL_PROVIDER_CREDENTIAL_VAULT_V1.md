# AIGOL_PROVIDER_CREDENTIAL_VAULT_V1

Status: DEFINED

Date: 2026-06-21

Governing inputs:

- FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED / CERT-000009
- PROVIDER_GOVERNANCE_RUNTIME_IMPLEMENTED
- PROVIDER_GOVERNANCE_CERTIFIED
- AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1
- AIGOL_OPERATOR_ENVIRONMENT_BOOTSTRAP_V1
- Provider lifecycle governance
- Cognition participation observability
- Replay architecture
- Human approval boundary

Final verdict:

```text
PROVIDER_CREDENTIAL_VAULT_DEFINED
```

## 1. Purpose

AIGOL_PROVIDER_CREDENTIAL_VAULT_V1 defines the canonical provider credential vault architecture for AiGOL.

The vault becomes the canonical source of provider credential values while preserving:

- human authority;
- approval boundaries;
- replay visibility;
- fail-closed behavior;
- non-authoritative provider participation;
- secret-free governance evidence.

This artifact defines architecture, runtime boundaries, replay model, ACLI interaction model, migration plan, and certification requirements.

It does not implement the vault runtime.

## 2. Problem Statement

Current provider credential access is environment-based.

Current example:

```python
api_key_env = "AIGOL_OPENAI_API_KEY"

def api_key(self):
    return os.environ.get(self.api_key_env)
```

This means credentials are visible to provider runtime only if the launching process environment contains the correct variable.

Current status:

| Capability | Status |
| --- | --- |
| Provider governance | implemented |
| Provider lifecycle governance | implemented |
| Provider observability | implemented |
| Cognition participation observability | implemented |
| Provider credential registry | implemented as secret-free metadata |
| Operator bootstrap | implemented as environment propagation |
| Credential vault | missing |

Operational risks:

- duplicated credential references;
- bootstrap coupling;
- shell-specific credential visibility failures;
- provider onboarding complexity;
- multi-provider scaling risk;
- no canonical credential lifecycle storage boundary.

## 3. Canonical Credential Source

The canonical provider credential source SHALL become:

```text
Provider Credential Vault
```

Canonical credential references SHALL use:

```text
vault://provider/<provider_id>
```

Initial references:

| provider_id | canonical vault reference |
| --- | --- |
| openai | vault://provider/openai |
| claude | vault://provider/claude |
| gemini | vault://provider/gemini |
| mistral | vault://provider/mistral |

The provider credential registry remains the canonical secret-free provider metadata registry. Its credential reference field SHALL migrate from environment references to vault references through the migration plan in this artifact.

The vault, not environment variables, becomes the credential value retrieval boundary after migration certification.

## 4. Storage Architecture

The vault SHALL store credential values outside replay and outside governance artifacts.

Allowed storage backends:

1. local operator secret backend;
2. organization-approved secret manager;
3. encrypted local credential store;
4. platform keychain where available.

V1 canonical abstraction:

```text
ProviderCredentialVault
```

Required runtime functions:

```text
add(provider_id, credential_value, approval_context)
rotate(provider_id, new_credential_value, approval_context)
disable(provider_id, approval_context)
delete(provider_id, approval_context)
verify(provider_id)
retrieve_for_authorized_invocation(provider_id, authorization_context)
diagnose(provider_id)
history(provider_id)
```

Forbidden storage behavior:

- repository files containing credential values;
- governance artifacts containing credential values;
- replay artifacts containing credential values;
- credential value hashing for replay;
- ACLI display of credential contents;
- provider runtime fallback to ungoverned credential sources after vault migration.

## 5. Vault Record Model

The secret-bearing internal vault record may contain:

```json
{
  "provider_id": "openai",
  "credential_reference": "vault://provider/openai",
  "credential_value": "<secret value, never replayed>",
  "enabled": true,
  "created_at": "timestamp",
  "last_verified": "timestamp or null",
  "last_rotated": "timestamp or null",
  "last_used": "timestamp or null",
  "credential_generation_id": "<opaque non-secret random identifier>"
}
```

The replay-safe public diagnostic model SHALL contain only:

```json
{
  "provider_id": "openai",
  "credential_reference": "vault://provider/openai",
  "credential_present": true,
  "credential_enabled": true,
  "last_verified": "timestamp or null",
  "last_rotated": "timestamp or null",
  "last_used": "timestamp or null",
  "display_identifier": "...5NwA",
  "credential_value_recorded": false,
  "credential_hash_recorded": false,
  "authorization_header_recorded": false,
  "replay_safe": true
}
```

The `display_identifier` SHALL be derived from non-secret vault metadata, such as an opaque random credential generation id. It SHALL NOT be derived from the credential value or a credential value hash.

## 6. Credential Lifecycle Workflows

### 6.1 Onboarding

ACLI pattern:

```text
add provider credential openai
```

Expected flow:

```text
Human
→ ACLI
→ clarification if provider or credential scope is unclear
→ human approval
→ vault add
→ provider governance event
→ replay-safe evidence
→ verification guidance
```

Rules:

- credential value entry must occur through a secret input boundary;
- the secret input boundary must disable echo where supported;
- the value must not be recorded in replay;
- the value must not be hashed for replay;
- the provider must be present in the provider credential registry or fail closed;
- adding a credential for an existing enabled provider is REPLACE and requires explicit human approval.

Replay artifact:

```text
PROVIDER_CREDENTIAL_VAULT_ONBOARDING_ARTIFACT_V1
```

Required replay-safe fields:

- provider_id
- credential_reference
- credential_present_after
- credential_enabled_after
- display_identifier
- human_approval_required
- human_approval_recorded
- credential_value_recorded=false
- credential_hash_recorded=false
- created_at
- artifact_hash

### 6.2 Rotation

ACLI pattern:

```text
rotate provider credential openai
```

Expected flow:

```text
Human
→ ACLI
→ rotation intent confirmation
→ human approval
→ secret input boundary
→ vault rotate
→ previous generation disabled or superseded
→ verification
→ replay-safe evidence
```

Rules:

- ROTATE requires human approval;
- rotation must fail closed if no existing credential is present unless explicitly converted into ADD after confirmation;
- previous credential value must not be replayed;
- new credential value must not be replayed or hashed;
- display_identifier must change after successful rotation.

Replay artifact:

```text
PROVIDER_CREDENTIAL_VAULT_ROTATION_ARTIFACT_V1
```

### 6.3 Disable

ACLI pattern:

```text
disable provider credential openai
```

Expected flow:

```text
Human
→ ACLI
→ impact explanation
→ human approval
→ vault disable
→ provider governance event
→ replay-safe dependency impact evidence
```

Rules:

- DISABLE requires human approval;
- disabled credentials must not be returned to provider runtimes;
- provider invocation must fail closed with dependency failure classification.

Replay artifact:

```text
PROVIDER_CREDENTIAL_VAULT_DISABLE_ARTIFACT_V1
```

### 6.4 Delete

ACLI pattern:

```text
delete provider credential openai
```

Expected flow:

```text
Human
→ ACLI
→ irreversible action warning
→ human approval
→ vault delete
→ verification of absence
→ replay-safe evidence
```

Rules:

- DELETE requires human approval;
- deletion must fail closed if approval is missing;
- deletion must remove credential value from vault storage;
- replay must preserve that deletion occurred without preserving any deleted value.

Replay artifact:

```text
PROVIDER_CREDENTIAL_VAULT_DELETE_ARTIFACT_V1
```

### 6.5 Verification

ACLI pattern:

```text
verify provider credential openai
```

Expected flow:

```text
Human
→ ACLI
→ vault diagnostic
→ optional provider-specific non-mutating validation
→ replay-safe verification evidence
```

Rules:

- VERIFY does not require destructive-action approval;
- verification must not invoke a provider unless the operator explicitly requests provider reachability validation;
- default verification checks only vault presence, enabled status, and metadata integrity.

Replay artifact:

```text
PROVIDER_CREDENTIAL_VAULT_VERIFICATION_ARTIFACT_V1
```

## 7. Approval Boundaries

Human approval is required for:

- ROTATE
- DISABLE
- DELETE
- REPLACE
- ADD when provider is unknown or the action would overwrite existing enabled credential state

Human approval is not required for:

- SHOW
- VERIFY metadata-only checks
- credential history inspection

Approval artifacts must record:

- provider_id
- operation
- approved_by
- approval_status
- approval_timestamp
- impact_acknowledged
- credential_value_recorded=false
- credential_hash_recorded=false

Approval does not authorize provider invocation. Provider invocation still requires the existing governed provider execution authorization path.

## 8. Runtime Boundaries

### 8.1 Vault Runtime

Proposed module:

```text
aigol/runtime/provider_credential_vault.py
```

Allowed responsibilities:

- manage credential value storage through the approved backend;
- return secret values only to authorized provider runtime boundaries;
- record secret-free lifecycle artifacts;
- provide secret-free diagnostics;
- maintain lifecycle history;
- fail closed on missing, disabled, corrupted, or unauthorized credentials.

Forbidden responsibilities:

- provider selection;
- ERR mutation;
- provider invocation;
- worker invocation;
- human approval fabrication;
- replay mutation;
- storing secrets in repository files.

### 8.2 Provider Runtime Boundary

Provider runtimes SHALL retrieve credentials through:

```text
ProviderCredentialVault.retrieve_for_authorized_invocation(provider_id, authorization_context)
```

Retrieval must require:

- provider_id;
- workflow or invocation id;
- authorization artifact reference;
- approved credential reference;
- replay-safe retrieval attempt artifact.

Retrieval must fail closed if:

- provider is unknown;
- credential is absent;
- credential is disabled;
- authorization context is missing;
- vault backend is unavailable;
- credential reference does not match registry policy.

### 8.3 Registry Boundary

Provider Credential Registry remains secret-free.

Registry V2 should map:

```text
openai -> vault://provider/openai
claude -> vault://provider/claude
gemini -> vault://provider/gemini
mistral -> vault://provider/mistral
```

Registry does not retrieve credentials.

### 8.4 Operator Bootstrap Boundary

Operator Environment Bootstrap remains valid during migration.

After vault certification:

- bootstrap may be used only to seed or repair the vault;
- provider runtime should not require repeated shell exports;
- environment variables become compatibility inputs, not canonical runtime credential sources.

## 9. Replay Model

Replay-visible artifacts:

- PROVIDER_CREDENTIAL_VAULT_ONBOARDING_ARTIFACT_V1
- PROVIDER_CREDENTIAL_VAULT_ROTATION_ARTIFACT_V1
- PROVIDER_CREDENTIAL_VAULT_DISABLE_ARTIFACT_V1
- PROVIDER_CREDENTIAL_VAULT_DELETE_ARTIFACT_V1
- PROVIDER_CREDENTIAL_VAULT_VERIFICATION_ARTIFACT_V1
- PROVIDER_CREDENTIAL_VAULT_RETRIEVAL_ATTEMPT_ARTIFACT_V1
- PROVIDER_CREDENTIAL_VAULT_DIAGNOSTIC_ARTIFACT_V1
- PROVIDER_CREDENTIAL_VAULT_HISTORY_ARTIFACT_V1

Required fields:

- artifact_type
- provider_id
- credential_reference
- operation
- credential_present
- credential_enabled
- display_identifier
- last_verified
- last_rotated
- last_used
- human_approval_required
- human_approval_recorded
- credential_value_recorded=false
- credential_hash_recorded=false
- authorization_header_recorded=false
- provider_invoked=false unless a separate governed provider invocation occurs
- worker_invoked=false unless a separate governed worker invocation occurs
- replay_visible=true
- created_at
- artifact_hash

Forbidden replay fields:

- credential_value
- credential_hash
- authorization header value
- request payload containing secrets
- backend-specific secret material
- environment variable value

## 10. ACLI Interaction Model

Natural language and command-like entries should converge to the same governed workflows.

Canonical ACLI commands:

```text
add provider credential <provider>
rotate provider credential <provider>
disable provider credential <provider>
delete provider credential <provider>
verify provider credential <provider>
show provider credentials
show provider credential history
```

Operator-safe example output:

```text
provider: openai
credential_reference: vault://provider/openai
identifier: ...5NwA
status: enabled
credential_present: true
last_verified: 2026-06-21T00:00:00Z
last_rotated: 2026-06-21T00:00:00Z
last_used: 2026-06-21T00:00:00Z
credential_value_recorded: false
credential_hash_recorded: false
```

ACLI must clarify when:

- provider name is missing;
- provider alias is ambiguous;
- operation is destructive;
- the user asks to overwrite an existing credential;
- the user asks for credential contents.

ACLI must refuse or fail closed when:

- the user requests secret display;
- approval is missing for destructive operations;
- the provider is not registered;
- vault backend is unavailable;
- credential verification cannot safely complete.

## 11. Vault Diagnostics

Required diagnostic fields:

| Field | Description |
| --- | --- |
| provider_id | Canonical provider id |
| credential_reference | `vault://provider/<provider_id>` |
| credential_present | Boolean presence marker |
| credential_enabled | Boolean enabled marker |
| last_verified | Timestamp or null |
| last_rotated | Timestamp or null |
| last_used | Timestamp or null |
| display_identifier | Non-secret metadata identifier |
| failure_classification | Optional dependency failure class |
| remediation_hint | Operator-safe next action |
| credential_value_recorded | Always false in replay |
| credential_hash_recorded | Always false in replay |
| authorization_header_recorded | Always false in replay |

Failure classifications:

- MISSING_CREDENTIAL
- DISABLED_CREDENTIAL
- VAULT_BACKEND_UNAVAILABLE
- VAULT_RECORD_CORRUPT
- AUTHORIZATION_REQUIRED
- PROVIDER_NOT_REGISTERED
- UNKNOWN_CREDENTIAL_FAILURE

## 12. Migration Plan

Migration objective:

```text
os.environ["AIGOL_OPENAI_API_KEY"]
→
Provider Credential Vault
```

### Phase 1: Definition

This artifact defines vault architecture and lifecycle.

Existing certifications remain valid:

- CERT-000009 remains valid as environment-backed live provider certification.
- Provider Governance Certification remains valid for governance lifecycle and replay visibility.
- Provider Participation Observability remains valid.

### Phase 2: Runtime Implementation

Implement:

```text
aigol/runtime/provider_credential_vault.py
```

Add a compatibility backend that can seed vault records from approved environment variables without replaying values.

Environment variables remain accepted only as onboarding inputs.

### Phase 3: ProviderConfig Adapter

Update provider configuration from:

```text
api_key_env = "AIGOL_OPENAI_API_KEY"
api_key() -> os.environ.get(api_key_env)
```

to:

```text
credential_reference = "vault://provider/openai"
api_key() -> ProviderCredentialVault.retrieve_for_authorized_invocation(...)
```

The adapter must preserve fail-closed behavior and existing authorization checks.

### Phase 4: Registry Migration

Introduce Provider Credential Registry V2 or a V1-compatible migration artifact:

```text
env:AIGOL_OPENAI_API_KEY
→
vault://provider/openai
```

Provider-native aliases may remain bootstrap inputs but must not remain canonical runtime references.

### Phase 5: Certification

Run credential vault certification before declaring vault-backed live provider certification.

### Phase 6: Deprecation

After successful vault certification:

- deprecate environment variables as runtime credential source;
- retain operator bootstrap only for vault seeding or emergency compatibility;
- update live provider certification to prove vault-backed retrieval.

## 13. Certification Requirements

Required certification campaigns:

### 13.1 Vault Lifecycle Certification

Must verify:

- ADD records secret-free onboarding evidence;
- VERIFY records secret-free verification evidence;
- ROTATE requires approval and changes display identifier;
- DISABLE requires approval and prevents retrieval;
- DELETE requires approval and removes retrievable value;
- REPLACE requires approval;
- unknown provider fails closed;
- disabled provider fails closed;
- missing provider fails closed;
- replay reconstructs all lifecycle artifacts.

### 13.2 Vault Runtime Boundary Certification

Must verify:

- provider runtime retrieves only after authorization;
- credential value is never replayed;
- credential hash is never replayed;
- retrieval attempt is replay-visible;
- vault backend unavailable fails closed;
- provider invocation is blocked when retrieval fails.

### 13.3 ACLI Certification

Must verify:

- natural language onboarding routes correctly;
- destructive actions require human approval;
- secret display requests are refused;
- show commands expose only safe diagnostics;
- history is replay-safe;
- ambiguity triggers clarification.

### 13.4 Migration Certification

Must verify:

- CERT-000009 remains historically valid;
- environment-backed provider path remains replay-readable;
- vault-backed provider path can replace environment retrieval;
- provider governance observability continues to work;
- cognition participation observability continues to work.

## 14. Future Multi-Provider Support

The vault design supports:

- OpenAI;
- Claude / Anthropic;
- Gemini;
- Mistral;
- future providers.

Adding a future provider requires:

1. Provider Credential Registry entry;
2. vault reference `vault://provider/<provider_id>`;
3. provider runtime adapter;
4. dependency failure messages;
5. lifecycle certification;
6. provider-specific live certification if invocation is required.

No new environment-variable convention should be required for steady-state runtime use.

## 15. Answers To Governing Questions

### What should be the canonical credential source?

The Provider Credential Vault.

Canonical reference:

```text
vault://provider/<provider_id>
```

### How should credentials be stored?

Credential values should be stored in an approved local or organizational secret backend behind `ProviderCredentialVault`. Values must never be written to replay, governance artifacts, git, logs, or ACLI output.

### How should credentials be rotated?

Rotation requires human approval, secret input boundary, new vault generation, old generation disablement or supersession, verification, and replay-safe rotation evidence.

### How should approval boundaries work?

Destructive or credential-changing actions require human approval. Approval does not authorize provider invocation. Invocation remains governed by provider execution authorization.

### How should replay-safe evidence work?

Replay records only operation metadata, provider id, vault reference, status booleans, display identifier, timestamps, approval evidence hashes, and non-authority declarations.

### How should provider onboarding work?

Onboarding uses ACLI clarification, human approval where required, secret input, vault write, verification, provider governance event, and replay-safe evidence.

## 16. Non-Goals

This artifact does not:

- implement credential storage;
- choose a specific enterprise secret-manager vendor;
- redesign ERR;
- redesign ACLI;
- authorize provider invocation;
- modify CERT-000009;
- invalidate environment-backed historical evidence;
- store secrets in governance artifacts.

## 17. Final Verdict

```text
PROVIDER_CREDENTIAL_VAULT_DEFINED
```
