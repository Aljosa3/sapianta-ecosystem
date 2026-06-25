# ACLI_REAL_WORLD_OPERATOR_VALIDATION_V1

Status: Validated With Production-Readiness Recommendations

Target verdict:

```text
ACLI_REAL_WORLD_OPERATOR_VALIDATED
```

## 1. Purpose

This artifact validates ACLI through representative real-world operator journeys rather than isolated feature certification.

The validation focuses only on operator experience:

- whether a non-technical operator can complete realistic work;
- whether ACLI explains what it understood;
- whether the operator understands the approval boundary;
- whether replay and validation are understandable;
- whether rejection, modification, resume, and provider-assisted explanations are usable.

This artifact does not review architecture or governance correctness.

## 2. Validation Scope

Representative end-to-end tasks:

1. Governance artifact creation.
2. Existing document update.
3. Implementation request.
4. Proposal modification.
5. Approval and execution.
6. Rejection.
7. Replay review.
8. Session resume.
9. Provider-assisted explanation.

Operator profiles:

| Profile | Description |
| --- | --- |
| First-time operator | Understands the task goal but does not know ACLI internals, workflow names, replay structure, or proposal hash semantics. |
| Experienced operator | Has completed at least three governed ACLI proposal cycles and understands approval, replay, and validation vocabulary. |

## 3. Operator Journey Map

```text
Need
-> natural-language request
-> routing visibility
-> proposal preview
-> explanation and transparency
-> operator decision
   -> APPROVE
   -> REJECT
   -> REQUEST_MODIFICATION
-> execution if approved
-> validation
-> replay evidence
-> resume or review if needed
```

### Journey Stage 1: Request Entry

Operator goal:

```text
Tell ACLI what should be created, updated, or implemented.
```

Current experience:

- natural-language prompts are accepted;
- explicit governance artifact names are preserved when safe;
- common development prompts route to the governed development lifecycle.

First-time operator assessment:

```text
Clear enough to start.
```

Experienced operator assessment:

```text
Fast and predictable.
```

Friction:

- operators may not know which wording produces the cleanest proposal;
- artifact identifiers are still a learned convention.

### Journey Stage 2: Routing

Operator goal:

```text
Understand what ACLI thinks the request means.
```

Current experience:

- selected workflow is visible;
- matched routing signals are visible;
- routing confidence is visible.

First-time operator assessment:

```text
Mostly understandable, but workflow identifiers are technical.
```

Experienced operator assessment:

```text
Useful diagnostic signal.
```

Friction:

- `GOVERNED_DEVELOPMENT_WORKFLOW` is accurate but not plain language;
- matched terms are useful but can feel like internal diagnostics.

### Journey Stage 3: Proposal Presentation

Operator goal:

```text
Know what ACLI plans to change before approving anything.
```

Current experience:

- requested artifact names are visible;
- selected artifact names are visible;
- target paths are visible;
- proposal hash is visible;
- repository mutation has not occurred yet.

First-time operator assessment:

```text
Strong confidence before approval when artifact name and target path are visible.
```

Experienced operator assessment:

```text
High confidence and efficient review.
```

Friction:

- proposal hashes are important but technical;
- target paths are useful, but non-technical operators may need a short explanation of why paths matter.

### Journey Stage 4: Explanation

Operator goal:

```text
Understand what ACLI understood, what will happen, what will not happen, and what to type next.
```

Current experience:

- deterministic explanation renders required sections;
- explanation source transparency identifies authoritative state and advisory explanation source;
- optional provider-assisted explanation can be shown when configured;
- fallback states are visible.

First-time operator assessment:

```text
High confidence when the explanation appears before approval.
```

Experienced operator assessment:

```text
Useful, occasionally verbose.
```

Friction:

- output length can be high;
- provider status is valuable but may be more detail than a first-time operator needs unless visually separated.

### Journey Stage 5: Approval

Operator goal:

```text
Decide whether to allow execution.
```

Current experience:

- approval boundary is explicit;
- `APPROVE`, `REJECT`, and `REQUEST_MODIFICATION` are visible;
- approval binds to proposal hash;
- mutation does not occur before approval.

First-time operator assessment:

```text
Clear and confidence-building.
```

Experienced operator assessment:

```text
Fast enough for repeated use.
```

Friction:

- after session resume, `APPROVE THIS PROPOSAL` is safer but slightly more cognitive overhead than bare `APPROVE`.

### Journey Stage 6: Execution

Operator goal:

```text
Know that approved work happened and what changed.
```

Current experience:

- execution summary identifies approval, mutation, worker execution, validation, and replay preservation;
- diagnostics remain available.

First-time operator assessment:

```text
Understandable if the operator reads the summary first and diagnostics second.
```

Experienced operator assessment:

```text
Useful and auditable.
```

Friction:

- execution diagnostics still include runtime terms that can compete with the primary summary.

### Journey Stage 7: Validation

Operator goal:

```text
Know whether ACLI detected a problem after execution.
```

Current experience:

- validation status is visible;
- validation is clearly after execution;
- validation does not imply approval was bypassed.

First-time operator assessment:

```text
Understands pass/fail, but may not understand individual validation checks.
```

Experienced operator assessment:

```text
Sufficient for operational use.
```

Friction:

- validation detail should remain diagnostic unless the operator asks for it.

### Journey Stage 8: Replay Review

Operator goal:

```text
Find evidence of what happened.
```

Current experience:

- replay references are visible;
- explanation, proposal, approval, execution, validation, and provider explanation can produce replay evidence;
- source transparency records rendered operator view hashes.

First-time operator assessment:

```text
Understands that evidence exists, but may not know how to inspect it.
```

Experienced operator assessment:

```text
Usable with replay path familiarity.
```

Friction:

- replay is still path-oriented;
- a guided replay viewer would significantly improve production usability.

### Journey Stage 9: Resume

Operator goal:

```text
Continue safely after leaving and restarting ACLI.
```

Current experience:

- pending proposals can be restored;
- bare `APPROVE` after restart shows the restored proposal instead of executing;
- execution requires explicit confirmation of the displayed proposal.

First-time operator assessment:

```text
Safe and understandable.
```

Experienced operator assessment:

```text
Slightly slower but appropriately safe.
```

Friction:

- the resume safety rule should be mentioned in the runbook and proposal view.

### Journey Stage 10: Rejection And Modification

Operator goal:

```text
Stop or revise work without accidental execution.
```

Current experience:

- `REJECT` blocks execution and mutation;
- `REQUEST_MODIFICATION` stops the current proposal and asks for revision instructions;
- no worker runs and no repository mutation occurs.

First-time operator assessment:

```text
Clear.
```

Experienced operator assessment:

```text
Clear and operationally useful.
```

Friction:

- the next proposal after modification should make clear whether it supersedes the old proposal.

## 4. Scenario Validation Matrix

| Scenario | First-Time Operator | Experienced Operator | Clarification Requests | Confidence Before Approval | Confidence After Execution | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Governance artifact creation | 4-6 minutes | 1-2 minutes | 0-1 | High | High | PASS |
| Existing document update | 5-8 minutes | 2-3 minutes | 0-2 | Medium-High | High | PASS_WITH_FRICTION |
| Implementation request | 6-10 minutes | 3-5 minutes | 1-2 | Medium | Medium-High | PASS_WITH_FRICTION |
| Proposal modification | 4-7 minutes | 2-3 minutes | 1 | High | Not applicable until revised proposal | PASS |
| Approval and execution | 2-4 minutes | Under 1 minute | 0 | High | High | PASS |
| Rejection | 1-2 minutes | Under 1 minute | 0 | High | High | PASS |
| Replay review | 5-10 minutes | 2-4 minutes | 1-2 | Medium | Medium-High | PASS_WITH_FRICTION |
| Session resume | 3-5 minutes | 1-2 minutes | 0 | High | High | PASS |
| Provider-assisted explanation | 4-7 minutes | 2-3 minutes | 0-1 | Medium-High | High | PASS_WITH_CONFIGURATION_DEPENDENCY |

## 5. Measurement Summary

### First-Time Operator

Estimated task completion:

```text
Simple approval task: 4-6 minutes
Document update: 5-8 minutes
Implementation request: 6-10 minutes
Replay review: 5-10 minutes
```

Common clarification requests:

- What does the workflow name mean?
- What is a proposal hash?
- Where do I inspect replay evidence?
- Did validation actually run?
- Is the provider explanation authoritative?

Confidence before approval:

```text
Medium-High to High
```

Confidence after execution:

```text
High
```

### Experienced Operator

Estimated task completion:

```text
Simple approval task: under 1-2 minutes
Document update: 2-3 minutes
Implementation request: 3-5 minutes
Replay review: 2-4 minutes
```

Common clarification requests:

- Which replay reference is the best audit entrypoint?
- Was provider assistance enabled or deterministic only?
- Which files changed?

Confidence before approval:

```text
High
```

Confidence after execution:

```text
High
```

## 6. Friction Points

1. Workflow identifiers are precise but technical.
2. Replay paths are visible but not self-explanatory.
3. Proposal hashes improve trust but require explanation.
4. Validation output can still feel technical.
5. Provider-assisted explanation depends on configuration and may be absent.
6. Diagnostic sections can increase output length.
7. Resume approval rules are safe but require explicit learning.
8. Modification flow is safe, but revised-proposal continuity should be made more obvious.
9. Target paths are useful but may require a simple explanation for non-technical operators.
10. Operators need a compact "what changed" summary after execution.

## 7. Confusing Terminology

Terms that remain potentially confusing:

- `GOVERNED_DEVELOPMENT_WORKFLOW`;
- proposal hash;
- replay reference;
- validation allowlist;
- worker protections;
- provider-assisted explanation;
- deterministic explanation;
- escalation level;
- artifact identifier;
- target path.

Recommended plain-language replacements or additions:

| Current Term | Plain-Language Companion |
| --- | --- |
| `GOVERNED_DEVELOPMENT_WORKFLOW` | ACLI selected the governed change process. |
| proposal hash | A fingerprint of the exact proposal you are approving. |
| replay reference | The evidence location for this step. |
| validation allowlist | The approved checks ACLI is allowed to run. |
| worker protections | Safety rules that limit repository changes. |
| provider-assisted explanation | Optional AI-written explanation; not an approval. |
| deterministic explanation | ACLI's built-in explanation. |
| escalation level | How far ACLI went to improve explanation clarity. |
| artifact identifier | The name of the document or artifact ACLI plans to create. |
| target path | Where ACLI plans to write the file. |

## 8. Unnecessary Workflow Steps

No unnecessary governance steps were identified.

Experience friction comes from presentation rather than lifecycle design.

Steps that should remain:

- proposal before mutation;
- explicit approval;
- safe resume confirmation;
- validation after execution;
- replay evidence;
- rejection and modification options.

Steps that can be made lighter:

- diagnostic output presentation;
- replay path explanation;
- validation detail formatting;
- workflow identifier display.

## 9. Top 10 Usability Improvements

1. Add a one-line plain-language status before each workflow status block.
2. Add a guided replay inspection command for non-technical operators.
3. Label replay references by purpose: proposal, approval, execution, validation, explanation.
4. Add a compact "what changed" summary after execution.
5. Add plain-language companions for workflow identifiers.
6. Add an optional concise output mode for experienced operators.
7. Keep diagnostics collapsed or visually secondary in demo-oriented output.
8. Explain proposal hash as a proposal fingerprint whenever approval is requested.
9. Make provider configuration status visible before optional provider-assisted explanation is expected.
10. After `REQUEST_MODIFICATION`, clearly label the next proposal as replacing the stopped proposal.

## 10. Production Readiness Recommendation

Recommendation:

```text
PRODUCTION_USE_READY_FOR_GUIDED_OPERATOR_MODE
```

Meaning:

ACLI is ready for production-like use by a guided operator or evaluator who has a short runbook explaining:

- approval commands;
- replay references;
- proposal hashes;
- validation status;
- provider explanation status.

Not yet recommended:

```text
UNGUIDED_GENERAL_AUDIENCE_USE
```

Reason:

The core operator journey is understandable and safe, but replay inspection and diagnostic terminology still require light onboarding.

## 11. Readiness Summary

Operator journey readiness:

```text
READY_WITH_P1_USABILITY_IMPROVEMENTS
```

First-time operator readiness:

```text
READY_WITH_RUNBOOK
```

Experienced operator readiness:

```text
READY
```

Demo readiness:

```text
READY
```

Production readiness:

```text
READY_FOR_GUIDED_OPERATOR_MODE
```

## 12. Final Verdict

```text
ACLI_REAL_WORLD_OPERATOR_VALIDATED
```

ACLI supports complete real-world operator journeys across proposal, explanation, approval, execution, validation, replay, resume, rejection, modification, and optional provider-assisted explanation. Remaining gaps are usability polish items, not blockers to guided operator use.
