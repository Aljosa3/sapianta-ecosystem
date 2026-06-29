# G3-04 Real Provider Activation Program V1

Status: Generation 3 implementation program.

Scope: governed real provider activation after G3-03 Product 1 certification.

This artifact does not implement runtime changes, modify tests, activate credentials, invoke
providers, invoke workers, authorize execution, mutate repositories, or deploy software.

## 1. Purpose

Platform Core Generation 2 is certified.

G3-02 ACLI Primary Development Interface is certified.

G3-03 Product 1, AI Decision Validator, is certified in deterministic, replay-visible,
non-executing scope.

G3-04 defines how AiGOL may activate real external LLM providers while preserving:

- governance authority;
- replay integrity;
- human approval boundaries;
- OCS cognition boundaries;
- Product 1 decision boundaries;
- provider ownership boundaries;
- worker execution boundaries;
- deterministic auditability.

The goal is to make ACLI usable for natural-language AiGOL development without
ChatGPT/Codex/terminal copy-paste, while ensuring provider output remains advisory and never
authoritative.

## 2. Required Invariants

G3-04 must preserve:

```text
LLM proposes.
AiGOL governs.
Human approves.
Worker executes.
Replay records.
```

Provider output is advisory only.

Provider output must not:

- become CSA semantic authority;
- override UBTR;
- override OCS cognition authority;
- approve proposals;
- authorize execution;
- invoke workers;
- mutate repositories;
- deploy;
- bypass governance;
- bypass replay;
- bypass human approval.

The same external LLM API may appear in separate architectural roles only when each role has
a distinct provider identity, credential lifecycle, replay lineage, approval boundary, and
usage policy.

## 3. Provider Activation Scope

G3-04 activates providers only for advisory cognition and conversational assistance.

Allowed provider scopes:

| Scope | Purpose | Authority |
| --- | --- | --- |
| `ACLI_CONVERSATIONAL_ASSISTANT` | Draft operator-facing responses, clarification options, and development guidance | Advisory only |
| `OCS_ADVISORY_COGNITION` | Support OCS analysis and recommendation prose | Advisory only |
| `PRODUCT1_DECISION_SUPPORT` | Assist Product 1 evidence explanation and risk analysis | Advisory only |
| `REPLAY_EXPLANATION_ASSISTANT` | Summarize existing replay evidence for humans | Advisory only |
| `PROVIDER_COMPARISON_EVALUATOR` | Compare advisory outputs across providers for difficult tasks | Advisory only |

Out of scope for G3-04:

- worker execution;
- provider-initiated repository mutation;
- autonomous task execution;
- automatic approval;
- automatic authorization;
- deployment;
- production credential rotation automation;
- external tool/broker execution.

## 4. Provider Identity Model

Provider identity must be architectural-role-specific.

Canonical provider identity fields:

- provider identity id;
- external provider family;
- model id;
- architectural role;
- credential reference id;
- credential lifecycle state;
- allowed scopes;
- prohibited scopes;
- cost policy id;
- rate-limit policy id;
- replay policy id;
- human approval requirement;
- fallback policy id;
- provider status.

Example identities:

| Provider Identity | External API | Architectural Role | Credential Lifecycle |
| --- | --- | --- | --- |
| `PROVIDER_OPENAI_ACLI_ASSISTANT_V1` | OpenAI | ACLI conversational assistant | ACLI-scoped credential |
| `PROVIDER_OPENAI_OCS_ADVISORY_V1` | OpenAI | OCS advisory cognition | OCS-scoped credential |
| `PROVIDER_OPENAI_PRODUCT1_SUPPORT_V1` | OpenAI | Product 1 decision support | Product-scoped credential |
| `PROVIDER_ANTHROPIC_OCS_ADVISORY_V1` | Anthropic | OCS advisory cognition | OCS-scoped credential |

These identities may point to the same vendor family, but they are not interchangeable.

No runtime may select a provider by vendor name alone. Selection must use provider identity,
role, scope, and credential lifecycle.

## 5. Credential And Role Separation

Credential lifecycle states:

| State | Meaning |
| --- | --- |
| `CREDENTIAL_NOT_CONFIGURED` | Provider identity exists but cannot be invoked |
| `CREDENTIAL_CONFIGURED_INACTIVE` | Credential reference exists but activation is not approved |
| `CREDENTIAL_ACTIVE_ADVISORY_ONLY` | Credential may be used only for approved advisory scopes |
| `CREDENTIAL_SUSPENDED` | Credential cannot be used until human/governance review |
| `CREDENTIAL_RETIRED` | Credential is permanently invalid for provider activation |

Credential requirements:

- credentials must never be stored in replay artifacts;
- replay records credential reference id, not secret material;
- each architectural role has a distinct credential reference;
- each credential reference has a distinct lifecycle state;
- credential use must be bound to provider identity and scope;
- credential activation requires explicit human approval evidence;
- credential suspension must fail closed and preserve replay evidence.

Role separation rules:

- ACLI provider identity cannot perform OCS advisory cognition unless separately approved;
- OCS provider identity cannot perform Product 1 decision support unless separately approved;
- Product 1 provider identity cannot authorize decisions or execute workers;
- replay explanation provider identity cannot modify replay evidence;
- comparison evaluator provider identity cannot choose final authority.

## 6. Cheapest-To-Most-Capable Escalation Policy

Provider selection should minimize cost while preserving adequacy.

Default escalation sequence:

```text
Local deterministic handling
  -> cheapest approved advisory provider
  -> stronger approved advisory provider
  -> multi-provider comparison
  -> human escalation / fail closed
```

Escalation triggers:

- low confidence;
- ambiguous provider answer;
- provider timeout;
- malformed response;
- policy mismatch;
- high-risk Product 1 decision support;
- repeated disagreement with CSA or governance evidence;
- human request for stronger review;
- replay reconstruction uncertainty.

Escalation evidence must record:

- starting provider identity;
- selected provider identity;
- escalation reason;
- prior response hash;
- next request hash;
- cost estimate;
- actual cost if available;
- rate-limit state;
- human approval reference if required;
- replay lineage.

Escalation must never grant authority to the stronger provider. Capability escalation changes
advisory quality only.

## 7. Multi-Provider Comparison Policy

Multi-provider comparison is required for difficult or high-risk advisory tasks.

Comparison triggers:

- high-impact Product 1 decision analysis;
- governance-sensitive recommendation prose;
- provider confidence below threshold;
- conflicting evidence interpretation;
- failed deterministic validation of provider output;
- operator request for independent comparison;
- OCS marks advisory uncertainty as material.

Comparison requirements:

- at least two distinct provider identities;
- distinct request hashes;
- distinct response hashes;
- normalized comparison artifact;
- agreement/disagreement summary;
- confidence comparison;
- uncertainty comparison;
- cost comparison;
- replay lineage;
- human-readable result.

Comparison result is advisory. Governance and human approval remain authoritative.

## 8. ACLI Interaction Model

ACLI becomes the primary operator interface for provider-assisted development.

ACLI may:

- request advisory provider assistance;
- show provider identity and role;
- show advisory-only status;
- show cost/rate-limit estimate;
- ask for human approval before provider use when policy requires;
- present provider response summaries;
- preserve provider request/response hashes;
- route provider output into OCS or Product 1 advisory artifacts;
- request fallback, retry, or stronger provider review.

ACLI must not:

- hide provider identity;
- hide provider cost or failure status;
- send provider output directly to workers;
- convert provider output into approval;
- mutate repositories based on provider output;
- bypass Product 1 for execution-sensitive requests.

Operator-visible provider response must include:

- provider identity;
- architectural role;
- advisory-only flag;
- request reference/hash;
- response reference/hash;
- cost/rate-limit summary;
- confidence/uncertainty;
- required next operator action;
- replay reference.

## 9. OCS Provider Invocation Path

OCS remains the cognition orchestration authority.

Provider invocation path:

```text
ACLI request or Product 1 context
  -> UBTR/CSA semantic context
  -> OCS advisory cognition request
  -> provider policy check
  -> human approval check if required
  -> provider invocation
  -> response normalization
  -> OCS advisory artifact
  -> replay evidence
  -> Product 1 or ACLI rendering
```

OCS provider invocation must record:

- OCS cognition request id;
- provider identity id;
- provider role;
- CSA reference/hash;
- request hash;
- response hash;
- normalized advisory hash;
- confidence;
- assumptions;
- risks;
- uncertainties;
- failure status if any;
- cost/rate-limit evidence;
- replay lineage.

OCS may reject provider output if it is malformed, over-authoritative, scope-violating,
non-reconstructable, missing required evidence, or inconsistent with governance boundaries.

## 10. Product 1 Provider Usage Boundary

Product 1 may consume provider-assisted advisory evidence only through OCS or approved
Product 1 decision-support provider identities.

Product 1 provider evidence may support:

- risk explanation;
- uncertainty explanation;
- recommendation prose;
- audit packet readability;
- comparison evidence;
- operator-facing summary.

Product 1 provider evidence must not:

- decide `ALLOW_READY`, `BLOCKED`, or `APPROVAL_REQUIRED` by itself;
- create approval;
- create authorization;
- invoke workers;
- mutate repositories;
- replace governance checkpoints;
- replace human review;
- replace deterministic Audit Packet assembly.

Product 1 provider usage must remain visible in Decision Packet, OCS advisory, Audit Packet,
and certification evidence.

## 11. Replay And Evidence Requirements

Every provider interaction must produce replay-visible evidence:

- provider identity id;
- architectural role;
- credential reference id;
- credential lifecycle state;
- provider request id;
- request hash;
- response hash;
- normalized response hash;
- CSA reference/hash;
- OCS cognition reference if applicable;
- Product 1 reference if applicable;
- advisory-only flag;
- human approval reference when required;
- cost estimate;
- actual cost if available;
- token/usage metadata if available;
- rate-limit state;
- timeout and retry status;
- fallback status;
- failure reason;
- replay lineage;
- rollback reference.

Replay must not store secret credential material.

Replay reconstruction must fail closed if:

- request hash is missing;
- response hash is missing;
- provider identity is unknown;
- credential lifecycle is invalid;
- advisory-only flag is missing or false;
- cost/rate-limit policy evidence is missing;
- human approval evidence is missing where required;
- normalized response cannot be reconstructed;
- provider output claims authority.

## 12. Failure And Fallback Handling

Provider failure must be visible and non-destructive.

Failure classes:

| Failure | Required Behavior |
| --- | --- |
| Provider timeout | Record timeout, retry if policy allows, otherwise fallback or fail closed |
| Rate limit | Record rate-limit state, switch provider if approved, otherwise pause |
| Cost boundary exceeded | Stop invocation and require human approval or cheaper path |
| Malformed response | Reject response, record failure, fallback or request clarification |
| Scope violation | Reject response and fail closed for that provider identity |
| Credential inactive | Do not invoke; record credential lifecycle failure |
| Provider disagreement | Trigger comparison policy or human review |
| Replay reconstruction failure | Fail closed and preserve evidence |

Fallback order:

```text
retry same provider if policy allows
  -> cheaper/same-tier approved provider
  -> stronger approved provider
  -> multi-provider comparison
  -> human review
  -> fail closed
```

No failure path may silently bypass governance or replay.

## 13. Cost And Rate-Limit Evidence

Every provider request must record cost/rate-limit metadata when available.

Required evidence:

- cost policy id;
- configured budget boundary;
- estimated cost before invocation;
- actual cost after invocation if available;
- usage units or token counts if available;
- rate-limit bucket or policy reference;
- retry count;
- escalation count;
- budget boundary status;
- human approval reference if budget threshold is exceeded.

Cost policy states:

| State | Meaning |
| --- | --- |
| `WITHIN_BUDGET` | Invocation may proceed if other gates pass |
| `NEAR_BUDGET_LIMIT` | Operator-visible warning required |
| `BUDGET_APPROVAL_REQUIRED` | Human approval required before invocation |
| `BUDGET_EXCEEDED` | Invocation fails closed |
| `COST_UNKNOWN` | Invocation requires explicit policy handling |

## 14. Human Approval Requirements

Human approval is required for:

- first activation of each provider identity;
- credential lifecycle transition to `CREDENTIAL_ACTIVE_ADVISORY_ONLY`;
- budget threshold override;
- high-risk Product 1 provider assistance;
- multi-provider comparison above configured cost threshold;
- provider fallback to a more capable or more expensive provider;
- use of provider output in operator-facing certification evidence;
- reactivation after suspension.

Approval evidence must record:

- approval request id;
- provider identity id;
- role;
- scope;
- credential reference id;
- cost/rate-limit policy;
- requested action;
- approved action;
- approval decision hash;
- human actor reference;
- replay lineage.

Approval is not execution authorization. Worker execution remains G3-05 or later.

## 15. Certification Criteria

G3-04 is ready when:

- provider identity model is implemented;
- credential lifecycle evidence is implemented;
- provider invocation path is replay-visible;
- provider output is normalized into advisory artifacts;
- OCS provider invocation is governed and fail-closed;
- ACLI can request and render provider assistance without bypassing governance;
- Product 1 can consume provider advisory evidence without authority transfer;
- cheapest-to-most-capable escalation is deterministic and replay-visible;
- multi-provider comparison is deterministic and replay-visible;
- cost/rate-limit evidence is recorded;
- human approval is enforced where required;
- provider failure and fallback paths are covered by regression tests;
- full test suite passes;
- generated replay artifacts are cleaned or intentionally packaged.

## 16. Implementation Order

Recommended G3-04 implementation sequence:

| Step | Objective |
| --- | --- |
| G3-04A | Provider identity and credential lifecycle artifacts |
| G3-04B | Provider policy gates for scope, cost, rate-limit, and approval |
| G3-04C | Advisory provider invocation substrate with replay evidence |
| G3-04D | OCS provider invocation path |
| G3-04E | ACLI provider-assisted interaction rendering |
| G3-04F | Product 1 provider advisory evidence binding |
| G3-04G | Cheapest-to-most-capable escalation |
| G3-04H | Multi-provider comparison |
| G3-04I | Failure, fallback, and rollback certification |
| G3-04J | G3-04 provider activation certification |

## 17. Dependencies On G3-05 Worker Expansion

G3-04 must complete before G3-05 worker expansion can safely use provider-assisted
development workflows.

G3-05 depends on G3-04 for:

- provider advisory evidence;
- OCS provider cognition output;
- cost and rate-limit evidence;
- provider failure classification;
- provider comparison evidence;
- ACLI provider-assisted operator workflow;
- proof that provider output cannot directly execute workers.

G3-04 must not introduce worker execution. It prepares advisory cognition and provider
evidence that G3-05 may later consume after proposal, approval, authorization, and worker
boundary certification.

## 18. Exit Criteria For G3-04

G3-04 exits when the repository contains:

- certified provider identity runtime;
- certified credential lifecycle evidence;
- certified provider invocation replay substrate;
- certified OCS provider invocation path;
- certified ACLI provider interaction model;
- certified Product 1 provider advisory boundary;
- certified escalation and comparison policies;
- certified failure and fallback behavior;
- certification document proving all G3-04 invariants.

Validation required for final G3-04 implementation certification:

```text
git diff --check
python -m py_compile ...
targeted provider activation tests
targeted OCS provider tests
targeted ACLI provider interaction tests
targeted Product 1 provider boundary tests
python -m pytest -q
```

## 19. Final Verdict

```text
G3_04_REAL_PROVIDER_ACTIVATION_PROGRAM_READY
```
