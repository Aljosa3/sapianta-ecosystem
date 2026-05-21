# REAL_CHATGPT_SEMANTIC_INGRESS_CONTRACT_V1

## Status

Contract v1.

## Purpose

This contract defines the first formal governed semantic ingress contract
between real ChatGPT semantic cognition and AiGOL governance validation.

This is a semantic ingress envelope contract, nondeterministic cognition
boundary contract, uncertainty semantics contract, replay-visible semantic
proposal contract, and authority separation contract.

This is not ChatGPT API implementation, endpoint implementation, provider
execution, orchestration, autonomous continuation, durable replay backend,
hidden ingress, or automatic execution.

## Mission

The canonical semantic ingress flow is:

ChatGPT
-> AiGOL semantic ingress validation
-> governed semantic proposal lifecycle

The contract preserves constitutional authority separation, replay visibility,
explicit uncertainty semantics, fail-closed ambiguity handling, and
operator-visible ingress lifecycle.

## 1. Semantic Ingress Envelope

The semantic ingress envelope is the canonical artifact shape for advisory
ChatGPT semantic cognition entering AiGOL validation.

Required fields:

- `semantic_ingress_id`
- `session_id`
- `proposal_id`
- `semantic_intent`
- `requested_mode`
- `authority_boundary_statement`
- `semantic_boundary_statement`
- `uncertainty_labels`
- `lineage_refs`
- `created_by`
- `non_authority_statement`
- `semantic_proposal`

Optional fields:

- `source_conversation_ref`
- `operator_visible_event_ref`
- `supersedes_semantic_ingress_id`
- `semantic_refinement_ref`
- `ingress_notes`

Canonical envelope shape:

```json
{
  "semantic_ingress_id": "SEMANTIC-INGRESS-...",
  "session_id": "SESSION-...",
  "proposal_id": "PROPOSAL-...",
  "semantic_intent": "Review bounded semantic direction.",
  "requested_mode": "REVIEW_ONLY",
  "authority_boundary_statement": "Semantic ingress is advisory only and grants no approval, dispatch, execution, orchestration, or continuation authority.",
  "semantic_boundary_statement": "ChatGPT cognition is nondeterministic and non-authoritative; AiGOL must validate or reject the proposal.",
  "uncertainty_labels": [],
  "lineage_refs": [],
  "created_by": "CHATGPT_ADVISORY_COGNITION",
  "non_authority_statement": "This semantic ingress artifact is not approval, not execution authorization, not governance certification, and not provider dispatch.",
  "semantic_proposal": {}
}
```

Field requirements:

- `semantic_ingress_id` identifies the ingress artifact and must be derived
  from canonical envelope content or supplied as an explicit replay-safe
  identity.
- `session_id` must bind the ingress artifact to an operator-visible session.
- `proposal_id` must identify the bounded semantic proposal candidate.
- `semantic_intent` must summarize the proposed semantic direction without
  claiming execution authority.
- `requested_mode` must be one of `READ_ONLY`, `REVIEW_ONLY`, or `DEMO_ONLY`.
- `authority_boundary_statement` must explicitly deny approval, dispatch,
  execution, orchestration, provider invocation, replay mutation, lifecycle
  mutation, and autonomous continuation.
- `semantic_boundary_statement` must state that ChatGPT cognition is
  nondeterministic, advisory, and non-authoritative.
- `uncertainty_labels` must be an array of canonical uncertainty labels.
- `lineage_refs` must be an array of replay-visible references to prior
  proposal, conversation, session, ingress, or refinement artifacts.
- `created_by` must be `CHATGPT_ADVISORY_COGNITION` for real ChatGPT semantic
  ingress.
- `non_authority_statement` must state that semantic ingress is not approval,
  execution authorization, governance certification, provider dispatch, or
  continuation authority.
- `semantic_proposal` contains the bounded semantic proposal candidate and must
  remain subject to AiGOL validation.

Canonical serialization rules:

- Serialize using canonical JSON with sorted object keys and deterministic
  primitive values.
- Do not insert implicit timestamps.
- Do not infer missing fields.
- Preserve unknown inspection-only fields only if a future validator explicitly
  permits them.
- Unknown fields must never create authority, lifecycle transition, replay
  mutation, dispatch, execution, provider invocation, or orchestration.

Replay-visible fields:

- `semantic_ingress_id`
- `session_id`
- `proposal_id`
- `semantic_intent`
- `requested_mode`
- `uncertainty_labels`
- `lineage_refs`
- `created_by`
- `non_authority_statement`
- ingress status
- rejection reason when rejected

Forbidden fields:

- `approval_token`
- `dispatch_target`
- `execution_command`
- `provider_runtime`
- `orchestration_plan`
- `autonomous_continuation`
- `replay_mutation`
- `lifecycle_transition`
- `hidden_persistence`
- any field that implies approval, execution, dispatch, provider invocation,
  orchestration, replay rewrite, lifecycle mutation, or continuation authority.

Deterministic identity expectations:

- `semantic_ingress_id` must be stable for the same canonical ingress content
  when generated by AiGOL.
- Any hash or deterministic ID must exclude the generated identity field from
  its own hash input.
- Identity stability does not imply semantic reasoning determinism.

## 2. Explicit Uncertainty Semantics

Canonical uncertainty labels:

| Label | Meaning | Severity | Required handling |
| --- | --- | --- | --- |
| `LOW_CONFIDENCE_INTENT` | ChatGPT indicates or implies low confidence in the human intent interpretation. | Medium | Accept for validation only if all boundaries are explicit; otherwise reject ambiguous. |
| `AMBIGUOUS_EXECUTION_LANGUAGE` | The proposal includes language that could be read as execution request or execution authority. | High | Fail closed unless explicitly negated by authority boundaries and mode is non-executing. |
| `MULTIPLE_INTERPRETATIONS_PRESENT` | More than one semantic interpretation is present. | Medium | Require operator-visible ambiguity; reject if no bounded selected interpretation exists. |
| `AUTHORITY_INTENT_UNCLEAR` | Approval, dispatch, execution, or continuation intent cannot be ruled out. | High | Reject as authority ambiguity. |
| `POSSIBLE_ORCHESTRATION_LANGUAGE` | The proposal suggests coordination, routing, multi-step autonomous control, or orchestration. | High | Reject unless clearly framed as review-only description without control authority. |
| `POSSIBLE_PROVIDER_EXECUTION_LANGUAGE` | The proposal mentions provider execution, Codex dispatch, or runtime invocation. | High | Reject unless explicitly bounded as observation or review only. |
| `MISSING_BOUNDARY_CONTEXT` | Required semantic or authority boundary context is missing. | High | Reject missing boundary. |

Fail-closed escalation:

- Any high-severity uncertainty without explicit negating boundaries must reject.
- Multiple medium-severity uncertainty labels may escalate to
  `SEMANTIC_INGRESS_REJECTED_AMBIGUOUS`.
- Missing boundary context must reject before downstream validation.
- Uncertainty labels must be replay-visible and operator-visible.

## 3. Semantic Ambiguity Contract

AiGOL rejects ambiguity when semantic intent cannot be bounded without
inference.

AiGOL must reject:

- ambiguous requested mode;
- unclear authority claim;
- execution-like language;
- provider-dispatch language;
- orchestration language;
- missing intent boundaries;
- conflicting constraints;
- next-step language that implies approval or continuation.

Uncertainty is bounded only when:

- a non-executing mode is explicit;
- authority boundaries explicitly deny approval, dispatch, execution,
  orchestration, provider invocation, replay mutation, lifecycle mutation, and
  autonomous continuation;
- semantic boundaries explicitly state nondeterministic, advisory,
  non-authoritative cognition;
- ambiguity is visible to the operator.

Semantic authority escalation is prevented by treating every ChatGPT proposal as
advisory until AiGOL validates or rejects it. ChatGPT confidence, fluency,
ranking, or explanation never creates authority.

Replay-visible ambiguity evidence must include the uncertainty labels, status,
rejection reason, and lineage references. Replay evidence must not claim
deterministic reconstruction of ChatGPT reasoning.

## 4. Human Visibility Rules

Semantic ingress must be visible to the operator.

Required operator-visible elements:

- semantic ingress event;
- semantic ingress lifecycle status;
- advisory-only label;
- uncertainty state;
- proposal status;
- rejection reason;
- non-authority statement;
- source label;
- lineage reference;
- distinction between semantic proposal and governance approval.

Forbidden:

- hidden background ingestion;
- silent semantic retries;
- invisible semantic refinement;
- hidden semantic mutation;
- hidden session inheritance;
- proposal ingestion without status visibility;
- automatic downgrade from unsafe language to safe language;
- hidden continuation after rejection.

## 5. Replay + Lineage Semantics

Replay-visible semantic ingress identity:

- `semantic_ingress_id` identifies the ingress artifact.
- `proposal_id` identifies the semantic proposal candidate.
- `session_id` binds the artifact to an operator-visible session.
- `lineage_refs` links proposal, session, conversation, prior ingress, and
  refinement artifacts without rewriting them.

Lineage linkage rules:

- A refinement must reference the prior `semantic_ingress_id`.
- Supersession must be append-only and visible.
- A superseding proposal must not rewrite the prior proposal.
- A rejection must remain replay-visible.
- Cross-session linkage requires an explicit lineage reference and must not
  mutate the prior session.

Semantic refinement linkage:

- refinement is proposal lineage, not hidden continuation;
- refinement is advisory unless separately validated;
- refinement must preserve uncertainty labels or explicitly explain why they no
  longer apply;
- refinement must never repair prior replay entries.

Proposal supersession semantics:

- supersession creates a new ingress artifact;
- supersession references the earlier artifact;
- supersession does not delete, overwrite, or mutate prior semantic ingress
  evidence;
- supersession does not inherit approval, dispatch, execution, or continuation
  authority.

Append-only replay expectations:

- semantic ingress events are append-only;
- rejection events are append-only;
- refinement events are append-only;
- supersession events are append-only;
- no replay rewrite, repair, deletion, or hidden inference is allowed.

Session-local replay visibility:

- the v1 semantic ingress contract assumes session-local visibility unless a
  later durable replay contract is approved;
- session-local visibility is not durable replay backend certification.

Explicit limitation:

- ChatGPT reasoning is not replay deterministic.
- Only bounded semantic artifacts are replay-visible.

## 6. Fail-Closed Semantic Statuses

Canonical statuses:

- `SEMANTIC_INGRESS_ACCEPTED_FOR_VALIDATION`
- `SEMANTIC_INGRESS_REJECTED_AMBIGUOUS`
- `SEMANTIC_INGRESS_REJECTED_AUTHORITY`
- `SEMANTIC_INGRESS_REJECTED_EXECUTION_LANGUAGE`
- `SEMANTIC_INGRESS_REJECTED_ORCHESTRATION`
- `SEMANTIC_INGRESS_REJECTED_UNSUPPORTED_MODE`
- `SEMANTIC_INGRESS_REJECTED_MISSING_BOUNDARY`

Status meanings:

- `SEMANTIC_INGRESS_ACCEPTED_FOR_VALIDATION`: the semantic ingress artifact is
  structurally present, authority-bounded, uncertainty-visible, and admissible
  for AiGOL validation. It is not approval or execution authorization.
- `SEMANTIC_INGRESS_REJECTED_AMBIGUOUS`: semantic ambiguity cannot be bounded
  without inference.
- `SEMANTIC_INGRESS_REJECTED_AUTHORITY`: the artifact implies approval,
  dispatch, execution, provider invocation, replay mutation, lifecycle mutation,
  or continuation authority.
- `SEMANTIC_INGRESS_REJECTED_EXECUTION_LANGUAGE`: execution-like language is
  present without sufficient non-execution boundaries.
- `SEMANTIC_INGRESS_REJECTED_ORCHESTRATION`: orchestration, routing, autonomous
  coordination, or multi-agent control language is present.
- `SEMANTIC_INGRESS_REJECTED_UNSUPPORTED_MODE`: requested mode is not
  `READ_ONLY`, `REVIEW_ONLY`, or `DEMO_ONLY`.
- `SEMANTIC_INGRESS_REJECTED_MISSING_BOUNDARY`: semantic or authority boundary
  context is missing.

Escalation semantics:

- Unknown status fails closed.
- Unsupported mode fails closed.
- Missing boundary fails closed.
- Authority ambiguity fails closed.
- Execution or orchestration language fails closed unless explicitly bounded as
  non-authoritative review material.

Replay semantics:

- every accepted or rejected status must be replay-visible;
- rejection reasons must be replay-visible;
- uncertainty labels must be replay-visible;
- status visibility does not create approval, dispatch, execution, or
  continuation authority.

Operator visibility requirements:

- status label;
- compact reason;
- detailed evidence;
- advisory-only label;
- non-authority statement;
- uncertainty labels;
- lineage references.

## 7. Constitutional Authority Model

ChatGPT may:

- interpret;
- structure;
- summarize;
- refine;
- propose.

ChatGPT must not:

- approve;
- dispatch;
- execute;
- self-authorize;
- bypass AiGOL governance;
- create autonomous continuation;
- mutate replay or lifecycle;
- infer execution authority;
- certify governance admissibility;
- invoke providers.

AiGOL remains:

- governance authority;
- admissibility authority;
- replay authority;
- lifecycle authority;
- validation authority.

Codex remains:

- bounded execution provider only;
- outside semantic ingress;
- unavailable unless a separate governed execution authorization path exists.

## 8. Non-Goals

This contract does not authorize:

- ChatGPT API integration;
- endpoint implementation;
- localhost listener implementation;
- provider dispatch;
- execution;
- approval automation;
- orchestration;
- autonomous continuation;
- durable replay backend;
- hidden persistence;
- hidden semantic refinement;
- automatic semantic retries.

## 9. Remaining Risks

- Operators may over-trust ChatGPT fluency as semantic correctness.
- `SEMANTIC_INGRESS_ACCEPTED_FOR_VALIDATION` may be mistaken for approval.
- Nondeterministic reasoning may be mistaken for replay-deterministic logic.
- Future endpoint pressure may create hidden ingress risk.
- Ambiguous execution language can be subtle and must remain fail-closed.
- Session-local replay may be overread as durable replay evidence.

## Recommended Next Implementation Milestone

Prepare `REAL_CHATGPT_SEMANTIC_INGRESS_VALIDATOR_PLAN_V1`.

The next milestone should remain plan/spec only unless separately approved. It
should define a pure validation primitive for semantic ingress envelopes that
accepts explicit input, returns an in-memory validation report, rejects
ambiguity fail-closed, and performs no IO, endpoint handling, provider calls,
dispatch, approval, execution, orchestration, replay mutation, lifecycle
mutation, or durable persistence.
