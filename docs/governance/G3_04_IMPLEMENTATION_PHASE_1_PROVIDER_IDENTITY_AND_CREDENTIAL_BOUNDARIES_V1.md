# G3-04 Implementation Phase 1 Provider Identity And Credential Boundaries V1

Status: implementation certification artifact.

Scope: deterministic provider identity and credential-reference boundary layer.

This phase does not implement provider calls, provider selection, worker execution, Product 1
provider usage, deployment, or credential secret storage.

## 1. Objective

Implement the first runtime layer for G3-04 real provider activation:

```text
provider identity + credential reference evidence only
```

The runtime establishes role-separated provider identities and credential-reference artifacts
that can later support governed provider activation without granting invocation authority.

## 2. Runtime Implementation

Implemented runtime:

- `aigol/runtime/provider_identity_boundaries.py`

Implemented public functions:

- `create_provider_credential_reference(...)`;
- `create_provider_identity(...)`;
- `reconstruct_provider_identity_replay(...)`.

## 3. Provider Identity Model

Every provider identity records:

- provider id;
- external provider family;
- model id;
- provider role;
- capability declarations;
- credential reference id;
- credential reference;
- credential lifecycle state;
- activation status;
- replay lineage;
- rollback reference;
- immutable artifact hash.

Provider identity status:

| State | Meaning |
| --- | --- |
| `PROVIDER_IDENTITY_CREATED` | Provider identity evidence exists and is replay-visible |

Activation status values:

| State | Meaning |
| --- | --- |
| `PROVIDER_REGISTERED_INACTIVE` | Provider identity exists but cannot be invoked |
| `PROVIDER_ACTIVE_ADVISORY_ONLY` | Provider identity may be used only by later certified advisory paths |
| `PROVIDER_SUSPENDED` | Provider identity cannot be used until review |
| `PROVIDER_RETIRED` | Provider identity is permanently inactive |

Phase 1 creates identity evidence only. It does not perform activation, selection, or
provider calls.

## 4. Role-Separated External APIs

The runtime supports distinct provider identities for the same external API family.

Example:

| Provider Role | External Family | Credential Reference |
| --- | --- | --- |
| `COGNITION_PROVIDER` | `openai` | `vault://provider/openai-cognition-g3-04` |
| `TRANSLATION_WORKER` | `openai` | `vault://worker/openai-translation-g3-04` |
| `REPAIR_WORKER` | `openai` | `vault://worker/openai-repair-g3-04` |

The identities are not interchangeable. A credential reference created for one role cannot
be bound to a different provider role.

## 5. Credential Boundary Model

Credential reference artifacts record:

- credential reference id;
- credential reference;
- credential role;
- credential lifecycle state;
- replay lineage;
- rollback reference;
- immutable artifact hash.

Credential lifecycle states:

| State | Meaning |
| --- | --- |
| `CREDENTIAL_NOT_CONFIGURED` | Credential reference exists but no credential is configured |
| `CREDENTIAL_CONFIGURED_INACTIVE` | Credential reference exists but provider use is inactive |
| `CREDENTIAL_ACTIVE_ADVISORY_ONLY` | Credential may be used only by later certified advisory paths |
| `CREDENTIAL_SUSPENDED` | Credential cannot be used until review |
| `CREDENTIAL_RETIRED` | Credential is permanently inactive |

Credentials are reference-only:

- credential secrets are not stored;
- credential secrets are not replayed;
- credential values are not recorded;
- credential hashes are not recorded;
- authorization headers are not recorded.

## 6. Capability Declarations

Provider capabilities are declarations, not invocation permissions.

Every capability must be:

- advisory only;
- scoped to a provider role;
- unable to grant execution authority.

The runtime fails closed if any capability claims execution authority or is not advisory.

## 7. Replay Evidence

Credential replay evidence is written as:

- `000_provider_credential_reference_created.json`.

Provider identity replay evidence is written as:

- `000_provider_identity_created.json`.

Replay reconstruction validates:

- wrapper hash;
- artifact hash;
- credential reference hash;
- provider identity hash;
- credential lifecycle state;
- activation status;
- replay lineage;
- secret-free evidence;
- non-invocation flags.

## 8. Non-Authority Guarantees

The runtime explicitly denies:

- provider invocation;
- provider selection;
- provider request creation;
- provider response receipt;
- worker invocation;
- approval creation;
- authorization creation;
- execution request;
- repository mutation;
- deployment request;
- external integration invocation.

Provider identity evidence is not provider activation.

Credential reference evidence is not credential use.

## 9. Regression Coverage

Added regression tests:

- role-separated identities for the same external API family;
- credential secret material rejection;
- provider/credential role mismatch rejection;
- execution-authority capability rejection;
- replay tamper detection;
- non-invocation and secret-surface assertions.

Targeted test file:

- `tests/test_provider_identity_boundaries_v1.py`

## 10. Rollback Impact

Rollback impact is low.

The runtime is additive and non-authoritative:

- no existing provider runtime is modified;
- no provider transport is activated;
- no provider selection is implemented;
- no worker execution is implemented;
- no Product 1 provider usage is implemented;
- no deployment path is introduced.

Removing the runtime, tests, and this document restores the repository to the G3-04 program
state.

## 11. Certification Impact

This phase establishes the deterministic identity and credential-reference substrate needed
for later G3-04 provider activation phases.

Remaining G3-04 phases must implement:

- provider policy gates;
- advisory provider invocation substrate;
- OCS provider invocation path;
- ACLI provider-assisted rendering;
- Product 1 provider evidence binding;
- escalation and comparison policies;
- failure/fallback certification.

## 12. Validation Scope

Required validation:

```text
git diff --check
python -m py_compile ...
targeted provider identity tests
python -m pytest -q
```

Generated `.runtime` artifacts from validation must be cleaned before completion.

## 13. Final Verdict

```text
G3_04_IMPLEMENTATION_PHASE_1_READY
```
