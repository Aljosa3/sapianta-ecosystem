# Constitutional Development Policy V1

Status: CANONICAL DEVELOPMENT GOVERNANCE SPECIFICATION

Version: V1

Authority: Development Governance

Constitutional position: L3 governed policy artifact

Compatibility baseline: G0-G44 and the accepted G45-00 through G45-04
Development Governance conclusions

## 0. Normative Interpretation

This document consolidates the accepted Constitutional-Driven Development
(CDD), Development Governance integration, deterministic classification, Need
Assessment, and Constitutional Development Policy conclusions into one
Development Governance policy.

The terms `MUST`, `MUST NOT`, `REQUIRED`, `SHALL`, `SHALL NOT`, `SHOULD`,
`SHOULD NOT`, `MAY`, and `OPTIONAL` are normative.

Text explicitly introduced as an **Informational note** is explanatory and
does not create an additional requirement.

This policy defines governance responsibilities and ordering. It does not
define a new artifact schema, constitutional protocol family, runtime engine,
or authority.

## 1. Purpose

### 1.1 Purpose

The purpose of this policy is to govern SAPIANTA development from task intake
through classification, necessity assessment, planning, approval,
authorization, implementation, validation, evidence, and certification where
applicable.

It provides one canonical answer to these questions:

1. What is this work?
2. Is this work necessary?
3. What residual work, if any, may be planned?
4. Who must review or approve it?
5. Who may authorize it?
6. How must correctness be verified?
7. What evidence must be preserved?
8. When is certification applicable?

### 1.2 Owner

Development Governance owns this policy and its application to governed
development.

Development Governance does not acquire the independent authority of the
Constitution, Human Authority, Mutation Authorization, Replay, implementation
owners, validation owners, or Certification.

### 1.3 Required Inputs

This policy requires:

- the exact human or governed development request;
- the active constitutional baseline;
- the declared scope and requested action mode;
- applicable repository and governance evidence;
- applicable ownership, certification, and supersession evidence; and
- explicit restrictions and non-goals.

### 1.4 Required Outputs

Application of this policy produces, as applicable:

- a CDD classification;
- a Need Assessment;
- a Development Governance disposition;
- a bounded implementation plan;
- required approval and authorization evidence;
- validation results;
- governance and Replay lineage evidence; and
- a certification result or an explicit determination that certification is
  not applicable.

### 1.5 Deterministic Responsibilities

The same canonical request, constitutional baseline, evidence snapshot, and
policy version MUST produce the same classification, necessity result,
governance obligations, and fail-closed outcome.

### 1.6 Fail-Closed Conditions

Policy application MUST fail closed or route to explicit review when:

- the request or scope is ambiguous;
- constitutional precedence is unresolved;
- required evidence is absent, stale, conflicting, or unverifiable;
- ownership is unresolved;
- authority impact is unclear;
- the requested work exceeds a protected boundary; or
- a later lifecycle state cannot be bound to its required upstream state.

### 1.7 Explicit Non-Responsibilities

This policy MUST NOT:

- amend the Constitution;
- alter the Stable Constitutional Substrate;
- create or modify a constitutional protocol family;
- modify PCBV31;
- approve a proposal;
- authorize mutation or execution;
- execute implementation or validation;
- mutate or reinterpret Replay;
- issue certification; or
- silently upgrade historical evidence or certification.

## 2. Scope

### 2.1 Purpose

This section defines which work is governed by this policy.

### 2.2 Owner

Development Governance owns scope classification. The constitutional owner of
each affected artifact or responsibility remains unchanged.

### 2.3 Required Inputs

Scope classification requires:

- declared objective;
- work and artifact class;
- requested repository, runtime, release, deployment, or read-only effect;
- intended target paths or responsibility surfaces where known; and
- declared exclusions.

### 2.4 Required Outputs

Scope classification MUST identify:

- whether the request is read-only or proposes mutation;
- the intended artifact class;
- the likely mutation layer or `NOT_APPLICABLE`;
- the bounded affected surface; and
- any separate release, deployment, or operational governance discipline that
  applies.

### 2.5 Deterministic Responsibilities

All SAPIANTA development work, including read-only audits, documentation,
governance evidence, runtime code, tests, product work, release work, and
architectural proposals, MUST enter through task intake and CDD
classification.

Read-only work MUST NOT bypass constitutional or protocol-impact
classification merely because it requests no repository mutation.

### 2.6 Fail-Closed Conditions

An unknown action mode, conflicting artifact class, or materially incomplete
scope MUST produce clarification, review, or a fail-closed disposition.

### 2.7 Explicit Non-Responsibilities

This policy does not replace separate release, deployment, server, domain, or
product lifecycle governance. It determines when those existing disciplines
apply.

## 3. Authority and Precedence

### 3.1 Purpose

This section preserves constitutional precedence and independent authority
boundaries.

### 3.2 Owner

The Constitution and Human Authority retain their existing highest
authorities. Development Governance interprets and applies this policy within
those constraints.

### 3.3 Required Inputs

Authority evaluation requires:

- the current constitutional architecture;
- the canonical layer classification;
- applicable freeze, mutation, approval, authorization, Replay, and
  certification constraints; and
- any domain-specific constitutional constraints.

### 3.4 Required Outputs

Authority evaluation MUST identify:

- the highest applicable authority;
- the owner of each decision or action;
- required review, approval, and authorization boundaries; and
- forbidden authority transfers.

### 3.5 Deterministic Responsibilities

When requirements conflict, this policy MUST defer to the existing
constitutional and governance enforcement precedence.

Development Governance MUST preserve:

- Constitution and Stable Constitutional Substrate authority;
- Human Authority over constitutional direction and required approvals;
- Mutation Authorization independence;
- Replay read-only and evidence-integrity ownership;
- Certification independence;
- Worker and Provider boundaries;
- interface non-authority; and
- PCBV31 boundaries.

### 3.6 Fail-Closed Conditions

Unresolved constitutional precedence, competing authority claims, or proposed
authority transfer MUST stop planning and implementation pending the required
Governance or Human review.

### 3.7 Explicit Non-Responsibilities

Development Governance MUST NOT use this policy to absorb another owner's
authority or to create a parallel approval, authorization, Replay,
certification, Worker, Provider, or execution path.

## 4. Policy Principles

The following requirements are normative:

1. The Constitution MUST be preserved before development convenience.
2. Work MUST be classified before implementation planning.
3. Necessity MUST be established before implementation planning.
4. Existing certified responsibilities MUST be reused before Platform
   expansion is proposed.
5. An existing realization MUST be completed before it is replaced.
6. An existing binding or composition MUST be preferred before a new
   capability is proposed.
7. The canonical owner MUST be extended before responsibility is duplicated.
8. Canonicalization MUST be preferred before a facade.
9. A bounded facade MUST be preferred before another runtime when a facade is
   sufficient.
10. Constitutional ownership and authority boundaries MUST be preserved.
11. Human Approval MUST NOT be treated as Mutation Authorization.
12. Planning MUST be limited to the proven residual need.
13. Architectural and mutation scope MUST be minimized.
14. Ambiguity, missing evidence, scope drift, and authority conflict MUST fail
    closed or route to explicit review.
15. Governance classification and evidence MUST remain deterministic.
16. Validation MUST match the touched surface.
17. Failed, skipped, partial, and unavailable validation MUST remain visible.
18. Certification MUST depend on complete applicable evidence.
19. Historical baselines, Replay, and prior certification semantics MUST
    remain immutable.

**Informational note:** These principles consolidate existing Development
Governance, discovery and reuse, task execution, lineage, approval,
authorization, validation, Replay, and certification requirements. They do
not create a new constitutional layer.

## 5. Development Governance Responsibilities

### 5.1 Purpose

This section defines Development Governance ownership of policy application
without transferring downstream authorities.

### 5.2 Owner

Development Governance owns:

- task-level constitutional classification;
- Need Assessment;
- ownership and duplication review;
- policy disposition;
- review and escalation routing; and
- verification that a request is eligible for implementation planning.

### 5.3 Required Inputs

Development Governance consumes:

- task intake evidence;
- CDD classification inputs;
- discovery and reuse evidence;
- ownership and certification evidence;
- known limitations;
- applicable constitutional and protocol evidence; and
- explicit Human constraints.

### 5.4 Required Outputs

Development Governance MUST produce one bounded disposition:

- complete or continue read-only assistance;
- reuse existing;
- no implementation required;
- clarification required;
- Governance or Human review required;
- bounded implementation planning permitted; or
- blocked or failed closed.

### 5.5 Deterministic Responsibilities

Development Governance MUST:

- apply CDD before Need Assessment;
- apply Need Assessment before planning;
- preserve higher authority and owner decisions;
- record unresolved limitations;
- route sensitive work to its existing owner; and
- prevent planning when classification or necessity is unresolved.

### 5.6 Fail-Closed Conditions

Development Governance MUST NOT issue planning eligibility when CDD, Need
Assessment, ownership, scope, or required evidence is incomplete or
inconsistent.

### 5.7 Explicit Non-Responsibilities

Development Governance disposition is not:

- Human Approval;
- Mutation Authorization;
- implementation;
- validation execution;
- Replay authorship;
- certification; or
- permission to expand scope.

### 5.8 Normative Responsibility Matrix

| Responsibility | Owner | Required output | Authority boundary |
|---|---|---|---|
| Task Intake | Development Governance for intake semantics; transport for capture only | Preserved request, objective, scope, and clarification state | No classification by transport |
| CDD classification | Development Governance | Deterministic work classification and obligations | No necessity, approval, or authorization decision |
| Need Assessment | Development Governance | Reuse, residual-gap, duplication, and necessity result | No implementation planning or expansion approval |
| Governance disposition | Development Governance | One bounded next-state decision | No mutation or execution permission |
| Implementation Planning | Existing certified planning owner | Exact bounded advisory plan | No approval or authorization |
| Human Approval | Human Authority through the applicable Governance surface | Exact subject-bound Human decision | Approval is not authorization |
| Mutation Authorization | Existing Authorization or Governance authorization owner | Exact bounded authorization result | Authorization creation is not mutation |
| Implementation | Existing authorized implementation owner or Worker | Exact implementation result | No self-approval, self-authorization, or self-certification |
| Validation | Existing validation and test owners | Truthful, scoped validation result | No repair, authorization, or certification |
| Evidence lineage | Each producing owner under Governance lineage requirements | Bound provenance and known limitations | Evidence presence grants no authority |
| Replay | Existing Replay owner | Immutable recording, reconstruction, or integrity verification where applicable | No classification, decision, mutation, or certification authority |
| Certification | Existing Certification owner | Scoped evidence-dependent certification result | No implementation, authorization, or Replay ownership |
| Drift and re-entry | Development Governance for reclassification; each downstream owner for its own invalidation | Re-entry point and invalidated dependent state | No preservation of stale approval, authorization, validation, or certification |

## 6. Canonical Development Lifecycle

The canonical lifecycle is:

```text
Human Request
      |
      v
Task Intake
      |
      v
Development Governance
      |
      +--> CDD Classification
      |          |
      |          v
      +--> Need Assessment
      |          |
      |          v
      `--> Governance Disposition
                 |
                 +--> read-only result --------------------------> terminate
                 |
                 +--> no implementation / reuse ----------------> terminate
                 |
                 +--> clarification or review ------------------> re-enter
                 |
                 +--> blocked / failed closed ------------------> terminate
                 |
                 `--> proven residual change
                              |
                              v
                    Implementation Planning
                              |
                              v
                    Human Approval, where required
                              |
                              v
                    Mutation Authorization, where required
                              |
                              v
                    Implementation
                              |
                              v
                    Validation
                              |
                  +-----------+-----------+
                  |                       |
               failed                  passing
                  |                       |
                  v                       v
          block / diagnose /       evidence complete
          reclassify or replan              |
                                           v
                                Certification, where applicable
                                           |
                                           v
                                  governed completion
```

Evidence lineage MUST begin at intake and continue through every applicable
stage. Replay MUST record or verify only the evidence for which an existing
Replay contract applies.

Not every request reaches planning, approval, authorization, implementation,
Replay, or certification. The active stage and termination reason MUST remain
explicit.

## 7. Task Intake

### 7.1 Purpose

Task Intake establishes the exact objective and bounded initial context for
CDD.

### 7.2 Owner

Development Governance owns constitutional intake semantics. A Human
Interface, AiCLI, Codex, or another transport MAY capture the request but MUST
NOT decide its constitutional classification.

### 7.3 Required Inputs

- exact request;
- requesting actor or source where required;
- requested action mode;
- declared artifacts or outcomes;
- declared constraints; and
- active baseline reference.

### 7.4 Required Outputs

- preserved request identity;
- declared objective;
- intended artifact and work class candidates;
- bounded initial scope;
- explicit constraints and non-goals; and
- clarification requirements.

### 7.5 Deterministic Responsibilities

Task Intake MUST preserve the request without silently broadening,
reinterpreting, or converting read-only work into implementation work.

### 7.6 Fail-Closed Conditions

Material ambiguity about governance, runtime, deployment, irreversible
behavior, or constitutional meaning MUST result in clarification or review.

### 7.7 Explicit Non-Responsibilities

Task Intake MUST NOT approve, authorize, plan, execute, or certify work.

## 8. Constitutional-Driven Development Classification

### 8.1 Purpose

CDD answers: `What is this work?`

### 8.2 Owner

Development Governance owns CDD classification.

### 8.3 Required Inputs

- valid task intake;
- exact objective and scope;
- constitutional baseline and evidence snapshot;
- known protocol, realization, capability, and ownership evidence; and
- declared action mode.

### 8.4 Required Outputs

CDD MUST identify:

- procedure version;
- input and baseline identity;
- action mode;
- primary work class and secondary impacts;
- mutation layer or `NOT_APPLICABLE`;
- constitutional impact;
- protocol impact;
- realization category and impact;
- capability impact;
- authority impact;
- owner;
- affected scope;
- required review and explicit prohibitions;
- unresolved fields; and
- deterministic termination state.

### 8.5 Deterministic Responsibilities

CDD MUST evaluate, in order:

1. input and baseline validity;
2. scope and artifact identity;
3. action mode;
4. constitutional and authority impact;
5. protocol impact;
6. realization impact;
7. capability impact;
8. implementation category;
9. mutation layer and ownership;
10. applicable drift; and
11. downstream governance obligations.

Where multiple proven impacts coexist, the primary work class MUST follow
this precedence:

```text
constitutional
> protocol
> realization
> capability
> implementation category
> implementation-only
```

Precedence MUST NOT be used to guess between ambiguous meanings.

### 8.6 Fail-Closed Conditions

CDD MUST return clarification, review, blocked, or failed-closed status when:

- intent or scope is ambiguous;
- baseline or evidence identity is missing;
- constitutional precedence is unresolved;
- protocol, owner, or authority impact cannot be established; or
- protected-layer impact is unknown.

### 8.7 Explicit Non-Responsibilities

CDD MUST NOT:

- decide whether implementation is necessary;
- construct an implementation plan;
- approve or authorize work;
- mutate the repository;
- change a protocol or realization;
- infer missing constitutional meaning; or
- certify its own classification.

## 9. Need Assessment

### 9.1 Purpose

Need Assessment answers: `What work, if any, remains necessary?`

### 9.2 Owner

Development Governance owns the assessment. Existing protocol, realization,
capability, domain, adapter, Worker, Provider, interface, Governance, Replay,
and Certification owners remain authoritative for their own evidence.

### 9.3 Required Inputs

- completed CDD classification;
- neutral objective and acceptance conditions;
- current evidence snapshot;
- protocol and realization evidence;
- capability registry and composition evidence;
- ownership and certification evidence;
- implementation history;
- existing API, adapter, Worker, Provider, domain, and binding evidence where
  applicable; and
- known limitations and supersession state.

### 9.4 Required Outputs

Need Assessment MUST produce one of:

- `NO_IMPLEMENTATION_REQUIRED`;
- `REUSE_EXISTING_UNCHANGED`;
- `CANONICALIZATION_ONLY`;
- `COMPLETE_EXISTING_REALIZATION`;
- `IMPLEMENT_EXISTING_BINDING`;
- `EXTEND_EXISTING_OWNER`;
- `COMPOSE_EXISTING_CAPABILITIES`;
- `NEW_REALIZATION_JUSTIFIED`;
- `NEW_DISTINCT_CAPABILITY_JUSTIFIED`;
- `ARCHITECTURAL_DUPLICATION`;
- `UNJUSTIFIED_EXPANSION`;
- `GOVERNANCE_REVIEW_REQUIRED`; or
- `FAILED_CLOSED`.

The output MUST identify:

- covered objective facets;
- certified and non-superseded reusable owners;
- residual gaps;
- duplication and ownership risks;
- the smallest justified change class;
- governance and Replay impact; and
- the evidence basis for the result.

### 9.5 Deterministic Responsibilities

Need Assessment MUST:

1. validate the CDD result and shared baseline;
2. state the objective in neutral Platform terms;
3. decompose the objective into bounded facets;
4. inspect existing protocols, realizations, capabilities, compositions,
   domains, adapters, Workers, Providers, interfaces, Governance artifacts,
   implementation history, APIs, and bindings as applicable;
5. verify ownership, certification, supersession, compatibility, and evidence;
6. build objective-to-coverage results;
7. identify residual gaps;
8. distinguish naming, API, binding, completion, composition, extension,
   realization, and genuinely new capability needs;
9. detect duplication and ownership drift; and
10. prove expansion necessity before recommending new architecture.

An uncovered registry or knowledge entry MUST NOT by itself prove that a new
capability is necessary.

### 9.6 Fail-Closed Conditions

Need Assessment MUST fail closed or require Governance review when:

- CDD evidence is invalid;
- the baseline or evidence snapshot differs from CDD;
- capability coverage is ambiguous;
- an existing owner's completeness cannot be established;
- semantic duplication cannot be resolved;
- expansion criteria are unproven; or
- authority or ownership would drift.

### 9.7 Explicit Non-Responsibilities

Need Assessment MUST NOT:

- redefine the CDD work class;
- create a new owner;
- treat novelty as necessity;
- create a protocol or capability;
- prepare implementation details;
- approve expansion;
- authorize mutation; or
- execute a recommendation.

## 10. Development Governance Disposition

### 10.1 Purpose

Disposition determines the next constitutional development state after CDD
and Need Assessment.

### 10.2 Owner

Development Governance owns the disposition.

### 10.3 Required Inputs

- completed CDD classification;
- completed Need Assessment;
- applicable Governance and Human review results; and
- exact shared scope and baseline.

### 10.4 Required Outputs

Disposition MUST select exactly one:

- read-only work may continue;
- no implementation is required;
- existing capability, realization, composition, or binding must be reused;
- clarification is required;
- Governance or Human review is required;
- bounded planning of the identified residual gap is permitted;
- work is blocked; or
- policy application failed closed.

### 10.5 Deterministic Responsibilities

Disposition MUST preserve the strictest applicable upstream restriction and
MUST bind planning eligibility to the exact classified residual gap.

### 10.6 Fail-Closed Conditions

Conflicting CDD and Need Assessment scope, unresolved review, missing evidence,
or a prohibited outcome MUST prevent planning eligibility.

### 10.7 Explicit Non-Responsibilities

Disposition MUST NOT be interpreted as approval, authorization,
implementation instruction, execution permission, or certification.

## 11. Implementation Planning

### 11.1 Purpose

Implementation Planning answers: `How may the proven residual need be
implemented within existing constitutional boundaries?`

### 11.2 Owner

The applicable certified planning owner or bounded Platform planning
capability owns plan construction. Development Governance owns plan
admissibility review.

### 11.3 Required Inputs

- planning-eligible Governance disposition;
- exact residual gap;
- canonical owners and dependencies;
- applicable compatibility and historical baseline requirements;
- validation requirements;
- evidence, Replay, and certification expectations; and
- explicit prohibitions.

### 11.4 Required Outputs

A plan MUST identify:

- exact objective and residual gap;
- affected artifacts and owners;
- bounded operations;
- dependency and implementation order;
- compatibility requirements;
- authority and approval boundaries;
- validation scope;
- evidence and Replay expectations;
- certification expectation;
- known risks and limitations; and
- non-goals and prohibited changes.

### 11.5 Deterministic Responsibilities

Planning MUST:

- address only the proven residual gap;
- prefer reuse, binding, completion, composition, and extension before new
  architecture;
- preserve a runnable or reconstructable system at defined checkpoints where
  the applicable implementation class requires it;
- preserve historical compatibility;
- separate planning from mutation; and
- derive validation and evidence obligations from the touched surface.

### 11.6 Fail-Closed Conditions

Planning MUST stop and return to CDD or Need Assessment when:

- scope expands;
- owner or work class changes;
- a new constitutional or protocol impact appears;
- required evidence changes materially;
- the plan contradicts an upstream prohibition; or
- the plan cannot bind its exact artifacts and operations.

### 11.7 Explicit Non-Responsibilities

A plan MUST NOT:

- approve itself;
- authorize mutation;
- dispatch a Worker or Provider;
- execute validation;
- issue certification; or
- conceal unresolved risks or gaps.

## 12. Human Approval

### 12.1 Purpose

Human Approval records an explicit Human decision on the exact proposal or
plan where approval is constitutionally or operationally required.

### 12.2 Owner

Human Authority owns the decision. The applicable Governance approval service
MAY record and validate its evidence.

### 12.3 Required Inputs

- exact proposal or plan identity and hash where the applicable contract uses
  hashes;
- scope and intended effects;
- material risks, alternatives, and prohibitions;
- required evidence; and
- Human actor evidence where required.

### 12.4 Required Outputs

- explicit approval, rejection, or request for clarification/modification;
- exact approved subject and scope;
- decision identity and evidence; and
- any Human constraints.

### 12.5 Deterministic Responsibilities

Approval evidence MUST bind to the exact reviewed subject. Approval absence
MUST NOT be interpreted as approval.

Approval is REQUIRED where existing governance requires it, including
constitutional, structural, destructive, broad-scope, deployment, release,
stable-runtime, or otherwise sensitive changes.

### 12.6 Fail-Closed Conditions

Missing, stale, substituted, ambiguous, rejected, or scope-mismatched approval
MUST block downstream authorization where approval is required.

### 12.7 Explicit Non-Responsibilities

Human Approval MUST NOT be treated as:

- Mutation Authorization;
- Worker or Provider invocation;
- implementation;
- validation;
- Replay mutation; or
- certification.

## 13. Mutation Authorization

### 13.1 Purpose

Mutation Authorization determines whether an exact approved mutation may
proceed within a bounded scope.

### 13.2 Owner

The existing Authorization or Governance authorization owner retains this
responsibility.

### 13.3 Required Inputs

- exact approved proposal or plan where approval is required;
- approval lineage;
- target artifacts and operations;
- applicable hashes, preconditions, permissions, freshness, expiration,
  revocation, and consumption policy;
- validation or readiness evidence required by the applicable contract; and
- forbidden operations.

### 13.4 Required Outputs

- a separately derived authorization result;
- exact authorized scope and operation;
- authorization identity and lineage;
- validity, expiration, revocation, and consumption constraints; and
- explicit forbidden operations.

### 13.5 Deterministic Responsibilities

Authorization scope MUST NOT exceed approved scope. Authorization MUST be
separately derived, bounded, freshness-checked, revocable where the applicable
contract requires it, and Replay-bound where the applicable authorization
contract requires Replay evidence.

### 13.6 Fail-Closed Conditions

Authorization MUST fail closed when:

- required approval is missing or invalid;
- scope exceeds the approved plan;
- target, operation, or evidence is substituted;
- authorization is expired, revoked, or already consumed;
- required readiness or lineage evidence is missing; or
- a forbidden operation is requested.

### 13.7 Explicit Non-Responsibilities

Authorization creation MUST NOT:

- perform the mutation;
- invoke a Worker or Provider unless a separate certified consumption path
  authorizes that action;
- expand Human-approved scope;
- repair missing evidence; or
- issue certification.

## 14. Implementation

### 14.1 Purpose

Implementation performs the exact approved and authorized development work.

### 14.2 Owner

The existing implementation owner, bounded development actor, or certified
Worker owns implementation within the applicable contract.

### 14.3 Required Inputs

- exact plan;
- applicable Human Approval;
- applicable Mutation Authorization;
- current preconditions and source state;
- bounded target scope; and
- required implementation constraints.

### 14.4 Required Outputs

- exact changed or generated artifacts;
- implementation result and status;
- affected paths;
- preserved provenance;
- known limitations; and
- inputs required for validation.

### 14.5 Deterministic Responsibilities

Implementation MUST:

- remain inside the exact authorized scope;
- preserve ownership and authority boundaries;
- avoid unrelated mutation;
- preserve historical evidence;
- report partial or failed work truthfully; and
- stop when a precondition or scope binding no longer holds.

### 14.6 Fail-Closed Conditions

Implementation MUST stop when authorization, source state, target identity,
scope, ownership, or protected-boundary checks fail.

### 14.7 Explicit Non-Responsibilities

An implementation owner MUST NOT:

- self-approve;
- self-authorize;
- broaden the plan;
- rewrite historical Replay or certification;
- declare validation passing without validation evidence; or
- certify its own work.

## 15. Validation

### 15.1 Purpose

Validation determines whether the implemented work satisfies its exact
requirements and preserves applicable constitutional and compatibility
constraints.

### 15.2 Owner

Existing test, validation, conformance, and domain-validation owners retain
their responsibilities. A validation Worker, where used, owns only the
certified validation execution boundary.

### 15.3 Required Inputs

- exact implementation result;
- planned validation scope;
- touched artifacts and behavior;
- applicable constitutional, governance, Replay, compatibility, and domain
  requirements; and
- exact validation commands or procedures allowed by the applicable contract.

### 15.4 Required Outputs

- validation procedures executed;
- passing, failing, skipped, or unavailable results;
- bounded stdout, stderr, exit status, hashes, or reports where applicable;
- scope coverage;
- known gaps; and
- readiness or failure disposition.

### 15.5 Deterministic Responsibilities

Validation MUST:

- match the touched surface;
- preserve deterministic and fail-closed reporting;
- keep failures, skips, missing dependencies, and known conformance gaps
  visible;
- distinguish targeted validation from broader regression; and
- avoid presenting partial validation as complete.

### 15.6 Fail-Closed Conditions

Failed required validation, insufficient coverage, invalid evidence, or
unavailable required dependencies MUST block completion or certification.

### 15.7 Explicit Non-Responsibilities

Validation MUST NOT:

- authorize implementation;
- mutate production or governance state outside an explicitly certified
  validation contract;
- repair failures automatically;
- rewrite expected behavior; or
- issue certification.

## 16. Evidence and Replay Relationship

### 16.1 Purpose

This section preserves governance provenance and Replay independence across
the lifecycle.

### 16.2 Owner

Each lifecycle owner produces its own evidence. Governance owns lineage
requirements. Replay owns read-only recording, reconstruction, and integrity
verification under existing Replay contracts.

### 16.3 Required Inputs

- lifecycle artifacts and decisions;
- exact identities, hashes, scope, and owner evidence where applicable;
- validation results;
- prior lineage; and
- applicable Replay contract.

### 16.4 Required Outputs

Evidence MUST preserve, as applicable:

- task and baseline identity;
- CDD and Need Assessment results;
- Governance disposition;
- plan and scope;
- Human Approval;
- Mutation Authorization;
- implementation result;
- validation status;
- known gaps;
- Replay references and verification; and
- certification status.

### 16.5 Deterministic Responsibilities

Evidence lineage MUST:

- identify what changed;
- identify the affected layer and owner;
- identify which gates applied;
- preserve scope and validation status;
- preserve known limitations;
- distinguish documentation-only, runtime-enforced, and domain-scoped
  evidence; and
- remain stable and reconstructable where Replay applies.

Replay MUST observe, record, reconstruct, or verify only according to existing
Replay ownership and contracts. Replay MUST NOT create authoritative history
or decide classification, necessity, approval, authorization, implementation,
or certification.

### 16.6 Fail-Closed Conditions

Missing, reordered, substituted, divergent, stale, or unverifiable required
evidence MUST reduce authority or block the dependent lifecycle transition.
Replay divergence MUST fail closed.

### 16.7 Explicit Non-Responsibilities

This policy MUST NOT:

- require Replay for a stage where no existing Replay contract applies;
- modify a Replay protocol or historical record;
- treat evidence presence as approval or authorization; or
- synthesize missing certification evidence.

## 17. Certification Relationship

### 17.1 Purpose

Certification determines whether an applicable artifact or development result
has satisfied its independent certification requirements.

### 17.2 Owner

Existing Certification owners retain certification authority.

### 17.3 Required Inputs

- exact artifact and identity;
- applicable Governance and mutation evidence;
- required validation and strict test evidence;
- Replay verification where required;
- approval and authorization evidence where applicable;
- compatibility and supersession evidence; and
- explicit known limitations.

### 17.4 Required Outputs

- certified, rejected, incomplete, or otherwise contract-defined
  certification result;
- certification scope;
- evidence references;
- compatibility and supersession status; and
- certification identity or record where the applicable contract defines one.

### 17.5 Deterministic Responsibilities

Certification MUST:

- remain separate from implementation and validation;
- consume only applicable verified evidence;
- preserve exact scope;
- preserve historical certification;
- avoid silent inheritance or upgrade; and
- remain conditional rather than mandatory for artifact classes that do not
  require certification.

### 17.6 Fail-Closed Conditions

Missing artifact type, evidence, validation, Replay verification, ownership,
or required approval/authorization MUST produce rejection, incompleteness, or
another fail-closed certification outcome under the applicable contract.

### 17.7 Explicit Non-Responsibilities

Certification MUST NOT:

- authorize mutation or execution;
- modify Replay;
- repair implementation;
- broaden certified scope; or
- retroactively change historical certification.

## 18. Drift and Re-entry Policy

### 18.1 Purpose

This section preserves continuity when a request or its evidence changes.

### 18.2 Owner

Development Governance owns reclassification requirements. Each downstream
owner remains responsible for invalidating or rejecting evidence that no
longer binds to its upstream state.

### 18.3 Required Inputs

- prior lifecycle state;
- proposed or observed change;
- prior and current scope;
- prior and current baseline/evidence identity; and
- applicable approval and authorization bindings.

### 18.4 Required Outputs

- unchanged-state confirmation;
- required re-entry point;
- invalidated downstream states;
- required review or clarification; or
- fail-closed termination.

### 18.5 Deterministic Responsibilities

CDD and Need Assessment MUST be repeated when any of these changes materially:

- objective;
- action mode;
- artifact or work class;
- constitutional or protocol impact;
- realization or capability classification;
- owner;
- mutation layer;
- scope, target, or operation;
- authority requirement;
- baseline or certification state;
- Replay impact; or
- implementation effect.

Planning MUST be repeated when the residual gap or implementation scope
changes.

Approval MUST be repeated when its reviewed subject changes.

Authorization MUST be re-derived when authorized scope, target, operation,
precondition, hash, freshness, lineage, or consumption state changes.

Validation MUST be repeated when implementation changes invalidate prior
coverage.

Certification MUST be re-evaluated when any required underlying evidence
changes.

### 18.6 Fail-Closed Conditions

Scope drift, ownership drift, authority drift, constitutional drift, protocol
drift, realization drift, capability inflation, protocol inflation,
certification drift, Replay-impact drift, validation drift, or evidence drift
MUST invalidate dependent continuation until the correct re-entry procedure
completes.

### 18.7 Explicit Non-Responsibilities

Re-entry MUST NOT:

- rewrite prior evidence;
- preserve stale approval or authorization;
- silently widen scope;
- infer Human acceptance; or
- bypass an earlier failed-closed result.

## 19. Non-Goals and Explicit Exclusions

This policy does not:

- create a Constitutional Development Protocol;
- create a new constitutional layer;
- create a new Governance authority;
- modify the Constitution or Stable Constitutional Substrate;
- modify PCBV31 or make it a Development Governance classifier;
- modify protocol families;
- create a universal runtime orchestrator;
- replace capability selection or composition;
- replace existing planning capabilities;
- replace Human Approval;
- replace Mutation Authorization;
- replace implementation, Worker, Provider, or adapter owners;
- replace validation or IVE;
- replace Replay;
- replace Certification;
- authorize repository mutation, execution, deployment, release, retry, or
  fallback;
- require every task to reach implementation or certification;
- hide partial conformance or known enforcement gaps; or
- permit autonomous constitutional mutation or self-certification.

## 20. Relationship to Existing Governance Artifacts

This policy references and consolidates application of existing authority. It
does not replace the following artifacts:

| Existing artifact | Relationship to this policy |
|---|---|
| `docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md` | Defines the distributed Constitution, layer taxonomy, authority model, and constitutional invariants. This policy is subordinate. |
| `docs/governance/STABLE_SUBSTRATE_DECLARATION_V1.md` | Defines the stable constitutional substrate and preservation requirements. This policy builds on it. |
| `docs/governance/CANONICAL_LAYER_MODEL.md` | Defines L0-L4 mutation layers and the separate safety authority model. This policy uses but does not reinterpret them. |
| `docs/governance/CONSTITUTIONAL_INVARIANTS.md` | Defines Replay, layer, fail-closed, determinism, certification, and execution-boundary invariants. This policy applies them. |
| `docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md` | Defines enforcement precedence and existing gate responsibilities. This policy does not change their order or authority. |
| `docs/governance/GOVERNANCE_LINEAGE_MODEL.md` | Defines mutation provenance, Replay lineage, certification inheritance, and evidence classes. This policy uses that lineage model. |
| `docs/governance/G6_05_PLATFORM_CAPABILITY_DISCOVERY_AND_REUSE_POLICY_V1.md` | Defines mandatory discovery, reuse, ownership verification, duplication checks, and minimal extension. Need Assessment consumes these requirements. |
| `docs/governance/G20_04_PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_AUDIT.md` | Establishes reusable deterministic planning inputs and residual-gap ordering. Planning remains advisory and separately owned. |
| `docs/governance/G5_06_HUMAN_APPROVAL_TO_EXECUTION_AUTHORIZATION_ALIGNMENT_V1.md` | Defines approval-to-authorization separation and continuity. This policy preserves it. |
| `docs/governance/CODEX_TASK_EXECUTION_PROTOCOL_V1.md` | Defines Codex intake, scope, validation, approval, escalation, and lineage discipline. Codex remains a bounded development actor. |
| `docs/governance/G8_13_GOVERNED_VALIDATION_EXECUTION_SPECIFICATION_V1.md` | Defines a bounded validation execution contract. This policy does not broaden validation execution. |
| `docs/governance/GOVERNANCE_CONFORMANCE_SYSTEM_V1.md` | Defines read-only constitutional conformance verification and known enforcement limitations. This policy does not claim full enforcement. |
| `docs/governance/G42_01_CONSTITUTIONAL_DEVELOPMENT_WORKFLOW_INTEGRATION.md` | Defines certified validation-planning workflow integration and preserves non-authority. |
| `docs/governance/G43_01_CONSTITUTIONAL_DEVELOPMENT_SUPERVISOR.md` | Defines read-only earliest-blocker diagnosis and minimal repair recommendations. It supports failure handling without becoming this policy's owner. |
| `docs/governance/G44_01_CONSTITUTIONAL_DEVELOPMENT_CONTINUITY_MANAGER.md` | Defines checkpoint, resume, and continuity verification without mutation or authorization authority. |

The accepted Generation 45 Development Governance decision lineage is:

- G45-00 — Constitutional-Driven Development Methodology Audit;
- G45-01 — Constitutional Development Governance Integration Review;
- G45-02 — Constitutional-Driven Development Decision Procedure Audit;
- G45-03 — Constitutional Need Assessment Audit; and
- G45-04 — Constitutional Development Policy Consolidation Audit.

This document is the canonical consolidation of those accepted conclusions.
It does not retroactively edit their reasoning or the G0-G44 baseline.

## 21. Versioning Policy

### 21.1 V1 Identity

V1 records the Development Governance policy derived from G0-G44 and the
accepted G45-00 through G45-04 conclusions.

### 21.2 Historical Immutability

Once governed and accepted, the semantic meaning of V1 MUST remain
historically stable. Prior policy evidence MUST NOT be rewritten to imply a
later rule.

### 21.3 New Version Requirement

A new version is REQUIRED for a semantic change to:

- lifecycle ordering;
- mandatory classification or Need Assessment;
- ownership;
- authority;
- approval or authorization separation;
- fail-closed behavior;
- evidence or Replay responsibilities;
- certification dependencies; or
- historical compatibility rules.

### 21.4 Higher-Authority Change

A proposed constitutional or protocol change MUST complete its own applicable
review and authorization before a later Development Policy version may
reference the accepted change.

### 21.5 Non-Semantic Maintenance

Non-semantic corrections MAY clarify wording or repair references only through
governed repository history. They MUST NOT silently change normative meaning.

### 21.6 Explicit Non-Responsibilities

Versioning this policy MUST NOT:

- amend the Constitution;
- modify a protocol family;
- change PCBV31;
- mutate Replay history;
- alter prior Authorization;
- upgrade prior Certification; or
- activate runtime enforcement.

## 22. Compliance Statement

A development workflow conforms to this policy only when:

- it enters through bounded task intake;
- CDD classification completes before planning;
- Need Assessment completes before planning;
- Development Governance issues a valid disposition;
- planning addresses only a proven residual need;
- required Human Approval remains distinct from Mutation Authorization;
- implementation remains inside exact applicable scope;
- validation truthfully covers the touched surface;
- evidence and Replay boundaries remain intact;
- certification occurs only where applicable and evidence-complete;
- drift triggers the required re-entry; and
- known limitations and partial conformance remain visible.

Conformance with this policy does not by itself prove full runtime enforcement,
grant authority, or certify an implementation.

## 23. Minimal Conclusion

Constitutional development is not implementation-first.

It is:

```text
classify
-> establish necessity
-> govern the residual need
-> plan
-> approve where required
-> authorize separately
-> implement within scope
-> validate
-> preserve evidence
-> certify where applicable
```

This policy consolidates that existing Development Governance model without
changing constitutional meaning, authority, protocol, runtime, Replay, or
certification.
