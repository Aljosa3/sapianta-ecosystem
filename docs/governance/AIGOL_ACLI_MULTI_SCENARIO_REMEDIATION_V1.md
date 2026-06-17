# AIGOL ACLI Multi Scenario Remediation V1

Status: implemented remediation with rerun evidence.

Purpose: remediate the two confirmed ACLI gaps found during MSC-003 and MSC-004 execution without redesigning ACLI, HIRR, governance, replay, worker contracts, or approval boundaries.

This artifact is remediation evidence.

It does not redesign ACLI.

It does not redesign HIRR.

It does not introduce new workflow architecture.

It does not authorize provider execution.

It does not authorize worker execution.

It preserves clarification-first behavior, fail-closed behavior, approval boundaries, and replay evidence generation.

## Governing Evidence

Governing artifacts and evidence:

```text
docs/governance/AIGOL_ACLI_MULTI_SCENARIO_CERTIFICATION_V1.md
runtime/acli_multi_scenario_certification_v1/scenarios/MSC-003/replay/certification/002_certification_report.json
runtime/acli_multi_scenario_certification_v1/scenarios/MSC-004/replay/certification/002_certification_report.json
runtime/acli_multi_scenario_certification_v1/replay/certification/001_certification_matrix_update.json
runtime/acli_multi_scenario_certification_v1/replay/certification/002_aggregate_summary.json
```

Confirmed gaps:

```text
MSC-003: continuation_prompt_not_recognized_as_continuation_intent
MSC-004: advisory_followup_did_not_refine_to_ocs_llm_cognition
```

## MSC-003 Reconstruction

Prompt:

```text
Nadaljuj.
```

Expected behavior:

```text
Recognize a bare continuation prompt as continuation-specific intent.
Ask what should be continued.
Require replay-visible prior context before continuing.
Do not fabricate context.
Do not invoke provider, worker, authorization, or execution.
```

Observed failure before remediation:

```text
Intent classification: AMBIGUOUS_INTENT
Matched terms: unknown-human-intent
Workflow: HUMAN_INTENT_CLARIFICATION_INTAKE
Behavior: generic ambiguity clarification rather than continuation-specific clarification
```

Divergence point:

```text
TURN-000001 conversational CLI routing delegated to human-intent intake, but intake had no deterministic continuation-specific family for bare continuation prompts.
```

Root cause:

```text
intake classification gap
```

The routing was safely conservative, but it lost the continuation semantics needed for normal-human usability.

## MSC-004 Reconstruction

Prompt:

```text
Kaj bi bilo najbolje narediti naprej?
```

Clarification response:

```text
Give me a plan only.
```

Expected behavior:

```text
Classify the initial prompt as GENERAL_IMPROVEMENT_INTENT.
Preserve clarification-first behavior.
Refine advisory-only clarification response to OCS_LLM_COGNITION.
Do not invoke provider, worker, authorization, or execution.
```

Observed failure before remediation:

```text
Initial route: HUMAN_INTENT_CLARIFICATION_INTAKE
Selected post-clarification workflow: CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
Expected post-clarification workflow: OCS_LLM_COGNITION
```

Divergence point:

```text
TURN-000002 clarification target refinement did not recognize advisory-only wording such as "plan only" as advisory cognition routing evidence.
```

Root cause:

```text
clarification interpretation and workflow refinement signal gap
```

No execution boundary was violated. The defect was an overly narrow deterministic advisory signal set.

## Remediation Implementation

Implementation files:

```text
aigol/runtime/human_intent_clarification_intake_runtime.py
aigol/runtime/human_intent_clarification_continuity_runtime.py
tests/test_conversational_cli_runtime_v1.py
```

Minimal deterministic changes:

- Added `CONTINUATION_INTENT` to human-intent clarification intake.
- Recognized only bare continuation phrases such as `Nadaljuj.`, `continue`, `continue this`, `go on`, `resume`, and `proceed`.
- Added continuation-specific clarification questions requiring replay-visible context.
- Preserved specific existing continuation routes such as `Continue the approved AI Decision Validator domain proposal...`.
- Added Slovenian advisory phrasing for general improvement intake.
- Added advisory refinement signals including `plan`, `plan only`, `best next step`, `najbolje`, `narediti naprej`, and `naslednji korak`.
- Preserved existing fail-closed unsupported-target checks.
- Preserved approval, authorization, provider, worker, execution, governance mutation, and replay mutation boundary flags.

No new workflow contract was created.

No new worker contract was created.

No provider or worker execution path was changed.

## Regression Tests

Focused regression coverage added:

```text
Bare Slovenian continuation prompt routes to CONTINUATION_INTENT clarification.
Advisory Slovenian prompt plus "Give me a plan only." refines to OCS_LLM_COGNITION.
Existing specific governed continuation prompt remains routed to AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW.
Unsupported clarification targets still fail closed.
```

Validation performed:

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_acli_human_prompt_regression_suite_runtime_v1.py
118 passed

python -m pytest tests/test_governance_conformance.py
5 passed
```

## Rerun Evidence

Rerun root:

```text
runtime/acli_multi_scenario_remediation_v1/
```

MSC-003 evidence:

```text
runtime/acli_multi_scenario_remediation_v1/scenarios/MSC-003/replay/certification/000_remediation_evidence_package_recorded.json
runtime/acli_multi_scenario_remediation_v1/scenarios/MSC-003/replay/certification/001_remediation_replay_package_recorded.json
runtime/acli_multi_scenario_remediation_v1/scenarios/MSC-003/replay/certification/002_remediation_certification_report_recorded.json
```

MSC-004 evidence:

```text
runtime/acli_multi_scenario_remediation_v1/scenarios/MSC-004/replay/certification/000_remediation_evidence_package_recorded.json
runtime/acli_multi_scenario_remediation_v1/scenarios/MSC-004/replay/certification/001_remediation_replay_package_recorded.json
runtime/acli_multi_scenario_remediation_v1/scenarios/MSC-004/replay/certification/002_remediation_certification_report_recorded.json
```

Aggregate remediation evidence:

```text
runtime/acli_multi_scenario_remediation_v1/replay/certification/000_remediation_aggregate_report_recorded.json
```

## Rerun Results

| Scenario | Previous Gap | Remediated Observation | Verdict |
| --- | --- | --- | --- |
| MSC-003 | `Nadaljuj.` not recognized as continuation-specific intent. | `CONTINUATION_INTENT`; clarification-first; continuation-specific questions; no fabricated context; no provider, worker, authorization, or execution. | `CERTIFIED` |
| MSC-004 | Advisory follow-up did not refine to `OCS_LLM_COGNITION`. | `GENERAL_IMPROVEMENT_INTENT`; clarification-first; advisory response refined to `OCS_LLM_COGNITION`; no provider, worker, authorization, or execution. | `CERTIFIED` |

## Boundary Preservation

The rerun evidence confirms:

```text
provider_invoked = false
worker_invoked = false
authorization_created = false
execution_requested = false
approval_bypassed = false
governance_mutated = false
replay_mutated = false
```

This confirms the remediation did not weaken execution control.

## Residual Limits

The remediation is intentionally narrow.

It does not attempt to solve every possible continuation phrase.

It does not infer a previous context when the user only says `Nadaljuj.`

It does not introduce a new `REPLAY_BOUND_CONTINUATION` workflow.

It treats bare continuation as clarification-first intake until replay-visible context is supplied.

## Certification Criteria

Remediation is complete only if:

```text
MSC-003 rerun verdict = CERTIFIED
MSC-004 rerun verdict = CERTIFIED
clarification_first_behavior_preserved = true
fail_closed_behavior_preserved = true
approval_boundaries_preserved = true
replay_evidence_generated = true
regression_tests_pass = true
no new architecture introduced = true
```

All criteria are satisfied.

## Final Verdict

```text
MSC_REMEDIATION_COMPLETE
```
