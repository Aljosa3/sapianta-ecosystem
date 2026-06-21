# AIGOL_PROVIDER_CREDENTIAL_GOVERNANCE_REVIEW_V1

Status: governance review.

Purpose: determine whether AiGOL has a canonical provider credential registry and identify the smallest governance-preserving remediation.

This artifact does not implement credential storage, secret retrieval, provider routing, provider fallback, worker invocation, ERR redesign, or runtime behavior changes.

## 1. Review Scope

Reviewed surfaces:

- provider selection;
- ERR provider metadata;
- operator entrypoints;
- provider runtimes;
- live provider credential boundary;
- dependency failure runtime;
- first live cognition-provider certification evidence.

Primary implementation references:

- `aigol/runtime/external_resource_registry_runtime.py`
- `aigol/runtime/first_live_provider_activation_package_instantiation.py`
- `aigol/runtime/first_live_provider_dispatch_authorization_instantiation.py`
- `aigol/runtime/first_live_provider_operator_entrypoint.py`
- `aigol/runtime/first_live_provider_execution_runtime.py`
- `aigol/runtime/live_provider_runtime_boundary.py`
- `aigol/runtime/live_provider_invocation_prerequisites.py`
- `aigol/runtime/llm_cognition_provider_runtime.py`
- `aigol/runtime/first_real_provider_runtime.py`
- `aigol/runtime/providers/provider_config.py`

Primary governance references:

- `AIGOL_LIVE_PROVIDER_CREDENTIAL_BOUNDARY_V1`
- `AIGOL_PROVIDER_CREDENTIAL_BOUNDARY_REVIEW_V1`
- `AIGOL_DEPENDENCY_FAILURE_RUNTIME_V1`
- `AIGOL_OPERATOR_ENTRYPOINT_CREDENTIAL_MISMATCH_REVIEW_V1`
- `AIGOL_LIVE_PROVIDER_ENVIRONMENT_TRACE_V1`
- `AIGOL_FIRST_LIVE_COGNITION_PROVIDER_CERTIFICATION_V1`
- `AIGOL_OPENAI_TRANSPORT_DIAGNOSTIC_V1`

## 2. Current Credential Architecture

Current credential ownership model:

```text
CREDENTIAL_OWNER = HUMAN_OR_ORGANIZATION_SECRET_AUTHORITY
AIGOL_CREDENTIAL_OWNERSHIP = NONE
```

Current secret handling model:

```text
AiGOL may record credential references and availability booleans.
AiGOL must not record credential values, bearer tokens, authorization headers, or credential hashes.
```

Current runtime credential path for the first live OpenAI cognition provider:

```text
operator or organization secret authority
-> governed process environment
-> env:AIGOL_OPENAI_API_KEY
-> operator entrypoint credential presence check
-> execution runtime credential revalidation
-> live provider boundary credential retrieval
-> in-memory OpenAI executor metadata
-> no-secret replay evidence
```

This architecture correctly preserves:

- external credential ownership;
- no secret storage in AiGOL;
- no secret replay;
- fail-closed behavior on missing credentials;
- operator-visible environment dependency;
- replay-visible credential policy and credential availability evidence.

## 3. Provider Selection and ERR Metadata

ERR currently registers real cognition providers as passive metadata:

```text
resource_id = openai | claude | gemini | mistral
resource_type = COGNITION_PROVIDER
capabilities = reasoning, planning, summarization, analysis, generation
status = ACTIVE
```

ERR proves only resource metadata selection.

ERR does not store:

- credential references;
- credential environment names;
- credential presence;
- credential authority;
- provider authentication requirements;
- secret-manager references.

This is architecturally correct because ERR is passive and must not become credential storage or invocation infrastructure.

However, because ERR intentionally excludes credentials, a separate canonical credential-reference surface is required if provider onboarding is to become deterministic across multiple providers.

## 4. Current Credential Reference Locations

Credential references currently exist across multiple surfaces.

| Surface | Current reference behavior | Governance interpretation |
| --- | --- | --- |
| Live provider credential boundary design | Allows `env:AIGOL_OPENAI_API_KEY` initially; future secret-manager references deferred | Correct boundary definition, not a registry |
| First live activation package | Creates `env:OPENAI_PROVIDER_CREDENTIAL` as a transitional internal policy reference | Transitional and not canonical for dispatch |
| Operator entrypoint | Hard-codes `env:AIGOL_OPENAI_API_KEY` and fails closed if missing | Correct for first OpenAI path, not extensible registry |
| Execution runtime | Creates live credential policy view with `env:AIGOL_OPENAI_API_KEY` | Correct for first OpenAI path |
| Live provider runtime boundary | Reads `credential_policy_artifact["credential_reference"]` from `os.environ` | Boundary supports env references but not a provider registry |
| LLM cognition provider runtime | Contains `_credential_env_registry(provider_id)` returning `("AIGOL_OPENAI_API_KEY", "OPENAI_API_KEY")` for OpenAI | Local helper registry, not canonical governance registry |
| ProviderConfig | Defaults `api_key_env = "AIGOL_OPENAI_API_KEY"` | Local config default, not canonical governance registry |
| Dependency failure runtime | Defines missing credential classification and operator guidance | Generic failure model, not credential registry |

Conclusion:

AiGOL has a credential boundary and OpenAI-specific credential conventions, but credential references are not governed by one canonical provider credential registry.

## 5. Determinations

### 5.1 Where Provider Credentials Are Expected To Live

Provider credentials are expected to live outside AiGOL in an operator-controlled or organization-controlled secret authority.

For the current first live OpenAI path, the concrete runtime location is:

```text
env:AIGOL_OPENAI_API_KEY
```

The environment variable must be present in the exact governed process environment that launches the operator entrypoint or certification entrypoint.

AiGOL must not store the credential in:

- ERR;
- provider metadata;
- replay artifacts;
- governance artifacts;
- certification reports;
- request or response envelopes;
- exception text.

### 5.2 Whether A Canonical Credential Registry Exists

Canonical provider credential registry:

```text
NOT FOUND
```

Existing related surfaces are not equivalent to a canonical registry:

- ERR is passive resource metadata and intentionally excludes credentials.
- `LIVE_PROVIDER_CREDENTIAL_POLICY_ARTIFACT_V1` is an invocation-scoped policy artifact.
- `_credential_env_registry(provider_id)` is a local helper inside the LLM cognition provider runtime.
- `ProviderConfig.api_key_env` is a local provider config default.
- `AIGOL_PROVIDER_CREDENTIAL_BOUNDARY_REVIEW_V1` documents current OpenAI expectations.

No single artifact or runtime module currently defines:

- provider id -> allowed credential references;
- provider id -> required credential class;
- provider id -> secret authority type;
- provider id -> verification command or diagnostic fields;
- provider id -> replay-visible credential policy requirements;
- provider onboarding acceptance criteria for credentials.

### 5.3 Whether Provider-Specific Environment Variables Are Standardized

For OpenAI:

```text
AIGOL_OPENAI_API_KEY = de facto standard
```

For other real cognition providers already present in ERR metadata:

```text
CLAUDE = NOT STANDARDIZED
GEMINI = NOT STANDARDIZED
MISTRAL = NOT STANDARDIZED
```

Compatibility alias:

`OPENAI_API_KEY` appears in the lower-level LLM cognition provider helper registry, but the first live certification/operator path requires `AIGOL_OPENAI_API_KEY`.

Transitional internal activation reference:

`env:OPENAI_PROVIDER_CREDENTIAL` appears in the activation package policy and is later mapped to `AIGOL_OPENAI_API_KEY` by execution-runtime logic. This is not a canonical provider credential registry.

### 5.4 Whether Credential Discovery Is Replay-Visible

Credential discovery is partially replay-visible.

Replay-visible today:

- credential policy reference;
- credential reference type;
- credential availability boolean;
- credential freshness validation;
- credential retrieval attempt in the live boundary;
- credential value omitted;
- credential secret not replayed;
- authorization header not replayed.

Not replay-visible today:

- canonical source of truth for provider credential reference;
- whether a provider credential reference was derived from a registry;
- whether aliases were considered;
- which alias won if multiple aliases exist;
- operator-facing diagnostic source for provider-specific credential requirements;
- multi-provider credential onboarding evidence.

The current replay evidence can prove that a specific invocation used or checked a credential reference. It cannot prove that the reference came from a canonical provider credential registry.

### 5.5 Whether Credential Diagnostics Are Operator-Visible

Credential diagnostics are partially operator-visible.

Operator-visible today:

- missing `AIGOL_OPENAI_API_KEY` can abort certification before provider invocation;
- dependency failure runtime defines `MISSING_CREDENTIAL`;
- manual execution command prints credential presence booleans without printing values;
- transport diagnostic provides operator verification guidance.

Missing operator-visible governance:

- provider-specific credential requirement inventory;
- provider onboarding credential checklist;
- canonical remediation owner per provider;
- canonical verification command per provider;
- safe alias policy per provider;
- registry-backed diagnostic message explaining exactly which credential reference was expected and why.

### 5.6 Whether Provider Onboarding Is Deterministic

Provider onboarding is deterministic for provider selection metadata but not for credentials.

Deterministic today:

- ERR registers real cognition provider ids.
- ERR selects the first active matching provider by capability.
- OpenAI first-live path is hard-scoped and one-attempt.
- Credential absence fails closed.

Not deterministic today:

- adding Claude, Gemini, or Mistral credentials;
- standardizing environment variable names for non-OpenAI providers;
- selecting allowed credential reference aliases;
- proving that credential policy artifacts were generated from canonical provider credential metadata;
- producing provider-specific operator diagnostics from a canonical source.

## 6. Governance Gaps

### Gap 1: No Canonical Provider Credential Registry

AiGOL has a credential boundary but no canonical registry that maps provider ids to allowed credential references and diagnostic requirements.

Impact:

- future provider onboarding may duplicate OpenAI-specific patterns inconsistently;
- operator diagnostics may drift across provider paths;
- replay can show a credential policy but not its canonical source.

### Gap 2: Credential Reference Scattered Across Runtime Surfaces

`AIGOL_OPENAI_API_KEY` appears in operator entrypoint, execution runtime, lower-level provider runtime, provider config, tests, and governance artifacts.

Impact:

- updates require coordinated edits;
- aliases can diverge;
- certification expectations can conflict with runtime checks.

### Gap 3: Transitional Activation Reference Remains Visible

The activation package uses `env:OPENAI_PROVIDER_CREDENTIAL` while the live operator path uses `env:AIGOL_OPENAI_API_KEY`.

Impact:

- reviewers can see two credential references and infer a mismatch;
- activation `credential_available=true` can be confused with dispatch-time process environment availability;
- deterministic onboarding semantics are weaker than they should be.

### Gap 4: Multi-Provider Credentials Are Not Governed

ERR already knows provider ids beyond OpenAI, but their credential references are not standardized.

Impact:

- multi-provider cognition certification would lack a credential governance substrate;
- provider-specific environment naming could become ad hoc;
- dependency-failure reporting could not produce canonical provider-specific remediation.

### Gap 5: Credential Diagnostics Are Not Registry-Backed

Dependency failure runtime defines a universal failure shape, but current provider credential diagnostics are assembled from specific runtime artifacts and command guidance.

Impact:

- users and operators may receive correct but inconsistent messages;
- future provider onboarding lacks a single diagnostic source of truth.

## 7. Smallest Remediation

The smallest conformant remediation is not to store credentials in AiGOL.

The smallest conformant remediation is to define a secret-free canonical provider credential registry.

Recommended artifact:

```text
AIGOL_PROVIDER_CREDENTIAL_REGISTRY_V1
```

Recommended runtime module:

```text
aigol/runtime/provider_credential_registry.py
```

The registry must contain only secret-free metadata.

Required fields:

| Field | Purpose |
| --- | --- |
| `provider_id` | Canonical provider id, matching ERR resource id |
| `provider_resource_type` | `COGNITION_PROVIDER` or future bounded provider type |
| `credential_class` | Example: `API_KEY` |
| `primary_reference` | Example: `env:AIGOL_OPENAI_API_KEY` |
| `allowed_aliases` | Optional secret-free aliases, if governance approves them |
| `secret_authority` | Example: `operator_controlled_environment` or future secret-manager authority |
| `required_for_capabilities` | Capabilities requiring this credential |
| `operator_label` | Human-readable provider credential requirement |
| `verification_guidance` | Secret-safe presence check guidance |
| `retry_guidance` | What to retry after remediation |
| `replay_fields` | Required replay-visible credential evidence fields |
| `secret_storage_allowed` | Must be `false` for current model |
| `credential_value_replay_allowed` | Must be `false` |
| `credential_hash_replay_allowed` | Must be `false` |

Initial registry content:

```text
provider_id = openai
provider_resource_type = COGNITION_PROVIDER
credential_class = API_KEY
primary_reference = env:AIGOL_OPENAI_API_KEY
allowed_aliases = []
secret_authority = operator_controlled_environment
required_for_capabilities = reasoning, planning, summarization, analysis, generation
secret_storage_allowed = false
credential_value_replay_allowed = false
credential_hash_replay_allowed = false
```

Optional future entries may be defined only when those providers are ready for governed certification.

## 8. Remediation Boundaries

The remediation must preserve:

- ERR passivity;
- no secret storage;
- no credential values in replay;
- no credential hashes in replay;
- fail-closed behavior;
- human approval before live invocation;
- no provider fallback;
- no worker invocation;
- no governance mutation;
- no replay mutation.

The remediation must not:

- move credentials into ERR;
- make ERR responsible for credential lookup;
- add automatic credential discovery;
- read environment variables during provider selection;
- silently substitute aliases;
- authorize live provider invocation by registry presence alone.

## 9. Recommended Integration Points

Minimal integration sequence:

1. Define secret-free credential registry artifact.
2. Add runtime helper that returns credential metadata by provider id.
3. Replace hard-coded OpenAI credential-reference constants with registry lookups where appropriate.
4. Keep the operator entrypoint fail-closed check.
5. Keep execution runtime credential revalidation.
6. Keep live provider boundary retrieval from invocation-scoped credential policy.
7. Record in replay that the credential policy was derived from the canonical registry by provider id and registry version.
8. Update dependency failure runtime inputs so missing credential messages can cite the provider registry metadata.
9. Add tests proving no secret material appears in registry, replay, errors, or diagnostics.

## 10. Pass/Fail Criteria For Future Registry Certification

Pass criteria:

- OpenAI credential reference resolves from the canonical registry.
- Credential policy artifacts reference registry version and provider id.
- Missing credential failure remains fail-closed.
- Credential values are never serialized.
- Credential hashes are never serialized.
- Operator diagnostics identify `env:AIGOL_OPENAI_API_KEY` without printing its value.
- ERR remains credential-free.
- Existing first-live OpenAI certification path behavior is unchanged except for registry-backed reference derivation.

Failure criteria:

- registry stores any secret value;
- registry stores any authorization header;
- registry becomes provider selection or routing authority;
- ERR stores or retrieves credential references;
- aliases are silently substituted without replay-visible evidence;
- credential availability is treated as invocation authorization;
- provider onboarding can proceed without a credential policy.

## 11. Review Answers

1. Where provider credentials are expected to live:

   Outside AiGOL, in an operator-controlled or organization-controlled secret authority. For current OpenAI live certification, the governed process environment must contain `AIGOL_OPENAI_API_KEY`.

2. Whether a canonical credential registry exists:

   No. AiGOL has credential boundary artifacts and OpenAI-specific references, but no canonical provider credential registry.

3. Whether provider-specific environment variables are standardized:

   OpenAI is de facto standardized as `AIGOL_OPENAI_API_KEY`. Other providers are not standardized.

4. Whether credential discovery is replay-visible:

   Invocation-scoped credential policy and presence checks are replay-visible. Registry-derived credential discovery is not replay-visible because no registry exists.

5. Whether credential diagnostics are operator-visible:

   Partially. Missing OpenAI credential diagnostics are visible, but they are not generated from a canonical provider credential metadata source.

6. Whether provider onboarding is deterministic:

   Provider selection metadata onboarding is deterministic through ERR. Credential onboarding is not fully deterministic because provider credential references are not canonicalized in one registry.

## 12. Final Verdict

`PROVIDER_CREDENTIAL_GOVERNANCE_GAP_FOUND`

AiGOL has a governed credential boundary and a working OpenAI-specific credential convention, but it does not yet have a canonical provider credential registry. The smallest remediation is a secret-free provider credential registry that records provider credential references and operator diagnostics without storing, hashing, replaying, retrieving, or owning credential values.
