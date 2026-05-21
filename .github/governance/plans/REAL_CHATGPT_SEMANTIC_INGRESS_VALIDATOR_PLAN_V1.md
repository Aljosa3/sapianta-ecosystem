# REAL_CHATGPT_SEMANTIC_INGRESS_VALIDATOR_PLAN_V1

## Status

Validator plan v1.

Readiness decision: `READY_FOR_PURE_FUNCTION_IMPLEMENTATION_REVIEW`

## Purpose

This plan defines a pure-function validator for real ChatGPT semantic ingress
envelopes based on `REAL_CHATGPT_SEMANTIC_INGRESS_CONTRACT_V1`.

The planned validator is:

```python
validate_real_chatgpt_semantic_ingress(envelope: dict) -> dict
```

This is plan/specification only. It is not implementation, ChatGPT API
integration, endpoint implementation, provider dispatch, execution, approval
automation, orchestration, autonomous continuation, durable replay backend, or
hidden ingress.

## Scope

Allowed validator scope:

- validate explicit in-memory semantic ingress envelope objects;
- perform required field checks;
- detect forbidden authority-bearing fields;
- validate supported `requested_mode`;
- enforce `created_by == CHATGPT_ADVISORY_COGNITION`;
- validate advisory-only and non-authority statements;
- evaluate uncertainty labels;
- reject execution, orchestration, provider, approval, dispatch, replay
  mutation, lifecycle mutation, and continuation language;
- validate `lineage_refs`;
- require `semantic_proposal`;
- return deterministic in-memory validation reports;
- prepare bounded refinement-loop guidance as a recommendation only.

Forbidden validator scope:

- filesystem reads or writes;
- network calls;
- ChatGPT API calls;
- endpoint handling;
- provider calls;
- dispatch;
- approval;
- execution;
- orchestration;
- replay mutation;
- lifecycle mutation;
- durable persistence;
- hidden retries;
- automatic semantic refinement;
- autonomous continuation.

## Validation Order

The planned validator should use a deterministic validation order:

1. canonicalize input envelope into an internal copy;
2. verify the envelope is a JSON-like object;
3. validate required fields;
4. reject forbidden authority-bearing fields;
5. validate `requested_mode`;
6. validate `created_by`;
7. validate `authority_boundary_statement`;
8. validate `semantic_boundary_statement`;
9. validate `non_authority_statement`;
10. validate `uncertainty_labels`;
11. reject execution, orchestration, provider, approval, dispatch, replay
    mutation, lifecycle mutation, and continuation language;
12. validate `lineage_refs`;
13. validate `semantic_proposal` presence and object shape;
14. select fail-closed semantic ingress status;
15. build deterministic validation report.

The validator must not infer missing fields, repair unsafe language, or rewrite
the envelope.

## Required Field Checks

Required envelope fields:

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

Missing, empty, or malformed required fields should return
`SEMANTIC_INGRESS_REJECTED_MISSING_BOUNDARY` when the missing field is a
boundary field and `SEMANTIC_INGRESS_REJECTED_AMBIGUOUS` for other required
semantic context gaps.

## Forbidden Authority-Bearing Field Checks

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

Presence of any forbidden field should return the most specific rejection:

- execution fields -> `SEMANTIC_INGRESS_REJECTED_EXECUTION_LANGUAGE`
- orchestration fields -> `SEMANTIC_INGRESS_REJECTED_ORCHESTRATION`
- approval, dispatch, replay, lifecycle, continuation, or hidden persistence
  fields -> `SEMANTIC_INGRESS_REJECTED_AUTHORITY`

## Supported Requested Mode Checks

Supported modes:

- `READ_ONLY`
- `REVIEW_ONLY`
- `DEMO_ONLY`

Unsupported or missing `requested_mode` should return
`SEMANTIC_INGRESS_REJECTED_UNSUPPORTED_MODE`.

Execution-like modes such as `EXECUTE`, `AUTO_EXECUTE`, `AUTONOMOUS`,
`PROVIDER_RUNTIME`, and `ORCHESTRATION` should fail closed and may map to
`SEMANTIC_INGRESS_REJECTED_EXECUTION_LANGUAGE`,
`SEMANTIC_INGRESS_REJECTED_ORCHESTRATION`, or
`SEMANTIC_INGRESS_REJECTED_UNSUPPORTED_MODE` depending on the specific mode.

## Advisory-Only Created By Check

`created_by` must be:

- `CHATGPT_ADVISORY_COGNITION`

Any other value should return `SEMANTIC_INGRESS_REJECTED_AUTHORITY` unless a
future contract explicitly authorizes another advisory source label.

## Non-Authority Statement Check

`non_authority_statement` must explicitly state that the semantic ingress
artifact is not:

- approval;
- execution authorization;
- governance certification;
- provider dispatch;
- orchestration authority;
- autonomous continuation authority.

Incomplete statements should return `SEMANTIC_INGRESS_REJECTED_AUTHORITY`.

## Uncertainty Label Handling

Allowed uncertainty labels:

- `LOW_CONFIDENCE_INTENT`
- `AMBIGUOUS_EXECUTION_LANGUAGE`
- `MULTIPLE_INTERPRETATIONS_PRESENT`
- `AUTHORITY_INTENT_UNCLEAR`
- `POSSIBLE_ORCHESTRATION_LANGUAGE`
- `POSSIBLE_PROVIDER_EXECUTION_LANGUAGE`
- `MISSING_BOUNDARY_CONTEXT`

Handling rules:

- unknown uncertainty labels return `SEMANTIC_INGRESS_REJECTED_AMBIGUOUS`;
- high-severity labels must reject unless explicit boundary statements fully
  negate the risk;
- `AUTHORITY_INTENT_UNCLEAR` returns
  `SEMANTIC_INGRESS_REJECTED_AUTHORITY`;
- `AMBIGUOUS_EXECUTION_LANGUAGE` returns
  `SEMANTIC_INGRESS_REJECTED_EXECUTION_LANGUAGE` unless bounded;
- `POSSIBLE_ORCHESTRATION_LANGUAGE` returns
  `SEMANTIC_INGRESS_REJECTED_ORCHESTRATION` unless bounded;
- `POSSIBLE_PROVIDER_EXECUTION_LANGUAGE` returns
  `SEMANTIC_INGRESS_REJECTED_EXECUTION_LANGUAGE` unless bounded;
- `MISSING_BOUNDARY_CONTEXT` returns
  `SEMANTIC_INGRESS_REJECTED_MISSING_BOUNDARY`;
- accepted labels must appear in `uncertainty_findings`.

## Language Rejection Checks

The validator should scan relevant text fields:

- `semantic_intent`
- `requested_mode`
- `authority_boundary_statement`
- `semantic_boundary_statement`
- `non_authority_statement`
- string content in `semantic_proposal`

Reject language that implies:

- approval;
- execution;
- dispatch;
- provider runtime;
- Codex execution;
- orchestration;
- autonomous continuation;
- replay mutation;
- lifecycle mutation;
- hidden persistence.

Explicit negation may bound otherwise risky language only when the requested
mode is non-executing and all authority statements are complete.

## Lineage Refs Validation

`lineage_refs` must be an array.

Each lineage ref should be either:

- a string replay-visible identifier; or
- an object with deterministic inspection fields such as `ref_type`, `ref_id`,
  and `relationship`.

Malformed lineage refs should return `SEMANTIC_INGRESS_REJECTED_AMBIGUOUS`.

The validator must not resolve lineage refs from disk or network. It validates
shape only.

## Semantic Proposal Presence

`semantic_proposal` must be present and must be a JSON-like object.

Missing or malformed `semantic_proposal` should return
`SEMANTIC_INGRESS_REJECTED_MISSING_BOUNDARY`.

The validator should not normalize, rewrite, enrich, or execute semantic
proposal content.

## Deterministic Report Shape

The validator should return:

```json
{
  "status": "SEMANTIC_INGRESS_ACCEPTED_FOR_VALIDATION",
  "ingress_id": "...",
  "proposal_id": "...",
  "session_id": "...",
  "rejection_reason": "",
  "uncertainty_findings": [],
  "authority_findings": [],
  "replay_visibility": {},
  "lineage_refs": [],
  "advisory_only_label": "CHATGPT_ADVISORY_ONLY_NOT_APPROVAL_NOT_EXECUTION",
  "recommended_refinement_instruction": ""
}
```

Report requirements:

- deterministic key set;
- deterministic list ordering;
- no timestamps unless externally supplied in a future contract;
- no random identifiers;
- no mutation of input envelope;
- no hidden persistence;
- no filesystem, network, provider, dispatch, approval, or execution behavior.

## Bounded Refinement-Loop Preparation

`recommended_refinement_instruction` may suggest a bounded human-visible
refinement instruction when the envelope is rejected.

It must:

- be advisory only;
- be deterministic;
- cite the rejection reason;
- request boundary clarification rather than perform hidden repair;
- never approve, dispatch, execute, orchestrate, call providers, mutate replay,
  mutate lifecycle, or continue autonomously.

## Status Selection Precedence

Recommended deterministic precedence:

1. `SEMANTIC_INGRESS_REJECTED_MISSING_BOUNDARY`
2. `SEMANTIC_INGRESS_REJECTED_AUTHORITY`
3. `SEMANTIC_INGRESS_REJECTED_EXECUTION_LANGUAGE`
4. `SEMANTIC_INGRESS_REJECTED_ORCHESTRATION`
5. `SEMANTIC_INGRESS_REJECTED_UNSUPPORTED_MODE`
6. `SEMANTIC_INGRESS_REJECTED_AMBIGUOUS`
7. `SEMANTIC_INGRESS_ACCEPTED_FOR_VALIDATION`

The implementation review may revise precedence if it preserves fail-closed
semantics and deterministic output.

## Tests Required For Future Implementation

Future tests should prove:

- valid envelope returns `SEMANTIC_INGRESS_ACCEPTED_FOR_VALIDATION`;
- missing required fields fail closed;
- forbidden authority-bearing fields are rejected;
- unsupported modes are rejected;
- non-`CHATGPT_ADVISORY_COGNITION` `created_by` is rejected;
- incomplete non-authority statements are rejected;
- unknown uncertainty labels are rejected;
- high-severity uncertainty labels fail closed;
- execution language is rejected;
- orchestration language is rejected;
- provider language is rejected;
- malformed `lineage_refs` are rejected;
- missing `semantic_proposal` is rejected;
- report shape is deterministic;
- input envelope is not mutated;
- no IO, endpoint, provider, dispatch, approval, execution, orchestration,
  replay mutation, lifecycle mutation, or hidden persistence is introduced.

## Recommended Next Step

Prepare `REAL_CHATGPT_SEMANTIC_INGRESS_VALIDATOR_IMPLEMENTATION_REVIEW_V1`
before implementation.
