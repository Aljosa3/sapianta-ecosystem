# AIGOL_HUMAN_INTENT_CLARIFICATION_FIRST_INTAKE_V1

## Objective

Define the first Human Intent Resolution repair:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE
```

This is a design artifact only. It does not implement runtime behavior, redesign ACLI, redesign governance, redesign PPP, redesign replay, introduce provider execution, or alter worker lifecycle semantics.

## Source Evidence

This design responds to:

```text
AIGOL_HUMAN_INTENT_RESOLUTION_READINESS_AUDIT_V1
AIGOL_HUMAN_INTENT_FAILURE_TAXONOMY_V1
```

Observed failure pattern:

```text
normal human prompt
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION
-> provider dependency
-> FAILED_CLOSED risk
```

Required repair shape:

```text
normal human prompt
-> HUMAN_INTENT_CLARIFICATION_INTAKE
-> CLARIFICATION_REQUIRED
-> replay-visible clarification answer
-> re-enter workflow selection
```

## Position

The intake layer sits before `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`:

```text
Human Prompt
-> Existing high-confidence certified workflow predicates
-> HUMAN_INTENT_CLARIFICATION_INTAKE
-> Workflow Selection
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION only when no clarification-worthy human intent exists
```

The intake layer must not override explicit high-confidence certified commands, lifecycle continuations, authorization continuations, worker continuations, or policy fail-closed conditions.

## Human Intent Intake Model

The intake model deterministically classifies normal-human prompts into one of:

```text
BUSINESS_GOAL_INTENT
PROBLEM_STATEMENT_INTENT
AUTOMATION_INTENT
COMPLIANCE_INTENT
HR_INTENT
DECISION_REVIEW_INTENT
OPERATIONAL_INTENT
AI_OVERSIGHT_INTENT
AMBIGUOUS_INTENT
NO_CLARIFICATION_INTAKE_MATCH
```

The output is a replay-visible artifact:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE_ARTIFACT_V1
```

Required fields:

```text
artifact_type
intake_id
prompt_id
human_prompt_hash
canonical_chain_id
intent_family
intent_confidence
intent_signals
clarification_required
clarification_questions
expected_workflow_targets
routing_decision
provider_invoked
worker_invoked
authorization_created
execution_requested
approval_bypassed
governance_mutated
replay_mutated
failure_reason
created_at
replay_reference
artifact_hash
```

Invariant fields:

```text
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
approval_bypassed = false
governance_mutated = false
replay_mutated = false
```

## Intent Family Mappings

| Intent family | Intent signals | Clarification questions | Expected workflow targets |
|---|---|---|---|
| `BUSINESS_GOAL_INTENT` | build/start/create a tool or system; trust AI recommendations; check automated decisions; review AI suggestions; reduce AI mistakes; customer-impacting AI | What kind of AI output or decision should be reviewed first? Who is affected by the decision? Is the immediate goal planning, evidence design, or a governed implementation request? | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`, later Product 1 intake if applicable |
| `PROBLEM_STATEMENT_INTENT` | AI contradicts policy; inconsistent AI answers; cannot explain recommendation; risky AI answers; missing review; unreliable AI review process | What problem should the first governed workflow address? Which team or process is affected? What evidence would show the problem is controlled? | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` |
| `AUTOMATION_INTENT` | automate review; flag incomplete outputs; screen decisions; collect evidence; stop bad suggestions; review before approval | What should be checked automatically? What should happen when a check fails? Should this create a proposal, an evidence model, or an execution request after human approval? | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` |
| `COMPLIANCE_INTENT` | auditors; regulators; proof; records; internal audit; controlled customer-impacting AI; rules; evidence | What compliance or audit evidence is needed? Which AI decision or output is in scope? Is this for internal review, external audit preparation, or controlled workflow design? | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` |
| `HR_INTENT` | hiring; recruitment; employee evaluation; performance feedback; promotion; HR AI safeguards; fairness | Which HR decision or recommendation is in scope? Should the workflow review AI output, collect evidence, or require human approval before use? What sensitivity or fairness concern must be preserved? | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` |
| `DECISION_REVIEW_INTENT` | approve/reject AI recommendation; decide when AI output is trustworthy; required evidence; checklist; review flow; acceptable AI decision | What type of AI recommendation should be reviewed? What evidence should be required before approval? Who confirms or rejects the recommendation? | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` |
| `OPERATIONAL_INTENT` | supplier actions; production schedules; service tickets; dispatch; warehouse planning; operational managers; routine workflow recommendations | Which operational workflow is affected? What AI recommendation needs review? What should be blocked until a person confirms it? | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` |
| `AI_OVERSIGHT_INTENT` | rules for AI use; supervise AI tools; controls; review enforcement; track checked outputs; guardrails; prevent unchecked AI work | What AI use should be supervised first? Should ACLI help define controls, evidence requirements, or an approval workflow? What risk should the first workflow reduce? | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` |
| `AMBIGUOUS_INTENT` | help with AI; build something for my business; better decisions; make this safer; get started; intelligent system; improve our process; quality problem | What are you trying to improve or control? Does this involve AI outputs, human approval, compliance evidence, or operational decisions? Should we start with planning, clarification, or a governed workflow proposal? | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` after clarification |

## Clarification Model

Clarification is deterministic and first-class.

Required statuses:

```text
CLARIFICATION_REQUIRED
CLARIFICATION_NOT_REQUIRED
FAILED_CLOSED
```

Clarification is required when:

```text
intent_family != NO_CLARIFICATION_INTAKE_MATCH
and intent_confidence in {LOW, MEDIUM, HIGH}
and no higher-priority certified workflow has already been selected
```

Low-confidence behavior:

```text
LOW confidence
-> CLARIFICATION_REQUIRED
```

Unknown intent behavior:

```text
Unknown normal-human intent
-> CLARIFICATION_REQUIRED
```

Ambiguous intent behavior:

```text
Ambiguous intent
-> CLARIFICATION_REQUIRED
```

The intake layer must not use a provider to generate clarification questions. Questions are selected from deterministic templates by intent family.

## Routing Decision Model

The intake layer emits a routing decision, not an execution decision.

Possible routing decisions:

```text
HUMAN_INTENT_CLARIFICATION_REQUIRED
HUMAN_INTENT_NO_MATCH_CONTINUE_TO_EXISTING_FALLBACK
HUMAN_INTENT_FAILED_CLOSED_POLICY_VIOLATION
```

Primary route:

```text
HUMAN_INTENT_CLARIFICATION_REQUIRED
-> CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

For general improvement prompts that are clearly advisory and non-operational, a later implementation may route to:

```text
OCS_LLM_COGNITION
```

However, the first repair should prioritize clarification over advisory routing when the prompt includes business process, AI decision, approval, evidence, HR, compliance, or operational impact signals.

## Replay Requirements

The intake must be replay-visible and deterministic.

Replay steps:

```text
000_human_intent_clarification_intake_recorded.json
001_human_intent_clarification_questions_recorded.json
002_human_intent_clarification_routing_returned.json
```

Replay invariants:

```text
stable prompt hash
stable intent family
stable matched signals
stable clarification questions
stable expected workflow target list
stable routing decision
artifact hashes verified on reconstruction
step ordering verified on reconstruction
```

Replay must prove:

```text
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
approval_bypassed = false
governance_mutated = false
replay_mutated = false
```

## Fail-Closed Requirements

The intake must preserve fail-closed behavior for real boundary violations.

Fail closed when:

```text
human_prompt is missing or empty
replay artifact hash mismatches
replay step ordering mismatches
existing replay path would be overwritten
policy violation is detected
prompt requests unrestricted autonomous action
prompt requests governance bypass
prompt requests approval bypass
prompt requests execution without authorization
prompt requests hidden or non-replayable mutation
```

Do not fail closed merely because:

```text
intent is unknown
intent is ambiguous
intent is low confidence
prompt uses normal business language
prompt lacks domain/capability/artifact/milestone terminology
prompt is non-English but contains human-intent signals
```

Those cases must return:

```text
CLARIFICATION_REQUIRED
```

## Failed-Closed Reduction Strategy

The repair reduces failed-closed outcomes by moving normal-human prompts away from provider fallback:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
-> provider dependency
-> FAILED_CLOSED risk
```

becomes:

```text
HUMAN_INTENT_CLARIFICATION_INTAKE
-> deterministic clarification
-> replay-visible continuation
-> re-enter workflow selection
```

Expected first impact on HIRR:

```text
Ambiguous prompts clarified correctly: 0/10 -> target 10/10
Provider fallback for known intent families: 97/100 -> target materially reduced
HIRR score: 1 -> target increase through clarification correctness before execution expansion
```

## Non-Goals

This design does not:

- create execution authorization;
- invoke a worker;
- invoke a provider;
- auto-create domains;
- auto-create capabilities;
- auto-create Product 1 artifacts;
- bypass PPP;
- bypass human approval;
- mutate governance;
- mutate replay;
- remove `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`;
- redesign certified workflows.

## Implementation Readiness Notes

Minimal implementation surface for a future repair:

1. Add a deterministic `human_intent_clarification_intake_runtime`.
2. Register `HUMAN_INTENT_CLARIFICATION_INTAKE` in ACLI workflow selection.
3. Call it immediately before `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`.
4. Add replay reconstruction tests.
5. Add HIRR corpus regression tests for all nine clarification-first families.

## Final Fields

```text
HUMAN_INTENT_INTAKE_DEFINED = YES
CLARIFICATION_FIRST_MODEL_DEFINED = YES
INTENT_FAMILY_MAPPINGS_DEFINED = YES
LOW_CONFIDENCE_BEHAVIOR_DEFINED = YES
FAILED_CLOSED_REDUCTION_STRATEGY_DEFINED = YES
HIRR_REPAIR_READY = YES
```
