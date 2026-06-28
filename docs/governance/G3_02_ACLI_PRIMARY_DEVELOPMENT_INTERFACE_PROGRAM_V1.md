# G3-02 ACLI Primary Development Interface Program V1

Status: Generation 3 ACLI primary development interface execution program.

Scope: pre-implementation program for transforming ACLI into the primary human-first
development interface.

This artifact does not implement runtime changes, modify tests, authorize repository
mutation, invoke providers, invoke workers, or change governance authority.

## 1. Purpose

Platform Core Generation 2 is certified.

Generation 3 planning artifacts are complete:

- Generation 3 Initiation.
- Generation 3 Master Execution Program.
- Product and Operational Priorities.
- Release Stabilization Program.

G3-02 defines the implementation program for ACLI as the primary human-first development
interface for AiGOL. The program preserves the certified Generation 2 boundaries:

- deterministic commands remain command-parser authority;
- UBTR and CSA remain semantic authority;
- HIRR remains clarification lifecycle authority;
- approval remains explicit human or governed approval authority;
- providers remain advisory;
- workers execute only after proposal, approval, authorization, and validation;
- replay remains the evidence source of truth.

## 2. Target User Experience

Target experience:

```text
Human expresses intent in natural language or command.
ACLI clarifies ambiguity.
ACLI shows semantic and lifecycle evidence.
ACLI proposes governed next actions.
Human confirms or rejects.
ACLI invokes only certified governed workflows.
Replay records every decision and boundary.
```

User-facing principles:

| Principle | Required Behavior |
| --- | --- |
| Human-first | User can use ordinary language without knowing internal workflow names |
| Clarification-first | Ambiguous, incomplete, contradictory, or unsafe requests clarify or fail closed |
| Evidence-visible | User can see decision status, CSA lineage, replay reference, and next action |
| Confirmation-bound | Action cannot proceed from vague agreement or inferred consent |
| Development-safe | Repository mutation requires proposal, approval, authorization, validation, and replay |
| Product-aware | Product 1 AI Decision Validator scenarios are supported without product framing drift |
| Recovery-oriented | Failures explain what happened, what is blocked, and what governed action is available |

ACLI should feel conversational, but it must not behave as an unrestricted autonomous agent.

## 3. ACLI Interaction Model

ACLI interaction model:

```text
Input
  -> command boundary check
  -> UBTR/CSA semantic lineage when natural language is present
  -> HIRR clarification lifecycle
  -> workflow candidate selection
  -> evidence-visible response
  -> human confirmation when action is possible
  -> proposal and approval path
  -> authorization
  -> worker execution only when certified
  -> validation
  -> replay and release evidence handoff
```

Interaction modes:

| Mode | Description | Authority Rule |
| --- | --- | --- |
| Exact command | Deterministic command parser match | Command parser authoritative |
| Natural-language request | Human prose requiring semantic interpretation | UBTR/CSA authoritative |
| Clarification turn | Reply to active clarification | HIRR lifecycle authoritative; UBTR supplies semantics |
| Advisory conversation | Planning, review, explanation, or recommendation | No approval or execution |
| Governed development | Repository-affecting work | Requires proposal, approval, authorization, validation, replay |
| Product 1 operation | AI Decision Validator workflow | Requires Product 1 evidence model |
| Release handoff | Validation and release evidence packaging | Requires G3-01 release packet rules |

## 4. Conversational Development Workflow

Primary workflow:

1. Capture user prompt or command.
2. Apply deterministic command boundary.
3. For natural-language input, generate or consume CSA semantic lineage.
4. Apply HIRR lifecycle checks and clarification-first rules.
5. Classify request as advisory, Product 1, governed development, release support, provider
   eligible, worker eligible, or unsupported.
6. If ambiguity remains, ask one or more bounded clarification questions.
7. If action is possible, present a proposal summary and required evidence.
8. Require explicit human confirmation or approval.
9. Persist proposal, approval, authorization, mutation or worker request, validation, and
   replay evidence in order.
10. Present result, validation state, replay reference, release packet impact, and next
    governed action.

Development workflow states:

```text
SESSION_STARTED
INPUT_CAPTURED
COMMAND_OR_SEMANTIC_SOURCE_RESOLVED
CLARIFICATION_OPEN
CLARIFICATION_RESOLVED
WORKFLOW_CANDIDATE_SELECTED
PROPOSAL_PREPARED
HUMAN_CONFIRMATION_REQUIRED
APPROVAL_RECORDED
AUTHORIZATION_RECORDED
WORKER_OR_MUTATION_EXECUTED
VALIDATION_RECORDED
REPLAY_LINKED
SESSION_COMPLETED
FAILED_CLOSED
```

No state may skip required upstream evidence.

## 5. Human Confirmation Model

Human confirmation is intentionally stricter than ordinary conversation.

Confirmation classes:

| Class | Meaning | Required Handling |
| --- | --- | --- |
| Clarification response | User narrows ambiguity | Bind to active clarification; not approval |
| Advisory confirmation | User agrees with recommendation or explanation | Does not authorize mutation or execution |
| Proposal approval | User explicitly approves a named proposal and scope | Can enable authorization if fresh and in scope |
| Release approval | User approves release candidate promotion | Requires release packet evidence |
| Deployment approval | User approves demo/server activation | Requires deployment readiness evidence |

Invalid confirmations:

- vague `yes`, `ok`, `go ahead`, or equivalent without active context;
- confirmation that references a stale proposal;
- approval whose scope differs from the proposal;
- approval that attempts to bypass validation, replay, or governance;
- confirmation inside advisory-only context treated as execution approval.

Required confirmation evidence:

- confirmation text hash;
- active context reference;
- proposal or release reference when applicable;
- approval scope;
- approval freshness;
- decision outcome;
- replay reference.

## 6. ACLI Session Lifecycle

Session lifecycle:

| Phase | Required Evidence |
| --- | --- |
| Session start | session id, operator context, repository context availability |
| Input capture | prompt/command hash, timestamp, source channel |
| Semantic or command resolution | command parser result or CSA reference/hash |
| Clarification lifecycle | active clarification id, questions, reply binding, resolution status |
| Workflow selection | selected workflow, rejected candidates, rationale, unsupported reason if any |
| Proposal | proposed action, scope, affected paths/resources, validation plan |
| Approval | approval request, human decision, freshness, scope match |
| Authorization | bounded authorization tied to approval |
| Execution or mutation | worker/mutation request, result, changed-file inventory if applicable |
| Validation | commands run, outputs, pass/fail, generated replay artifact handling |
| Replay linkage | replay references, hashes, reconstruction status |
| Release handoff | release packet update when applicable |
| Session close | completion status, next action, known limitations |

Lifecycle invariants:

- one active clarification at a time;
- no mutation before approval and authorization;
- no worker invocation before authorization;
- no provider invocation unless explicitly in a provider-eligible path;
- no release handoff without validation evidence;
- no hidden replay mutation.

## 7. UBTR Interaction Model

UBTR interaction model:

| ACLI Need | UBTR / CSA Role | ACLI Rule |
| --- | --- | --- |
| Natural-language meaning | Produce canonical semantic lineage | Consume CSA as semantic source |
| Ambiguity detection | Identify ambiguity and confidence | HIRR decides lifecycle response |
| Requested action | Represent action semantics | ACLI maps to supported workflow only after lifecycle checks |
| Domain/entity extraction | Represent target domain and entities | ACLI verifies supported scope |
| Explanation rendering | Provide semantic projection where certified | ACLI renders human-readable evidence |
| Replay lineage | Provide CSA reference/hash | ACLI persists lineage in session evidence |

UBTR must not:

- approve;
- authorize;
- execute;
- mutate repository or governance;
- select providers as authority;
- invoke workers;
- replace HIRR lifecycle enforcement;
- replace deterministic exact command parsing.

## 8. OCS Integration

OCS integration is limited to cognition orchestration and proposal-only support.

OCS may be used when:

- deterministic and CSA evidence indicate advisory cognition is appropriate;
- ambiguity remains safe and unresolved after clarification;
- Product 1 scenario requires cognition evidence;
- provider-assisted advisory cognition is explicitly allowed by later G3 provider
  activation work.

OCS must not:

- approve proposals;
- authorize execution;
- invoke workers;
- mutate governance;
- bypass HIRR clarification lifecycle;
- convert advisory cognition into executable work.

OCS evidence requirements:

- cognition request reference;
- CSA source reference;
- advisory/proposal-only status;
- provider involvement status;
- non-authority flags;
- replay hash.

## 9. Replay And Evidence Requirements

Every G3-02 ACLI session must record:

| Evidence | Required Fields |
| --- | --- |
| Session evidence | session id, operator channel, created timestamp, lifecycle state |
| Input evidence | prompt/command hash, raw text handling policy, source |
| Command boundary evidence | parser decision, exact-match status, CSA unused reason if applicable |
| CSA evidence | CSA reference/hash, semantic source, fallback status |
| HIRR evidence | clarification required, active clarification id, reply binding, lifecycle state |
| Workflow evidence | candidates, selection rationale, unsupported/fail-closed reason |
| Confirmation evidence | human confirmation class, scope, freshness, decision |
| Proposal/approval evidence | proposal hash, approval request, approval/denial |
| Authorization evidence | authorized scope, target paths/resources, boundary checks |
| Worker/mutation evidence | request, result, changed-file inventory, authority denials |
| Validation evidence | commands, outputs, pass/fail, generated artifact handling |
| Release evidence | release packet reference when applicable |
| Replay evidence | replay references, hashes, reconstruction status |

Replay requirements:

- historical replay remains read-only;
- generated validation replay artifacts are classified using G3-01 rules;
- every failure path records fail-closed evidence;
- every authority denial is visible;
- every next action is grounded in replay-visible state.

## 10. Governance Checkpoints

Required governance checkpoints:

| Checkpoint | Required Review |
| --- | --- |
| Command boundary | Exact commands remain deterministic and parser-authoritative |
| Semantic authority | Natural-language meaning comes from UBTR/CSA |
| HIRR lifecycle | Clarification-first and one-active-clarification invariants hold |
| Approval boundary | Action requires explicit in-scope approval |
| Authorization boundary | Execution/mutation requires bounded authorization |
| Provider boundary | Provider remains advisory and only used in eligible paths |
| Worker boundary | Worker runs only after approval and authorization |
| Replay boundary | Evidence is append-only, hash-bound, and reconstructable |
| Release boundary | Release handoff follows G3-01 packet rules |
| Product boundary | Product 1 remains AI Decision Validator |

Any checkpoint failure must block downstream action and produce fail-closed evidence.

## 11. Failure And Recovery Model

Failure classes:

| Failure | Required Behavior | Recovery Path |
| --- | --- | --- |
| Ambiguous input | Ask clarification or fail closed | User supplies clarification |
| Missing context | Ask for missing object/reference | User provides reference |
| No active continuation | Do not fabricate history | User selects prior session or restarts |
| Stale approval | Block authorization | Reissue proposal and approval request |
| Scope mismatch | Block authorization or execution | Create corrected proposal |
| Provider unavailable | Continue without provider if path allows or fail closed | Retry only under provider policy |
| Worker unavailable | Block execution | Select certified alternative or defer |
| Validation failure | Do not release or mark complete | Remediate through governed proposal |
| Replay mismatch | Fail closed | Inspect replay and preserve blocker evidence |
| Governance violation | Fail closed | Governance review before retry |

Recovery output must tell the user:

- what failed;
- which boundary blocked action;
- what evidence was recorded;
- what safe next action is available.

## 12. Required Runtime Components

G3-02 implementation may require these runtime components:

| Component | Purpose |
| --- | --- |
| ACLI session lifecycle artifact | Persist session state and lifecycle transitions |
| ACLI evidence root | Bind all session evidence under a deterministic root |
| CSA-visible response renderer | Show semantic source and fallback status to operator |
| Confirmation classifier | Distinguish clarification reply, advisory agreement, approval, release approval, and deployment approval |
| Proposal and approval bridge | Persist proposal, request, approval/denial, and scope |
| Authorization bridge | Persist bounded authorization after approval |
| Validation evidence bridge | Persist validation commands and results |
| Release packet handoff | Link ACLI validation evidence to G3-01 release packet model |
| Failure recovery renderer | Present blocked reason, evidence, and next action |

These components must be implemented incrementally with targeted tests when runtime work
begins.

## 13. Certification Milestones

| Milestone | Certification Target |
| --- | --- |
| G3-02A ACLI workflow inventory | Existing ACLI, command, HIRR, UBTR, approval, validation, and replay paths inventoried |
| G3-02B Session lifecycle evidence | Session lifecycle artifact and evidence root certified |
| G3-02C CSA-visible operator responses | ACLI displays semantic source, CSA hash, fallback, and next action |
| G3-02D Confirmation model | Approval, clarification, advisory, release, and deployment confirmations separated |
| G3-02E Governed development path | Proposal, approval, authorization, mutation/worker, validation, replay path certified |
| G3-02F Failure recovery | Ambiguity, missing context, stale approval, worker/provider failure, validation failure, replay mismatch certified |
| G3-02G ACLI primary interface certification | ACLI certified as primary human-first development interface |

## 14. Operational Readiness Criteria

G3-02 is operationally ready when:

1. Human operators can use ordinary language without internal vocabulary.
2. Ambiguous requests clarify or fail closed.
3. Exact commands remain deterministic.
4. CSA lineage is visible for semantic decisions.
5. HIRR lifecycle evidence is visible for clarification turns.
6. No action proceeds without explicit approval and authorization.
7. Failure recovery is understandable and replay-visible.
8. Product 1 scenarios can start through ACLI or have a certified handoff path.
9. Release packet handoff follows G3-01.
10. Full validation is green for runtime implementation batches.

## 15. Exit Criteria For G3-02

G3-02 exits successfully when:

| Exit Criterion | Required Evidence |
| --- | --- |
| Target UX defined | Section 2 |
| Interaction model defined | Section 3 |
| Development workflow defined | Section 4 |
| Confirmation model defined | Section 5 |
| Session lifecycle defined | Section 6 |
| UBTR and OCS interaction models defined | Sections 7 and 8 |
| Replay and evidence requirements defined | Section 9 |
| Governance checkpoints defined | Section 10 |
| Failure and recovery model defined | Section 11 |
| Runtime component inventory defined | Section 12 |
| Certification milestones defined | Section 13 |
| Operational readiness criteria defined | Section 14 |
| Validation passed | `git diff --check` |

Exit verdict:

```text
G3_02_ACLI_PRIMARY_DEVELOPMENT_INTERFACE_PROGRAM_READY
```

## 16. Dependencies On G3-03 And Later Workstreams

G3-02 provides the human-first interface foundation consumed by:

| Later Workstream | Dependency On G3-02 |
| --- | --- |
| G3-03 Product 1 operationalization | Product 1 scenarios should start, clarify, display evidence, and record audit state through ACLI |
| G3-04 real provider activation | Provider invocation must be surfaced to users as advisory, replay-visible, and non-authoritative |
| G3-05 worker ecosystem expansion | Worker execution must use ACLI proposal, approval, authorization, validation, and replay flow |
| G3-06 deployment readiness | Release and deployment approvals must use the confirmation model and release handoff |
| G3-07 production certification | ACLI readiness evidence becomes part of final Generation 3 certification |

No later workstream should bypass the G3-02 confirmation, evidence, or failure recovery
model.

## 17. Recommended Next Step

After this program is approved, the next batch should be:

```text
G3-02A_ACLI_WORKFLOW_INVENTORY_AND_SESSION_LIFECYCLE_EVIDENCE_V1
```

Expected scope:

- inventory current ACLI flows;
- define session lifecycle evidence schema;
- map current replay/evidence gaps;
- identify targeted runtime components for first implementation;
- avoid Product 1, provider, worker, and deployment expansion until ACLI lifecycle evidence
  is certified.

## 18. Final Verdict

```text
G3_02_ACLI_PRIMARY_DEVELOPMENT_INTERFACE_PROGRAM_READY
```
