# AIGOL Live Provider Invocation Governance V1

Status: governance specification.

Purpose: define the governance requirements for the first live provider invocation.

This artifact applies after:

```text
AIGOL_FIRST_REAL_PROVIDER_RUNTIME_IMPLEMENTATION_V1
AIGOL_FIRST_REAL_PROVIDER_RUNTIME_REGRESSION_SUITE_V1
```

It does not implement provider invocation.

It does not invoke a provider.

It does not authorize live invocation by itself.

## Governance Position

The first live provider invocation may be considered only as a governed validation event.

The live provider invocation path must preserve:

```text
Human approves.
ERR identifies metadata.
Canonical contract constrains input and output.
Adapter normalizes provider dialect.
Runtime invokes exactly one approved provider.
Provider output remains untrusted.
AiGOL governs.
Replay records.
```

ERR remains passive shared infrastructure.

Provider invocation remains outside ERR.

Provider output has no governance authority.

## Approval Requirements

Live provider invocation requires explicit approval before runtime activation.

Approval must be:

1. human-authorized;
2. replay-visible;
3. scoped to exactly one provider: `openai`;
4. scoped to exactly one capability request;
5. scoped to exactly one runtime path;
6. scoped to one validation run or one explicitly bounded batch;
7. time-bounded;
8. revocable;
9. non-transferable to other providers;
10. non-transferable to worker invocation;
11. non-transferable to future routing, fallback, ranking, or comparison.

Approval must record:

- approval artifact id;
- approver identity or governance-approved approval reference;
- provider id;
- required capability;
- runtime path;
- canonical contract version;
- replay directory;
- credential handling policy reference;
- allowed prompt/input boundary;
- allowed provider output boundary;
- expiration or run limit;
- rollback procedure reference.

Required approval output:

```text
LIVE_PROVIDER_INVOCATION_APPROVED = YES
APPROVED_PROVIDER_ID = openai
APPROVED_SCOPE = SINGLE_PROVIDER_SINGLE_RUNTIME_VALIDATION
```

Any missing approval field must fail closed.

## Replay Evidence Requirements

The live invocation must produce replay-visible evidence before, during, and after invocation.

Required pre-invocation replay evidence:

- human approval artifact;
- ERR selection artifact showing `selected_resource_id = openai`;
- canonical provider input artifact;
- adapter input artifact;
- credential policy reference without secret values;
- regression suite result showing pre-live protection passed;
- invocation boundary declaration.

Required invocation replay evidence:

- invocation attempt id;
- provider id;
- provider resource metadata hash;
- canonical input hash;
- adapter input hash;
- request timestamp;
- response timestamp or fail-closed timestamp;
- transport boundary identifier;
- no secret material;
- no raw credential material;
- no worker invocation;
- no dispatch request.

Required post-invocation replay evidence:

- canonical provider output artifact;
- adapter output artifact;
- `LLM_COGNITION_ARTIFACT_V1`;
- provider output trust classification;
- confidence representation;
- uncertainty representation;
- authority-boundary validation result;
- fail-closed result if triggered;
- replay reconstruction result;
- audit summary artifact.

Replay evidence must be immutable after creation.

Replay history must not be mutated, rewritten, compacted, or amended by the provider runtime.

## Provider Invocation Boundaries

The first live invocation boundary is:

```text
approved openai metadata
-> canonical provider input
-> OpenAI adapter
-> single live OpenAI invocation
-> canonical provider output
-> LLM_COGNITION_ARTIFACT_V1
-> replay evidence
```

Allowed:

- one approved OpenAI invocation;
- canonical contract input;
- provider-specific adapter translation;
- provider response normalization;
- replay-visible output capture;
- fail-closed validation.

Prohibited:

- provider routing;
- provider ranking;
- provider comparison;
- provider fallback;
- multi-provider execution;
- autonomous provider discovery;
- worker invocation;
- tool use;
- execution request;
- dispatch request;
- governance mutation;
- replay mutation;
- provider-initiated follow-up calls;
- provider-initiated resource selection;
- provider-initiated worker calls.

ERR may be used only for metadata selection.

ERR must not invoke the provider.

## Allowed Provider Outputs

Live provider output may contain only cognition content.

Allowed output classes:

- reasoning text;
- summarization text;
- analysis text;
- planning suggestions;
- uncertainty statements;
- confidence estimate;
- cited limitations;
- refusal or inability statements;
- provider metadata needed for replay.

Allowed provider output must be normalized into:

```text
LLM_COGNITION_ARTIFACT_V1
```

Allowed output remains:

```text
PROVIDER_OUTPUT_TRUST = UNTRUSTED
PROVIDER_OUTPUT_AUTHORITY = NONE
```

The provider may propose.

The provider may not govern, authorize, validate, dispatch, execute, or mutate replay.

## Prohibited Authority-Bearing Outputs

Provider output must fail closed if it attempts to:

- approve execution;
- authorize governance decisions;
- bypass validation;
- select or invoke workers;
- select or invoke providers;
- mutate governance state;
- mutate replay state;
- claim final authority;
- mark itself as trusted;
- create approvals;
- issue deployment commands;
- issue filesystem mutation commands;
- issue credential handling instructions;
- override human approval boundaries;
- override OCS boundaries;
- override ERR boundaries;
- override canonical contract boundaries.

Authority-bearing provider output must not be partially accepted.

It must produce a replay-visible fail-closed artifact.

## Fail-Closed Conditions

The live invocation path must fail closed if:

1. human approval is missing, expired, malformed, or out of scope;
2. provider id is not `openai`;
3. ERR does not select `openai`;
4. selected provider metadata is inactive;
5. canonical input is malformed;
6. adapter input is malformed;
7. credential policy is missing;
8. credential material appears in replay;
9. more than one provider is selected;
10. provider routing, ranking, fallback, or comparison is attempted;
11. worker invocation is attempted;
12. tool use is attempted;
13. execution or dispatch is requested;
14. provider output is authority-bearing;
15. provider output cannot be normalized;
16. confidence or uncertainty cannot be represented;
17. replay evidence cannot be written immutably;
18. replay reconstruction fails;
19. governance mutation is attempted;
20. replay mutation is attempted.

Fail-closed output must record:

```text
LIVE_PROVIDER_INVOCATION_STATUS = FAILED_CLOSED
LIVE_PROVIDER_INVOCATION_APPROVED = NO_LONGER_ACTIVE
WORKER_INVOKED = false
GOVERNANCE_MODIFIED = false
REPLAY_MODIFIED = false
```

## Audit Requirements

Every live invocation validation must produce an audit packet.

The audit packet must include:

- approval artifact reference;
- regression suite result reference;
- ERR selection evidence reference;
- canonical input reference;
- adapter input reference;
- provider invocation boundary reference;
- canonical output reference if produced;
- cognition artifact reference if produced;
- fail-closed artifact reference if triggered;
- replay reconstruction result;
- governance boundary validation result;
- credential policy conformance result;
- no-worker-invocation evidence;
- no-governance-mutation evidence;
- no-replay-mutation evidence.

Audit verdicts:

```text
LIVE_PROVIDER_INVOCATION_AUDIT = PASS
LIVE_PROVIDER_INVOCATION_AUDIT = FAIL
LIVE_PROVIDER_INVOCATION_AUDIT = FAILED_CLOSED
```

An audit failure prevents promotion from validation to any broader runtime use.

## Rollback Requirements

Rollback must be defined before approval.

Rollback must include:

1. disable live invocation path;
2. revoke approval artifact;
3. preserve replay evidence;
4. preserve fail-closed artifacts;
5. revert to deterministic mock provider response path;
6. keep ERR provider metadata intact unless the metadata caused the failure;
7. mark live invocation readiness as suspended;
8. require recertification before another live invocation.

Rollback must not delete replay evidence.

Rollback must not rewrite governance artifacts.

Rollback output:

```text
LIVE_PROVIDER_INVOCATION_ROLLED_BACK = YES
REPLAY_EVIDENCE_PRESERVED = YES
DETERMINISTIC_PROVIDER_PATH_RESTORED = YES
RECERTIFICATION_REQUIRED = YES
```

## Recertification Triggers

Recertification is required if any of the following change:

- approval model;
- ERR provider metadata;
- ERR selection evidence;
- canonical provider contract;
- OpenAI adapter;
- canonical input schema;
- canonical output schema;
- `LLM_COGNITION_ARTIFACT_V1`;
- confidence representation;
- uncertainty representation;
- replay serialization or hashing;
- provider invocation boundary;
- credential policy;
- audit packet fields;
- fail-closed rules;
- rollback procedure;
- pre-live regression suite;
- any test protecting the first real provider runtime path;
- any live invocation attempt fails closed;
- any provider output attempts authority-bearing behavior;
- any worker invocation, dispatch request, governance mutation, or replay mutation is observed.

Recertification must re-run the pre-live regression suite and produce a new governance evidence artifact.

## Acceptance Criteria

The first live provider invocation governance is acceptable only when:

1. approval model is explicit;
2. replay evidence requirements are explicit;
3. provider invocation boundaries are explicit;
4. allowed provider outputs are limited to cognition;
5. authority-bearing outputs are prohibited;
6. fail-closed conditions are enumerated;
7. audit requirements are defined;
8. rollback requirements are defined;
9. recertification triggers are defined;
10. live invocation remains single-provider and single-path;
11. ERR remains passive;
12. provider output remains untrusted;
13. workers remain unreachable from providers;
14. governance remains outside provider authority;
15. replay history remains immutable.

Acceptance output:

```text
LIVE_PROVIDER_INVOCATION_GOVERNANCE_DEFINED = YES
LIVE_PROVIDER_INVOCATION_IMPLEMENTED = NO
LIVE_PROVIDER_INVOKED = NO
LIVE_PROVIDER_INVOCATION_APPROVED_BY_THIS_ARTIFACT = NO
```

## Final Recommendation

Approve this artifact as the governance prerequisite for designing the first live OpenAI invocation.

Do not proceed to live invocation until a separate approval artifact exists and the pre-live regression suite passes immediately before the attempt.

Final status:

```text
AIGOL_LIVE_PROVIDER_INVOCATION_GOVERNANCE_V1 = PREPARED
ERR_REMAINS_PASSIVE = YES
PROVIDER_OUTPUT_AUTHORITY = NONE
LIVE_PROVIDER_INVOCATION_REQUIRES_SEPARATE_APPROVAL = YES
```
