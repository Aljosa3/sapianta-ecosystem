# G5-01 Provider Identity And Bound Read-Only Cognition Execution V1

Status: provider identity alignment and bounded read-only cognition execution architecture certified.

Final verdict: READ_ONLY_PROVIDER_EXECUTION_READY

## 1. Purpose

This artifact certifies the architectural readiness of the first Generation 5 governed execution capability:

```text
PGSP-bound read-only provider cognition execution
```

The capability is intentionally narrow. It permits a future runtime implementation to execute a cognition-provider call only when the call is:

- read-only;
- non-mutating;
- provider cognition only;
- replay-visible;
- governance-checked;
- authorization-bound;
- credential-bound;
- post-execution reviewable.

This milestone does not execute a provider, invoke a worker, mutate a repository, deploy software, create approval activation, or change runtime behavior.

## 2. Background Determination

G5-00 concluded:

```text
EXECUTION_TRANSITION_BLOCKERS_FOUND
```

The recommended first governed execution capability was:

```text
PGSP_BOUND_READ_ONLY_PROVIDER_COGNITION_EXECUTION_V1
```

G5-01 narrows and certifies the architecture for that first capability while preserving the permanent Generation 3 invariant:

The same external LLM provider may appear under multiple independent Platform Core identities.

Examples:

- cognition provider;
- translation provider;
- repair provider;
- worker.

These identities are not interchangeable, even when backed by the same external API family.

## 3. Scope

Allowed future execution scope:

- one PGSP session;
- one cognition-provider identity;
- one read-only cognition request;
- one provider dispatch attempt;
- credential retrieval through the governed credential boundary;
- replay-visible request, response, or error evidence;
- governance review before and after dispatch;
- no repository mutation;
- no worker execution;
- no deployment;
- no approval activation in this milestone.

Excluded from this milestone:

- repository mutation;
- worker execution;
- deployment;
- approval creation;
- approval activation;
- authorization creation from natural-language intent;
- provider output as authority;
- provider fallback;
- retry loops;
- multi-provider dispatch;
- cross-session authority transfer.

## 4. Provider Identity Assessment

Provider identity evidence already establishes:

- provider id;
- external provider family;
- model id;
- provider role;
- capability declarations;
- credential reference id;
- credential lifecycle state;
- activation status;
- replay lineage;
- immutable artifact hash.

The identity model supports role-separated identities for the same external API family.

Example:

| Architectural Identity | External Family | Allowed Use |
| --- | --- | --- |
| `COGNITION_PROVIDER` | `openai` | Read-only cognition evidence |
| `TRANSLATION_PROVIDER` | `openai` | UBTR translation support only if separately certified |
| `REPAIR_PROVIDER` | `openai` | Repair proposal support only if separately certified |
| `WORKER` | `openai` | Worker execution only if separately certified |

G5-01 certifies only the cognition-provider identity path. It does not certify translation-provider execution, repair-provider execution, or worker execution.

Assessment:

```text
PROVIDER_IDENTITY_BOUNDARY_ALIGNED
```

## 5. Provider Role Separation

Role separation rules:

- a cognition provider cannot be treated as a translation provider;
- a cognition provider cannot be treated as a repair provider;
- a cognition provider cannot be treated as a worker;
- a credential reference bound to one role cannot silently authorize another role;
- a provider response cannot create approval, authorization, worker handoff, mutation authority, or deployment authority;
- provider role must be recorded in replay evidence.

The first runtime implementation must fail closed when:

- provider identity is missing;
- provider role is not `COGNITION_PROVIDER`;
- credential role does not match provider role;
- provider capability claims execution authority;
- provider output claims authority;
- provider output requests mutation or worker execution.

## 6. Provider Credential Boundaries

Credential boundaries remain secret-free.

Credential evidence may record:

- credential reference id;
- credential reference;
- credential source type;
- credential presence;
- credential lifecycle state;
- operator-safe display identifier;
- retrieval boundary status.

Credential evidence must not record:

- credential value;
- credential hash;
- authorization header;
- full request authorization payload;
- provider secret material.

Credential retrieval must occur only inside the governed credential boundary and only after provider identity, role, governance, and authorization checks pass.

## 7. Provider Governance

Provider governance must evaluate:

- provider identity validity;
- provider role validity;
- credential boundary status;
- request scope;
- read-only status;
- non-mutating status;
- provider authority constraints;
- replay readiness;
- authorization status;
- output admissibility;
- post-execution review requirements.

Provider governance may record participation and usage evidence. It must not grant provider authority.

Provider governance must fail closed if the dispatch request attempts to:

- mutate repository state;
- invoke a worker;
- create approval;
- create authorization;
- deploy;
- bypass replay;
- reuse stale authorization;
- use a provider under the wrong architectural role.

## 8. Read-Only Cognition Execution Flow

Canonical future execution flow:

```text
PGSP session
-> OCS cognition execution request
-> Governance read-only execution checkpoint
-> provider identity validation
-> credential boundary validation
-> execution authorization validation
-> provider request envelope creation
-> single provider cognition dispatch
-> response or error envelope capture
-> cognition artifact creation
-> replay reconstruction
-> post-execution governance review
-> UHCL summary rendering
```

Execution output remains cognition evidence. It does not become:

- approval;
- authorization;
- worker handoff;
- mutation authority;
- deployment authority;
- governance decision.

## 9. Execution Authorization Boundaries

G5-01 does not activate approval creation.

The first runtime implementation must use a scoped execution authorization that is:

- explicit;
- replay-visible;
- bound to the PGSP session id;
- bound to provider identity;
- bound to provider role `COGNITION_PROVIDER`;
- bound to read-only cognition scope;
- one-attempt only;
- freshness-checked;
- consumed or marked attempted after use.

Authorization must not be inferred from:

- user request text;
- UHCL confirmation;
- adapter response;
- provider readiness;
- provider output;
- OCS proposal alone.

## 10. Failure Handling

The runtime must fail closed on:

- missing provider identity;
- wrong provider role;
- missing credential reference;
- missing credential at dispatch time;
- credential boundary violation;
- missing execution authorization;
- expired authorization;
- reused authorization;
- provider transport failure;
- provider timeout;
- malformed provider response;
- response containing authority claims;
- response requesting mutation;
- response requesting worker execution;
- replay write failure;
- replay reconstruction failure;
- post-execution governance review failure.

Failure evidence must be replay-visible and must not authorize retry, fallback, worker execution, or mutation.

## 11. Replay Model

The read-only cognition execution replay model must record:

1. PGSP session reference.
2. OCS cognition execution request.
3. Governance pre-dispatch checkpoint.
4. Provider identity artifact reference.
5. Credential boundary artifact reference.
6. Execution authorization artifact reference.
7. Provider request envelope.
8. Provider response or error envelope.
9. Cognition artifact.
10. Provider usage metric.
11. Cognition participation artifact.
12. Post-execution governance review.
13. UHCL execution summary.
14. Final replay reconstruction hash.

Replay must remain secret-free. Provider request and response evidence must be scrubbed or bounded so no credential or authorization secret is persisted.

## 12. Replay Reconstruction

Replay reconstruction must verify:

- artifact ordering;
- PGSP session binding;
- provider identity role;
- credential boundary status;
- authorization freshness and consumption status;
- request envelope hash;
- response or error envelope hash;
- cognition artifact hash;
- provider governance evidence;
- post-execution review evidence;
- non-mutation flags;
- non-worker flags;
- non-deployment flags.

Replay mismatch must fail closed and must mark the execution evidence inadmissible.

## 13. Post-Execution Review

Post-execution review must determine:

- whether the provider identity matched the authorized role;
- whether the dispatch remained read-only;
- whether the provider output remained non-authoritative;
- whether no worker was invoked;
- whether no repository mutation occurred;
- whether no deployment occurred;
- whether replay reconstruction passed;
- whether governance boundaries were preserved;
- whether UHCL can summarize the result to the human.

Post-execution review must not treat successful provider cognition as approval for downstream execution.

## 14. Governance Model

Governance owns the admissibility decision for the read-only cognition dispatch.

Governance must preserve:

- provider identity boundary;
- credential boundary;
- execution authorization boundary;
- replay boundary;
- worker boundary;
- mutation boundary;
- deployment boundary;
- human authority visibility.

The provider supplies cognition evidence only. Governance remains the authority boundary.

## 15. Ownership Matrix

| Concern | PGSP | OCS | Governance | Provider Service | Credential Boundary | Replay | UHCL | Adapter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Session identity | Owns | References | Checks | References | Excludes | Records | References | Displays |
| Cognition execution request | Routes | Owns proposal/request | Checks | Consumes | Excludes | Records | Explains | Excludes |
| Provider identity | Requires | References | Checks | Owns identity role | References | Records | References | Excludes |
| Credential retrieval | Excludes | Excludes | Checks | Requests through boundary | Owns | Records secret-free evidence | Excludes | Excludes |
| Provider dispatch | Excludes | Requests | Admits or blocks | Owns bounded call | Supplies secret | Records envelope | Excludes | Excludes |
| Provider output | Receives evidence | Consumes as cognition | Reviews | Produces | Excludes | Records | Summarizes | Renders |
| Approval activation | Excludes in G5-01 | Excludes | Blocks | Excludes | Excludes | Records absence | Explains | Excludes |
| Worker execution | Excludes | Excludes | Blocks | Excludes | Excludes | Records absence | Explains | Excludes |
| Repository mutation | Excludes | Excludes | Blocks | Excludes | Excludes | Records absence | Explains | Excludes |

## 16. Remaining Blockers

Remaining blockers before runtime implementation:

- PGSP execution authorization artifact shape must be selected or bound to an existing authorization artifact.
- PGSP execution replay schema must be implemented.
- Provider request and response envelope shape must be bound to PGSP session evidence.
- Post-execution review artifact must be implemented.
- UHCL execution summary rendering must be defined.
- Fail-closed response classification for authority-bearing provider output must be implemented.

These are implementation blockers, not architecture blockers.

## 17. Recommended First Runtime Implementation

Recommended implementation:

```text
G5_02_PGSP_BOUND_READ_ONLY_PROVIDER_COGNITION_RUNTIME_V1
```

Recommended runtime constraints:

- use one configured cognition-provider identity;
- require explicit pre-existing execution authorization;
- require provider role `COGNITION_PROVIDER`;
- require read-only request scope;
- dispatch at most once;
- record provider response or failure;
- record provider governance usage and participation evidence;
- reconstruct replay;
- produce post-execution review;
- render UHCL summary;
- do not mutate repositories;
- do not invoke workers;
- do not deploy;
- do not create approval.

Recommended validation:

- provider identity mismatch fails closed;
- credential missing fails closed;
- missing authorization fails closed;
- stale authorization fails closed;
- provider failure records replay-visible error;
- authority-bearing output fails closed;
- successful cognition remains non-authoritative;
- replay reconstruction validates the full path.

## 18. Certification Impact

G5-01 certifies the first execution capability architecture, not execution occurrence.

Certification impact:

- provider identity separation is preserved;
- cognition provider execution is scoped as read-only;
- worker execution remains excluded;
- repository mutation remains excluded;
- approval activation remains excluded;
- execution authorization remains required for implementation;
- replay and post-execution review are mandatory.

## 19. Rollback Impact

Rollback impact is documentation-only.

No runtime files were changed. Removing this artifact would remove the G5-01 certification design, not any execution capability.

## 20. Final Determination

Bounded read-only provider cognition execution is architecturally ready as the first Generation 5 execution capability, provided the runtime implementation enforces provider identity, credential, authorization, replay, governance, failure, and post-execution review boundaries.

Final verdict:

```text
READ_ONLY_PROVIDER_EXECUTION_READY
```
