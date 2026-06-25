# ACLI_OPERATOR_EXPERIENCE_CERTIFICATION_V1

Status: Certified With Non-Blocking Improvements

Target verdict:

```text
ACLI_OPERATOR_EXPERIENCE_CERTIFIED
```

## 1. Purpose

This artifact certifies ACLI from the perspective of a non-technical operator.

It reviews only operator experience:

- request entry;
- routing visibility;
- proposal presentation;
- deterministic explanation;
- optional LLM-assisted explanation;
- approval;
- execution;
- validation;
- replay;
- resume;
- rejection;
- modification.

This certification does not review architecture, workflow correctness, governance correctness, or runtime authority design.

## 2. Certification Basis

The certified operator path is:

```text
Human request
-> ACLI
-> routing decision
-> governed development proposal
-> deterministic explanation
-> optional LLM-assisted explanation
-> explicit approval / rejection / modification request
-> execution when approved
-> validation
-> replay
```

The review assumes the current operator-facing implementation includes:

- governed development bridge;
- governance artifact normalization into `GOVERNED_DEVELOPMENT_WORKFLOW`;
- same-session approval handling;
- safe approval resume;
- deterministic human-friendly explanation;
- optional LLM-assisted explanation;
- explanation source transparency V2;
- proposal content fidelity;
- operator-language refactor.

## 3. End-To-End Experience Review

### 3.1 Entering A Request

Result:

```text
PASS
```

Normal operator prompts such as:

```text
Create governance artifact ACLI_OPERATOR_GUIDE_V1 explaining ACLI approval, replay, validation, and execution behavior for a non-technical operator.
```

are now expected to enter the governed development lifecycle instead of exposing unsupported internal workflow branches.

Operator clarity:

```text
HIGH
```

Residual friction:

The operator still benefits from clear artifact naming and concise purpose extraction. This is acceptable because proposal fidelity now preserves explicit artifact identifiers when deterministic and safe.

### 3.2 Routing

Result:

```text
PASS
```

Routing visibility now communicates the selected workflow and matched signals.

Operator clarity:

```text
MEDIUM_HIGH
```

Strengths:

- workflow selection is visible;
- confidence is visible;
- matched signals are visible;
- stateful approval turns no longer misleadingly show routing failure when approval handling succeeds.

Residual friction:

Workflow identifiers remain technical. They are acceptable in diagnostics, but non-technical operators benefit more from a plain-language first sentence.

### 3.3 Proposal Presentation

Result:

```text
PASS
```

The proposal now exposes:

- requested artifact identifier;
- selected artifact identifier;
- target paths;
- proposal hash;
- approval boundary;
- mutation status before approval;
- worker status before approval.

Operator clarity:

```text
HIGH
```

Strengths:

- the operator can see what ACLI plans to create or modify before approval;
- explicit artifact names such as `ACLI_USAGE_GUIDELINES_V1` are preserved when safe;
- repository mutation is not hidden behind opaque hash-based names.

Residual friction:

The proposal still includes a diagnostic section. This is appropriate for auditability, but the primary operator view should continue to keep diagnostics visually secondary.

### 3.4 Deterministic Explanation

Result:

```text
PASS
```

The deterministic explanation now tells the operator:

- what ACLI understood;
- what will happen if approved;
- what will not happen before approval;
- why approval is required;
- what to type next;
- where replay evidence will be available;
- what is authoritative versus explanatory.

Operator clarity:

```text
HIGH
```

The explanation is non-authoritative and replay-visible.

### 3.5 Optional LLM-Assisted Explanation

Result:

```text
PASS_WITH_CONFIGURATION_DEPENDENCY
```

The optional LLM-assisted explanation layer improves readability when configured or injected.

Operator clarity:

```text
MEDIUM_HIGH
```

Strengths:

- provider output is explicitly marked advisory;
- provider output cannot change workflow, approval, execution, validation, or replay authority;
- provider failure falls back to deterministic explanation;
- source transparency explains whether provider assistance was used.

Residual friction:

Provider assistance is not enabled by default. A non-technical operator may not know whether LLM assistance is available unless the transparency section states provider status clearly.

Current certification position:

```text
Optional provider assistance is experience-positive but not required for operator readiness.
```

### 3.6 Approval

Result:

```text
PASS
```

Approval behavior is understandable:

- `APPROVE` continues an in-memory pending proposal;
- safe resume re-presents restored proposals before execution;
- cross-session execution requires explicit confirmation such as `APPROVE THIS PROPOSAL`;
- approval binds to proposal hash;
- no mutation occurs before approval.

Operator clarity:

```text
HIGH
```

The approval boundary is now visible enough for a non-technical operator to understand that typing approval is the action that allows execution.

### 3.7 Execution

Result:

```text
PASS
```

After approval, execution output now communicates:

- approved and executed;
- repository mutation occurred;
- worker ran;
- validation ran;
- replay lineage was preserved.

Operator clarity:

```text
MEDIUM_HIGH
```

Residual friction:

Execution summaries still include technical diagnostic fields. They are useful, but the first operator-facing lines should remain plain-language.

### 3.8 Validation

Result:

```text
PASS
```

Validation evidence is surfaced after execution.

Operator clarity:

```text
MEDIUM_HIGH
```

Strengths:

- validation is clearly after approval and execution;
- validation is not implied before execution;
- validation success is visible.

Residual friction:

Non-technical operators may not know what specific validation checks mean. A short plain-language summary should remain primary.

### 3.9 Replay

Result:

```text
PASS
```

Replay is visible across proposal, explanation, approval, execution, validation, and optional provider explanation.

Operator clarity:

```text
MEDIUM
```

Strengths:

- replay locations are shown;
- replay is source-of-truth evidence;
- explanation source transparency records rendered operator view hashes;
- provider-assisted explanation replay distinguishes provider success, fallback, and deterministic-only modes.

Residual friction:

Replay paths are still file-system oriented. A non-technical operator can understand that evidence exists, but may not know how to inspect it without a guided replay viewer or command.

### 3.10 Resume

Result:

```text
PASS
```

Safe approval resume improves operator safety.

Operator clarity:

```text
HIGH
```

Critical behavior:

- bare `APPROVE` after restart does not execute immediately;
- ACLI re-presents the restored proposal;
- execution requires explicit confirmation of the displayed proposal.

This substantially improves confidence for non-technical operation.

### 3.11 Rejection

Result:

```text
PASS
```

Rejection blocks execution and preserves replay evidence.

Operator clarity:

```text
HIGH
```

The operator can understand that rejecting a proposal cancels mutation.

### 3.12 Modification

Result:

```text
PASS
```

`REQUEST_MODIFICATION` rejects the current proposal without mutation, clears execution authorization state, and asks the operator to describe the required change.

Operator clarity:

```text
HIGH
```

This is a major operator-confidence improvement because it provides a safe alternative between approval and rejection.

## 4. Experience Criteria Assessment

| Criterion | Assessment | Notes |
| --- | --- | --- |
| Clarity | PASS | Primary proposal, approval, rejection, modification, and execution messages are understandable. |
| Terminology | PASS_WITH_MINOR_FRICTION | Workflow names and replay paths remain technical but are increasingly isolated in diagnostics. |
| Operator confidence | PASS | Approval boundary, proposal hash binding, replay, and source transparency improve trust. |
| Cognitive load | PASS_WITH_MINOR_FRICTION | The system is understandable, but output volume can be high. |
| Unnecessary technical details | PARTIAL_PASS | Diagnostics remain useful but should stay visually secondary. |
| Consistency | PASS | Proposal, approval, resume, rejection, and modification now share a coherent lifecycle. |
| Approval understanding | PASS | Approval behavior and safe resume are clear. |
| Replay understanding | PARTIAL_PASS | Replay is visible and trustworthy, but not yet fully operator-friendly to inspect. |

## 5. P0 Issues

P0 issues are blockers that prevent non-technical operator certification.

Current P0 issues:

```text
None.
```

Rationale:

- operator can enter a normal request;
- proposal is visible before approval;
- deterministic explanation is available;
- approval is explicit;
- execution does not occur before approval;
- rejection and modification are safe;
- replay is visible;
- resume is safe;
- provider explanation is optional and advisory only.

## 6. P1 Improvements

P1 improvements are important experience refinements but do not block certification.

### P1-001 Simplify Workflow Status For Operators

Current status blocks still expose runtime-like fields.

Recommended improvement:

Show a short operator sentence first:

```text
Current status: Waiting for your approval.
```

Keep full lifecycle state in diagnostics.

### P1-002 Add Replay Inspection Guidance

Replay paths are visible but still technical.

Recommended improvement:

Add one plain-language line:

```text
To inspect evidence later, use the replay reference shown below.
```

Optionally provide the relevant ACLI replay command when available.

### P1-003 Label Diagnostic Sections More Aggressively

The operator should always know when content is diagnostic.

Recommended improvement:

Use:

```text
Diagnostics for audit and support
```

instead of terse technical labels where possible.

### P1-004 Explain Validation Outcome In Plain Language

Validation result should appear as:

```text
Validation passed. ACLI did not detect formatting or governance evidence problems in this change.
```

Technical validation command details can remain in diagnostics.

### P1-005 Surface Provider Configuration State Early

When LLM-assisted explanation is disabled, the transparency section should remain clear that this is configuration, not failure.

The current source transparency V2 supports this; future operator wording should keep it plain.

## 7. P2 Future Enhancements

P2 items are future experience enhancements.

### P2-001 Guided Replay Viewer

Create an operator-facing replay inspection command or view that summarizes:

- request;
- selected workflow;
- proposal;
- approval decision;
- execution result;
- validation result;
- explanation source;
- replay hashes.

### P2-002 Adaptive Explanation Escalation

Use deterministic explanation by default, then escalate to provider-assisted explanation only when ambiguity, operator confusion, or high cognitive load is detected.

### P2-003 Operator Satisfaction Capture

Allow replay to record optional operator feedback:

- explanation accepted;
- explanation confusing;
- clarification requested;
- satisfaction rating.

This must remain evidence only and must not directly modify deterministic behavior.

### P2-004 Reduced Output Mode

Offer a concise mode for experienced operators:

```text
summary only + replay references
```

with full diagnostics still available.

## 8. Operator Experience Score

Operator Experience Score:

```text
88 / 100
```

Score rationale:

- strong request-to-proposal clarity;
- strong approval boundary clarity;
- strong safe resume behavior;
- strong rejection and modification behavior;
- strong explanation source transparency;
- moderate remaining cognitive load from diagnostics and replay paths.

## 9. Readiness Score

Readiness Score:

```text
90 / 100
```

Score rationale:

- no P0 operator-experience blockers remain;
- current path is usable by a non-technical operator with minimal guidance;
- P1 improvements would improve polish but are not required for readiness;
- optional LLM-assisted explanation is correctly non-authoritative and fallback-safe.

## 10. Certification Recommendation

Recommendation:

```text
CERTIFY_OPERATOR_EXPERIENCE
```

Conditions:

- keep deterministic explanation enabled;
- keep proposal preview before approval;
- keep safe approval resume;
- keep rejection and modification paths visible;
- keep explanation source transparency visible;
- keep diagnostics secondary to operator summaries.

Non-blocking follow-up:

Complete P1 improvements before a public demo or third-party evaluation.

## 11. Final Verdict

```text
ACLI_OPERATOR_EXPERIENCE_CERTIFIED
```

ACLI is certified as usable from the perspective of a non-technical operator for the governed development lifecycle. Remaining issues are operator-experience refinements, not certification blockers.
