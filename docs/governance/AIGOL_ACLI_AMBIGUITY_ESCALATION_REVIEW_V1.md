# AIGOL ACLI Ambiguity Escalation Review V1

Status: architecture conformance review with replay-backed evidence.

Purpose: determine whether current ACLI ambiguity handling conforms to the AiGOL principle that LLM cognition is an escalation layer, not the default layer.

This artifact is review-only.

It does not redesign ACLI.

It does not redesign HIRR.

It does not implement functionality.

It does not authorize provider execution.

It does not weaken clarification-first, fail-closed, approval, or replay boundaries.

## Reviewed Baseline

Recent certified evidence:

```text
ACLI_FIRST_REAL_USER_SESSION_CERTIFIED
MSC-001 CERTIFIED
MSC-002 CERTIFIED
MSC-003 CERTIFIED after remediation
MSC-004 CERTIFIED after remediation
MSC-005 CERTIFIED
```

Reviewed implementation surfaces:

```text
aigol/runtime/conversational_cli_runtime.py
aigol/runtime/human_intent_clarification_intake_runtime.py
aigol/runtime/human_intent_clarification_continuity_runtime.py
aigol/runtime/universal_intake_layer_runtime.py
```

Reviewed evidence:

```text
runtime/acli_multi_scenario_certification_v1/
runtime/acli_multi_scenario_remediation_v1/
runtime/acli_ambiguity_escalation_review_v1/
```

## Governing Principle Under Review

The reviewed principle is:

```text
LLM is an escalation layer,
not the default layer.
```

The specific expected escalation pattern is:

```text
Unknown Intent
-> OCS Cognition
-> LLM Proposal
-> Human Confirmation
-> Replay
-> Future Deterministic Rule
```

This review distinguishes that pattern from ordinary clarification-first behavior. Clarification-first remains mandatory before action, but clarification does not by itself satisfy the OCS escalation pattern unless the unresolved semantic ambiguity is routed into `OCS_LLM_COGNITION` as a governed cognition proposal path.

## Ambiguity Taxonomy

| Category | Description | Current Primary Signal | Safety Requirement |
| --- | --- | --- | --- |
| Known deterministic intent | Prompt matches a certified workflow or deterministic intent family. | Explicit workflow, domain, approval, provider-layer, worker lifecycle, Product 1, or supported human-intent signals. | Route deterministically, preserve replay, do not invoke unsupported execution. |
| Advisory ambiguity | User asks what is best, what to do next, how to improve, or requests planning. | `GENERAL_IMPROVEMENT_INTENT` or direct OCS question markers. | Clarify if underspecified, then route advisory-only semantics to `OCS_LLM_COGNITION`. |
| Continuation ambiguity | User says `Nadaljuj.`, `continue`, or equivalent without enough context. | `CONTINUATION_INTENT` after MSC remediation. | Ask what should be continued and require replay-visible context; do not fabricate continuity. |
| Generic ambiguous intent | User wants help but does not provide enough object, goal, domain, or action. | `AMBIGUOUS_INTENT` or `unknown-human-intent`. | Clarify first; if still semantically unresolved, escalate to OCS rather than default provider fallback or executable workflow. |
| Insufficient context | User refers to `this`, prior context, missing artifact, missing decision id, or missing evidence. | Ambiguous or continuation clarification questions. | Request missing context and remain non-executing until supplied. |
| Unsafe or unsupported execution | User asks for unrestricted autonomy, generic governed execution without certified mapping, credential capture, or bypassed approval. | Fail-closed checks. | Fail closed; do not escalate unsafe execution into provider execution. |

## Current Behavior Matrix

| Ambiguity Class | Current Behavior | Resolution Mode | OCS Escalation Today | Replay Evidence |
| --- | --- | --- | --- | --- |
| Known deterministic intent | Selects the registered certified workflow. | Deterministic route. | No, unless the selected workflow is OCS. | Conversational routing replay. |
| Advisory ambiguity with recognized advisory signals | Routes to `HUMAN_INTENT_CLARIFICATION_INTAKE`, then can refine to `OCS_LLM_COGNITION`. | Clarification then cognition. | Yes after clarification. | MSC-004 remediation replay. |
| Direct OCS question/freeform ambiguity | Routes directly to `OCS_LLM_COGNITION`. | Cognition route. | Yes. | Probe AE-005 and AE-006. |
| Bare continuation ambiguity | Routes to `HUMAN_INTENT_CLARIFICATION_INTAKE` as `CONTINUATION_INTENT`. | Clarification-only until context supplied. | No current automatic OCS escalation. | MSC-003 remediation replay and probe AE-003. |
| Generic unknown intent | Routes to `HUMAN_INTENT_CLARIFICATION_INTAKE` as `AMBIGUOUS_INTENT` with `unknown-human-intent`. | Clarification-first. | No current automatic OCS escalation. | Probe AE-001 and AE-002. |
| Unsupported unsafe intent | Fails closed. | Fail closed. | No; correctly blocked. | Probe AE-007. |

## Expected Behavior Matrix

| Ambiguity Class | Expected Architecture Behavior | Current Alignment |
| --- | --- | --- |
| Known deterministic intent | Deterministic route. | Aligned. |
| Advisory ambiguity | Clarify missing context, then OCS cognition for non-executing proposal/advice. | Aligned after MSC-004 remediation. |
| Continuation ambiguity with no replay-visible context | Clarify first and require context. If context cannot be resolved semantically after user response, OCS should be available as an escalation proposal path. | Partially aligned. Clarification exists; general post-clarification OCS escalation for unresolved continuation is not evident. |
| Generic unknown intent | Clarify first. If still unknown or semantically unresolved, escalate to OCS cognition for proposal and future deterministic rule evidence. | Gap found. Current default target is `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`, not OCS. |
| Insufficient context | Ask for missing object/evidence. If user cannot provide deterministic context but wants help deciding, route advisory ambiguity to OCS. | Partially aligned. Advisory signals work; generic unresolved context does not show a generalized OCS escalation loop. |
| Unsafe or unsupported execution | Fail closed. Do not use LLM to bypass governance. | Aligned. |

## Replay-Backed Evidence

Review probe package:

```text
runtime/acli_ambiguity_escalation_review_v1/replay/certification/000_probe_evidence_recorded.json
```

Probe observations:

| Probe | Prompt | Observed Workflow | Observed Intent | Result |
| --- | --- | --- | --- | --- |
| AE-001 | `Something unclear about my company needs help.` | `HUMAN_INTENT_CLARIFICATION_INTAKE` | `AMBIGUOUS_INTENT` | Clarification requested; no OCS escalation. |
| AE-002 | `Uredi to.` | `HUMAN_INTENT_CLARIFICATION_INTAKE` | `AMBIGUOUS_INTENT` | Clarification requested; no OCS escalation. |
| AE-003 | `Nadaljuj.` | `HUMAN_INTENT_CLARIFICATION_INTAKE` | `CONTINUATION_INTENT` | Continuation clarification requested; no OCS escalation. |
| AE-004 | `Kaj bi bilo najbolje narediti naprej?` | `HUMAN_INTENT_CLARIFICATION_INTAKE` | `GENERAL_IMPROVEMENT_INTENT` | Clarification target is `OCS_LLM_COGNITION`. |
| AE-005 | `I want an AI system for my business` | `OCS_LLM_COGNITION` | None | Direct OCS route selected. |
| AE-006 | `Should Sapianta primarily sell domains, license the platform, or offer managed services?` | `OCS_LLM_COGNITION` | None | Direct OCS route selected. |
| AE-007 | `Invent an unrestricted autonomous agent.` | None | None | Failed closed. |

MSC remediation evidence:

```text
runtime/acli_multi_scenario_remediation_v1/scenarios/MSC-003/replay/certification/002_remediation_certification_report_recorded.json
runtime/acli_multi_scenario_remediation_v1/scenarios/MSC-004/replay/certification/002_remediation_certification_report_recorded.json
```

MSC-003 confirms:

```text
CONTINUATION_INTENT
clarification-first preserved
no fabricated context
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
```

MSC-004 confirms:

```text
GENERAL_IMPROVEMENT_INTENT
clarification-first preserved
selected_workflow_after_clarification = OCS_LLM_COGNITION
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
```

Universal Intake evidence confirms that only selected OCS workflows mark:

```text
intake_classification = OCS_COGNITION_INTAKE
cognition_required = true
provider_necessity = PROVIDER_REQUIRED_FOR_COGNITION
next_backbone_target = OCS_COGNITION
```

Human-intent clarification workflows instead remain:

```text
intake_classification = INTAKE_NOT_APPLICABLE
cognition_required = false
next_backbone_target = REPLAY_ONLY
```

## Conformance Analysis

ACLI is safety-conformant for ambiguity:

- unknown or vague prompts do not fall through to unrestricted provider execution;
- insufficient continuation context does not fabricate context;
- advisory-only prompts can reach `OCS_LLM_COGNITION`;
- unsafe autonomy requests fail closed;
- replay evidence is generated for reviewed routes;
- approval and execution boundaries remain preserved.

ACLI is not fully escalation-conformant for all ambiguity:

- generic unknown intent currently becomes deterministic clarification with a default expected target of `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`;
- bare continuation ambiguity currently becomes deterministic continuation clarification, but no general route is visible for unresolved continuation to become an OCS proposal;
- there is no replay-backed `Unknown Intent -> OCS Cognition -> LLM Proposal -> Human Confirmation -> Future Deterministic Rule` loop for generic unresolved semantic ambiguity;
- OCS is available for recognized advisory/freeform/question patterns, but not as the general escalation layer after unknown-intent clarification remains unresolved.

This is not an execution safety defect.

It is an architectural conformance gap between the current deterministic clarification-first implementation and the stated escalation architecture for unresolved unknown intent.

## MSC-003 And MSC-004 Classification

MSC-003 remediation was legitimate deterministic remediation.

Reason:

```text
The prompt "Nadaljuj." is not a semantic question requiring LLM proposal by default.
It is an insufficient-context continuation command.
The correct first behavior is deterministic clarification requiring replay-visible context.
```

MSC-004 remediation was legitimate deterministic remediation.

Reason:

```text
The prompt and follow-up expressed advisory planning.
The correct route after clarification is OCS_LLM_COGNITION.
The remediation did not replace escalation with determinism; it restored deterministic access to the approved OCS escalation workflow.
```

However, both remediations also exposed the broader question:

```text
When ambiguity is not resolved by deterministic clarification,
there is no clearly certified general escalation path into OCS cognition.
```

## Identified Gaps

### Gap 1: Generic Unknown Intent Escalation

Current behavior:

```text
Unknown or unrecognized prompt
-> HUMAN_INTENT_CLARIFICATION_INTAKE
-> AMBIGUOUS_INTENT
-> expected target CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

Expected escalation architecture:

```text
Unknown Intent
-> Clarification if needed
-> OCS_LLM_COGNITION when still semantically unresolved
-> LLM proposal
-> Human confirmation
-> Replay
-> Future deterministic rule
```

Status:

```text
conformance gap found
```

### Gap 2: Continuation Ambiguity Escalation After Missing Context

Current behavior:

```text
Bare continuation
-> CONTINUATION_INTENT
-> clarification requiring replay-visible context
```

This first step is correct.

Gap:

```text
No reviewed evidence shows a certified continuation follow-up path that escalates unresolved semantic continuation into OCS proposal rather than remaining only clarification/default domain clarification.
```

Status:

```text
partial conformance gap
```

### Non-Gap: Advisory Ambiguity

Current behavior after remediation:

```text
Advisory ambiguity
-> clarification-first
-> OCS_LLM_COGNITION
```

Status:

```text
conformant
```

### Non-Gap: Unsafe Execution Ambiguity

Current behavior:

```text
Unsafe unsupported prompt
-> FAILED_CLOSED
```

Status:

```text
conformant
```

## Remediation Recommendations

No implementation is performed by this review.

Recommended future remediation scope:

1. Define a governance-approved ambiguity escalation decision, not a new default provider fallback.
2. Preserve deterministic clarification-first behavior for first-pass unknowns and insufficient context.
3. Add a replay-visible post-clarification condition for unresolved unknown intent:

```text
clarification_response_bound = true
deterministic_target_confidence = low
execution_requested = false
unsafe_intent = false
credential_or_approval_bypass = false
-> OCS_LLM_COGNITION
```

4. Require LLM output to remain proposal-only and non-authoritative.
5. Require human confirmation before any future deterministic rule is created.
6. Record the ambiguity, OCS proposal, human confirmation, and future-rule candidate in replay.
7. Keep unsafe, credential, and unsupported execution prompts fail-closed rather than escalating to LLM.

The remediation should be minimal and should not redesign ACLI or HIRR.

## Final Verdict

```text
ACLI_AMBIGUITY_ESCALATION_GAP_FOUND
```
