# G3-01 Product And Operational Priorities V1

Status: Generation 3 product and operational priority artifact.

Scope: measurable priorities before Generation 3 implementation begins.

This artifact does not implement runtime changes, modify tests, redefine governance, expand
authority boundaries, or authorize deployment.

## 1. Purpose

Platform Core Generation 2 is certified.

Generation 3 has been initiated, and the Generation 3 Master Execution Program is defined.
The architectural direction is stable. The next decision is priority: what the platform
must make usable, measurable, and certifiable first.

This artifact defines product and operational priorities for Generation 3 so implementation
can proceed with measurable acceptance criteria instead of broad ambition.

## 2. Primary User Personas

| Persona | Primary Need | Success Signal |
| --- | --- | --- |
| Human operator | Express intent, review evidence, approve or reject governed actions | Can complete Product 1 and development workflows without bypassing governance |
| Platform maintainer | Evolve the repository through ACLI and governed release discipline | Can produce changes, validation, replay evidence, and release packets deterministically |
| Enterprise reviewer | Inspect governance evidence and trust boundaries | Can understand why an AI execution decision was allowed, blocked, or escalated |
| Governance reviewer | Confirm constitutional, replay, approval, provider, worker, and deployment boundaries | Can audit authority preservation from evidence rather than assertion |
| Provider operator | Activate and monitor real provider usage | Can prove provider calls are advisory, bounded, replay-visible, and fail-closed |
| Worker capability owner | Add or certify worker capabilities | Can prove worker execution is scoped, approved, authorized, validated, and replayed |
| Release operator | Promote governed builds into demo/runtime environments | Can trace release from local validation to GitHub lineage to server activation |

Primary user priority:

```text
Human operator first, enterprise reviewer second, platform maintainer third.
```

This order keeps Generation 3 human-first and product-facing while preserving development
and release usability.

## 3. Primary Operational Scenarios

| Scenario | Persona | Priority | Required Evidence |
| --- | --- | --- | --- |
| Validate an AI execution decision before runtime activation | Human operator, enterprise reviewer | P0 | CSA, governance decision, approval state, validation result, replay lineage |
| Conduct a governed ACLI development session | Human operator, platform maintainer | P0 | prompt/command, clarification, proposal, approval, worker, validation, replay |
| Generate a Product 1 audit packet | Enterprise reviewer, release operator | P0 | evidence index, decision rationale, replay hashes, known limitations |
| Activate a bounded real provider call | Provider operator, governance reviewer | P1 | provider request/response metadata, cost, advisory-only status, failure behavior |
| Certify an expanded worker capability | Worker owner, governance reviewer | P1 | worker contract, authorization, result validation, failure tests, rollback evidence |
| Produce a governed release candidate | Release operator | P1 | release packet, validation results, commit lineage, rollback drill |
| Reconstruct a prior session for audit | Enterprise reviewer, governance reviewer | P1 | replay references, CSA hashes, compatibility exception status, reconstruction result |
| Rehearse server deployment and rollback | Release operator | P2 | deployment manifest, human approval, rollback proof |

Priority definitions:

- P0: required before Product 1 operational certification.
- P1: required before production release certification.
- P2: required before stable deployment certification.

## 4. Prioritized Product Roadmap

Product 1 remains the canonical product:

```text
AI Decision Validator
```

Product roadmap:

| Priority | Product Work | Acceptance Criteria |
| --- | --- | --- |
| P0 | Product 1 scenario set | Canonical scenarios cover allow, block, clarify, approve, reject, and audit paths |
| P0 | Decision validation flow | Every scenario validates proposed AI execution before runtime activation |
| P0 | Evidence-first audit view | Operator can inspect CSA, replay, governance, approval, validation, and limitation evidence |
| P0 | ACLI Product 1 operation | Product 1 scenarios can be initiated and reviewed through ACLI |
| P1 | Provider-assisted Product 1 path | Provider assistance is advisory, replay-visible, and non-authoritative |
| P1 | Worker-assisted Product 1 path | Worker execution is proposal-approved-authorized-validated-replayed |
| P1 | Enterprise demo packet | Demo packet includes scenario evidence, boundaries, limitations, and rollback notes |
| P2 | Stable demo release | Product 1 release candidate is governed, rollback-capable, and deployment-ready |

Product non-goals:

- generic chatbot positioning;
- unrestricted autonomous execution;
- perfect safety or guaranteed compliance claims;
- hidden provider or worker authority;
- deployment without governed release evidence.

## 5. ACLI Success Criteria

ACLI is the primary conversational interface for Generation 3.

ACLI success criteria:

| Criterion | Metric | Acceptance Threshold |
| --- | --- | --- |
| Clarification-first operation | Ambiguous requests produce clarification before proposal or execution | 100% of covered ambiguity fixtures |
| CSA visibility | Semantic decisions expose CSA reference/hash or explicit fallback status | 100% of semantic routing fixtures |
| Command boundary preservation | Exact commands remain deterministic and do not invoke UBTR unnecessarily | 100% of command-boundary fixtures |
| Governed development path | Repository mutation requires proposal, approval, authorization, execution, validation, replay | 100% of governed mutation fixtures |
| Failure recovery | Missing context, provider failure, worker failure, and validation failure are explainable | 100% of covered failure fixtures |
| Operator readability | User-facing output names decision, evidence, next action, and blocked reason where applicable | Certified by review artifact |
| Release handoff | ACLI can produce or reference release packet evidence after validation | Certified by release stabilization batch |

ACLI must never become an implicit bypass around governance, replay, approval, validation,
provider boundaries, worker boundaries, or deployment discipline.

## 6. Provider Activation Priorities

Provider activation is P1 because Product 1 and ACLI foundations must come first.

Provider priorities:

| Priority | Provider Capability | Acceptance Criteria |
| --- | --- | --- |
| P1 | Provider prerequisite certification | Credentials, vault, policy, metadata, and invocation constraints are verified |
| P1 | First bounded provider call | Call is explicit, replay-visible, advisory-only, and human-approved where required |
| P1 | Provider failure handling | Timeout, malformed response, refusal, unavailable provider, and cost limits fail closed |
| P1 | Provider comparison evidence | Provider output is compared against deterministic and CSA evidence without authority transfer |
| P2 | Product 1 provider use | Provider helps explain or analyze Product 1 scenario without approving or executing |
| P2 | Multi-provider readiness | Multiple providers can be compared without hardcoded authority or identity dependence |

Provider success metrics:

- zero provider paths with approval authority;
- zero provider paths with execution authority;
- zero provider paths with semantic authority over CSA;
- replay evidence for every provider invocation;
- fail-closed behavior for every covered failure mode.

## 7. Worker Ecosystem Priorities

Worker expansion is P1 and must follow ACLI and Product 1 scoping.

Worker priorities:

| Priority | Worker Capability | Acceptance Criteria |
| --- | --- | --- |
| P1 | Worker candidate inventory | First worker candidates are scoped and ranked by Product 1 and ACLI value |
| P1 | Worker contract certification | Inputs, outputs, authority denials, failure modes, and validation requirements are explicit |
| P1 | First expanded worker | One worker capability executes end to end under approval and authorization |
| P1 | Worker failure matrix | Unavailable, malformed, scope mismatch, and authority claim failures are certified |
| P2 | Repeatable onboarding | Worker onboarding process can certify new capabilities without redesign |

Initial worker priority order:

1. validation execution worker;
2. audit packet assembly worker;
3. repository inspection worker;
4. documentation generation worker;
5. Product 1 demonstration worker.

The validation worker is first because it strengthens release and Product 1 certification.
Audit packet assembly is second because it improves enterprise review and release packets.

## 8. Deployment Priorities

Deployment is P2 until release, ACLI, Product 1, provider, and worker evidence exist.

Deployment priorities:

| Priority | Deployment Work | Acceptance Criteria |
| --- | --- | --- |
| P1 | Release candidate evidence | Candidate includes validation, replay, known limitations, rollback, and commit lineage |
| P2 | Deployment boundary specification | Server activation rules and forbidden mutation paths are explicit |
| P2 | Demo server rehearsal | Deployment is sourced from governed GitHub lineage |
| P2 | Rollback rehearsal | Previous stable state can be restored with evidence preserved |
| P2 | Stable demo certification | Product 1 demo runtime is governed, bounded, and human-approved |

Deployment must preserve:

- local PC as innovation layer;
- GitHub as governed release registry;
- server as stable governed runtime;
- no uncontrolled direct server mutation;
- no autonomous deployment authority.

## 9. User Experience Priorities

Generation 3 UX should make governance understandable without weakening governance.

UX priorities:

| Priority | UX Goal | Acceptance Criteria |
| --- | --- | --- |
| P0 | Decision clarity | User can see decision status: allowed, blocked, clarify, approval required, or failed closed |
| P0 | Evidence clarity | User can inspect CSA, replay, approval, validation, provider, and worker evidence |
| P0 | Next-action clarity | User always knows the next governed action available |
| P1 | Audit readability | Enterprise reviewer can understand evidence without reading runtime internals |
| P1 | Failure readability | Fail-closed outcomes explain boundary and recovery path |
| P1 | Product narrative clarity | Product remains framed as AI Decision Validator |
| P2 | Demo polish | Enterprise demo is stable, readable, and bounded |

UX non-goals:

- hiding complexity by hiding evidence;
- claiming automatic compliance;
- making provider output look authoritative;
- making workers appear autonomous;
- presenting ACLI as an unrestricted agent.

## 10. Success Metrics

Technical metrics:

| Metric | Target |
| --- | --- |
| Full validation | Green at each runtime-affecting batch |
| Replay reconstruction | Pass for covered Product 1, ACLI, provider, worker, and release flows |
| CSA lineage coverage | Present for all semantic decisions in covered scenarios |
| Approval boundary coverage | Present before every covered execution path |
| Provider authority violations | 0 |
| Worker authority violations | 0 |
| Governance bypasses | 0 |
| Release packet completeness | 100% of required fields for release candidate |
| Rollback drill pass rate | 100% for release/deployment certification fixtures |

User-facing metrics:

| Metric | Target |
| --- | --- |
| Operator can identify decision status | 100% of Product 1 scenario outputs |
| Operator can find replay evidence | 100% of Product 1 scenario outputs |
| Operator can identify next action | 100% of ACLI covered flows |
| Enterprise reviewer can trace decision rationale | Certified by review packet |
| Provider advisory status is visible | 100% of provider-assisted outputs |
| Worker approval and authorization status is visible | 100% of worker-assisted outputs |
| Known limitations are visible | 100% of release and demo packets |

## 11. Exit Criteria By Workstream

| Workstream | Exit Criteria |
| --- | --- |
| Release stabilization | Release packet schema, evidence inventory, validation checklist, rollback drill plan, and baseline certification complete |
| ACLI conversational development | ACLI supports covered Product 1 and development flows with clarification, CSA, proposal, approval, validation, replay, and recovery evidence |
| Product 1 operationalization | AI Decision Validator scenarios are certified end to end with audit evidence and enterprise demo packet |
| Real provider activation | First bounded provider use is certified advisory-only with failure handling and replay evidence |
| Worker ecosystem expansion | First expanded worker capability and repeatable onboarding path are certified |
| Deployment readiness | Release candidate, deployment boundary, server rehearsal, rollback rehearsal, and readiness certification complete |
| Production certification | All workstream evidence consolidated with human approval and final Generation 3 certification |

## 12. Generation 3 Milestone Acceptance Criteria

| Milestone | Acceptance Criteria |
| --- | --- |
| G3-01 | Product and operational priorities approved; release stabilization can begin |
| G3-02 | Release packet and baseline stabilization certified |
| G3-03 | ACLI primary conversational interface certified |
| G3-04 | Product 1 operational workflow certified |
| G3-05 | First bounded provider activation certified |
| G3-06 | First worker expansion certified |
| G3-07 | Deployment readiness certified |
| G3-08 | Production certification complete |

The acceptance sequence intentionally front-loads product clarity and release evidence before
runtime expansion.

## 13. Recommended Implementation Order

Recommended order:

1. Product and operational priorities.
2. Release stabilization foundation.
3. ACLI primary conversational development interface.
4. Product 1 AI Decision Validator operationalization.
5. Product 1 audit UX and enterprise evidence packet.
6. First bounded real-provider activation.
7. Provider failure and comparison certification.
8. Worker ecosystem expansion batch 1.
9. Deployment readiness and rollback rehearsal.
10. Generation 3 production certification.

## 14. Governance Impact

This priority artifact has no runtime governance impact.

It preserves:

- UBTR semantic authority;
- CSA canonical representation;
- governance authority;
- approval authority;
- provider advisory boundary;
- worker execution boundary;
- replay authority;
- release discipline;
- Product 1 AI Decision Validator framing.

## 15. Final Verdict

```text
G3_01_PRODUCT_AND_OPERATIONAL_PRIORITIES_READY
```
