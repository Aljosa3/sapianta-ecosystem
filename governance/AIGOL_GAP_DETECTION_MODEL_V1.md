# AIGOL_GAP_DETECTION_MODEL_V1

## Status

Foundation model.

## Definition

A Gap is a replay-visible condition where observed evidence diverges from expected governance, runtime, domain, worker, or operator workflow expectations.

Gap detection is evidence classification only.

It is not proposal generation.

It is not approval.

It is not implementation.

## Gap Categories

Mandatory categories:

```text
MISSING_EVIDENCE
HASH_MISMATCH
CHAIN_CONTINUITY_FAILURE
REPLAY_RECONSTRUCTION_FAILURE
VALIDATION_FAILURE
POLICY_CONSTRAINT_FAILURE
RESOURCE_SELECTION_AMBIGUITY
PROVIDER_UNAVAILABLE
PROPOSAL_REJECTION_PATTERN
CLARIFICATION_LOOP
APPROVAL_ESCALATION_PATTERN
CONTEXT_ASSEMBLY_INCOMPLETE
DOMAIN_POLICY_MISMATCH
WORKER_EVIDENCE_INCONSISTENCY
OPERATOR_WORKFLOW_FRICTION
```

## Gap Artifact Candidate Fields

Future runtime artifacts should include:

```text
artifact_type
gap_detection_version
gap_id
canonical_chain_id
source_replay_reference
source_replay_hash
observed_condition
expected_condition
gap_category
affected_layer
affected_domain
affected_worker_family
severity
confidence
repeat_count
false_positive_controls
human_review_required
improvement_intent_allowed
created_at
replay_visible
artifact_hash
```

## Severity

Severity values:

```text
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

Critical does not mean automatic implementation.

Critical means human-visible escalation is required.

## Confidence

Confidence values:

```text
LOW
MEDIUM
HIGH
DETERMINISTIC
```

Only `HIGH` or `DETERMINISTIC` gaps may become improvement-intent candidates without human clarification.

## False Positive Controls

Gap detection must avoid false-positive improvements by requiring:

- expected condition reference;
- observed condition reference;
- replay hash;
- chain id;
- affected scope;
- deterministic category;
- duplicate detection;
- known limitation check;
- policy exception check.

If expected behavior is unknown, the result is:

```text
GAP_CANDIDATE_REQUIRES_HUMAN_REVIEW
```

## Fail-Closed Conditions

Gap detection must fail closed when:

- replay evidence is missing;
- source hash mismatches;
- chain continuity fails;
- expected condition cannot be identified;
- observed condition is ambiguous;
- affected scope is ambiguous;
- confidence is insufficient;
- false-positive controls cannot run.

## Non-Goals

Gap Detection does not:

- create proposals;
- create improvement intents automatically unless policy permits;
- approve;
- authorize;
- mutate governance;
- mutate replay;
- execute;
- invoke providers;
- invoke workers.
