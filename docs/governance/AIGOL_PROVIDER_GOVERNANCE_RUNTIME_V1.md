# AIGOL_PROVIDER_GOVERNANCE_RUNTIME_V1

Status: IMPLEMENTED

Date: 2026-06-21

Governing inputs:

- AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1
- AIGOL_OPERATOR_ENVIRONMENT_BOOTSTRAP_V1
- FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED / CERT-000009
- ERR architecture
- Replay architecture
- Human approval boundary

## 1. Purpose

AIGOL_PROVIDER_GOVERNANCE_RUNTIME_V1 defines and implements the canonical runtime layer for provider credential diagnostics, lifecycle governance, provider usage observability, and cognition participation observability.

The runtime does not grant providers authority. Providers remain non-authoritative proposal or execution dependencies governed by AiGOL, human approval boundaries, workflow routing, and replay reconstruction.

## 2. Scope

Implemented runtime module:

```text
aigol/runtime/provider_governance_runtime.py
```

Implemented certification integration:

```text
aigol/runtime/first_live_cognition_provider_certification.py
```

Implemented ACLI query surface:

```text
aigol provider governance status
aigol provider governance credentials
aigol provider governance usage
aigol provider governance failures
aigol provider governance costs
aigol provider governance participation
```

The lifecycle mutation API is runtime-level only in V1. Destructive lifecycle operations require explicit human approval artifacts before a replay-visible event can be recorded.

The first live cognition-provider certification emits provider governance observability without changing provider dispatch, credential retrieval, approval, replay, or certification logic.

## 3. Canonical Provider Source

The runtime uses Provider Credential Registry V1 semantics as the canonical provider source.

Initial provider references:

| provider_id | credential_reference | source_type |
| --- | --- | --- |
| openai | env:AIGOL_OPENAI_API_KEY | ENVIRONMENT_VARIABLE |
| claude | env:AIGOL_ANTHROPIC_API_KEY | ENVIRONMENT_VARIABLE |
| gemini | env:AIGOL_GEMINI_API_KEY | ENVIRONMENT_VARIABLE |
| mistral | env:AIGOL_MISTRAL_API_KEY | ENVIRONMENT_VARIABLE |

No credential values are stored, hashed, replayed, printed, or exposed.

## 4. Credential Lifecycle Operations

Supported lifecycle operations:

- ADD
- ENABLE
- DISABLE
- ROTATE
- REPLACE
- DELETE
- VERIFY

Human approval is required for:

- DISABLE
- ROTATE
- REPLACE
- DELETE

If required approval is missing or not approved, the runtime fails closed and no successful lifecycle event is produced.

## 5. Operator-Safe Credential Display

Credential diagnostics expose only:

- provider_id
- credential_reference
- credential_source_type
- credential_present
- credential_display_identifier
- remediation_hint
- operator_safe_message

The display identifier is derived from secret-free registry metadata, not from credential contents.

Example:

```text
provider=openai
credential_reference=env:AIGOL_OPENAI_API_KEY
credential_display_identifier=ref:...<registry_suffix>
credential_present=true
```

Forbidden evidence:

- full credential
- credential contents
- credential hashes
- authorization headers
- request payload secrets

## 6. Provider Usage Metrics

PROVIDER_USAGE_METRIC_ARTIFACT_V1 records replay-visible provider health and usage:

- provider_id
- model
- status
- availability
- success_count
- failure_count
- last_used
- last_failure
- latency_ms
- token_usage
- cost_tracking
- cost_tracking_hooks_present

Cost tracking remains hook-based in V1 and must remain secret-free.

## 7. Cognition Participation Observability

COGNITION_PARTICIPATION_ARTIFACT_V1 records when and why a provider participated in cognition.

Fields:

- provider_id
- participation_location
- participation_role
- workflow_id
- invocation_reason
- purpose
- response_used
- worker_invoked_after
- human_confirmation_required

Supported participation locations:

- HIRR
- OCS_LLM_COGNITION
- REPLAY_ANALYSIS
- IMPROVEMENT_PROPOSAL
- WORKER_GENERATION
- WORKER_REPAIR
- HUMAN_RESPONSE_ASSISTANCE

Unsupported locations fail closed.

## 8. Replay Artifacts

Implemented artifact types:

- PROVIDER_GOVERNANCE_EVENT_ARTIFACT_V1
- PROVIDER_USAGE_METRIC_ARTIFACT_V1
- COGNITION_PARTICIPATION_ARTIFACT_V1

Each artifact includes:

- runtime_version
- replay_visible=true
- artifact_hash
- non-authority declarations where relevant

Replay reconstruction verifies artifact hashes and summarizes:

- provider governance event count
- provider usage metric count
- cognition participation count
- provider status
- credential diagnostics
- usage
- failures
- costs
- cognition participation

The live cognition certification writes these artifacts under:

```text
<CERT_ROOT>/provider_governance/credential_lifecycle/
<CERT_ROOT>/provider_governance/usage/
<CERT_ROOT>/provider_governance/cognition_participation/
```

## 9. ACLI Query Definitions

Operator queries:

```bash
python -m aigol.cli.aigol_cli provider governance status --replay-root <path>
python -m aigol.cli.aigol_cli provider governance credentials --replay-root <path>
python -m aigol.cli.aigol_cli provider governance usage --replay-root <path>
python -m aigol.cli.aigol_cli provider governance failures --replay-root <path>
python -m aigol.cli.aigol_cli provider governance costs --replay-root <path>
python -m aigol.cli.aigol_cli provider governance participation --replay-root <path>
```

These commands are read-only. They do not modify credentials, invoke providers, invoke workers, or change governance state.

## 10. Governance Preservation

Preserved constraints:

- fail-closed behavior
- replay reconstruction
- governance authority boundaries
- human approval before destructive lifecycle changes
- non-authoritative provider principle
- secret-free replay evidence

## 11. Certification Tests

Implemented certification tests:

```text
tests/test_provider_governance_runtime_v1.py
```

Coverage:

- secret-free credential diagnostics
- VERIFY lifecycle event recording
- approval enforcement for destructive lifecycle operations
- provider usage metric replay reconstruction
- cognition participation replay reconstruction
- unsupported participation fail-closed behavior
- ACLI provider governance query rendering
- unknown provider fail-closed behavior

## 12. Final Verdict

PROVIDER_GOVERNANCE_RUNTIME_IMPLEMENTED
