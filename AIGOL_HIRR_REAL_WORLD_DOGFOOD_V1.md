# AIGOL_HIRR_REAL_WORLD_DOGFOOD_V1

Status: completed.

## Objective

Validate `HUMAN_INTENT_RESOLUTION_READY` using real AiGOL development work instead of the synthetic HIRR corpus.

## Method

The dogfood run used ACLI as the primary interface:

```text
python -m aigol.cli.aigol_cli conversation
```

Because ACLI runs in multi-line mode in this environment, each operator turn was terminated with a single `.` line.

Persistent evidence root:

```text
/tmp/aigol_hirr_real_world_dogfood_v1
```

Structured run summary:

```text
/tmp/aigol_hirr_real_world_dogfood_v1/results.json
```

Replay evidence observed:

```text
20 turn directories
2 turns per session
conversational_cli_routing artifacts present
human_intent_clarification_continuity artifacts present for clarification-continuation cases
ocs_llm_cognition_end_to_end artifacts present for the direct OCS case
```

## Results

| Session | Human Prompt | Clarification Response | Expected Workflow | Actual Workflow | Outcome | Replay Root |
| --- | --- | --- | --- | --- | --- | --- |
| REAL-HIRR-001 | I want to improve how AiGOL handles normal human requests before they become governed work. | Keep this advisory first: identify the next safest routing improvement and preserve replay evidence before any implementation. | `OCS_LLM_COGNITION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | MISROUTED | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-001/runtime/REAL-HIRR-001` |
| REAL-HIRR-002 | ACLI misunderstood broad improvement requests last time. How should we reduce that risk? | Analyze the routing failure and recommend a safer clarification path before changing runtime behavior. | `OCS_LLM_COGNITION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | MISROUTED | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-002/runtime/REAL-HIRR-002` |
| REAL-HIRR-003 | We need a repeatable check that catches HIRR routing regressions before release. | Create a governed workflow proposal for automatically checking HIRR corpus routing and reporting evidence. | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | SUCCESS | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-003/runtime/REAL-HIRR-003` |
| REAL-HIRR-004 | Help define evidence that proves advisory routing did not bypass governance. | Define audit evidence for advisory routing decisions, replay lineage, and no provider or worker invocation. | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | SUCCESS | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-004/runtime/REAL-HIRR-004` |
| REAL-HIRR-005 | I want to build a small operator view for human intent routing health. | Start with a governed implementation proposal for showing routing outcomes, clarification status, and replay references. | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | SUCCESS | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-005/runtime/REAL-HIRR-005` |
| REAL-HIRR-006 | Make it easier for a product manager to understand why ACLI asked a clarification question. | Give advisory guidance for wording and evidence visibility; do not start implementation yet. | `OCS_LLM_COGNITION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | MISROUTED | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-006/runtime/REAL-HIRR-006` |
| REAL-HIRR-007 | Our validation reports are hard to compare across HIRR runs. | Define the first governed workflow for comparing HIRR run results and preserving the comparison evidence. | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | SUCCESS | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-007/runtime/REAL-HIRR-007` |
| REAL-HIRR-008 | Can we collect evidence whenever a clarification response changes the selected workflow? | Create a governed evidence model for clarification response binding and selected workflow changes. | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | SUCCESS | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-008/runtime/REAL-HIRR-008` |
| REAL-HIRR-009 | What should be the first step for safer Product 1 decision review? | Keep this advisory and recommend the next Product 1 planning step for AI decision review, without execution. | `OCS_LLM_COGNITION` | `OCS_LLM_COGNITION` | FAILED_CLOSED | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-009/runtime/REAL-HIRR-009` |
| REAL-HIRR-010 | I need help making the governed workflow path more understandable to new operators. | I want operator-facing guidance for the clarification-to-workflow path before any runtime changes. | `OCS_LLM_COGNITION` | `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | MISROUTED | `/tmp/aigol_hirr_real_world_dogfood_v1/REAL-HIRR-010/runtime/REAL-HIRR-010` |

## Observations

Synthetic HIRR readiness did not fully transfer to real AiGOL development prompts.

The clarification-first intake behaved safely for most prompts:

- unknown or broad prompts were clarified instead of routed to provider fallback;
- replay-visible clarification state was created;
- clarification responses were bound to the same chain;
- no provider or worker invocation was introduced by HIRR continuity.

However, real operator clarification responses exposed a remaining routing limitation:

```text
AMBIGUOUS_INTENT
-> clarification response says advisory/planning/no implementation
-> selected workflow remains CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
```

This means continuation currently preserves the initial target from the first-turn intent family instead of re-resolving the workflow target from the clarification response.

One direct OCS prompt selected the expected workflow but failed closed inside OCS cognition:

```text
FAILED_CLOSED:
cognition comparison failed closed: at least two cognition artifacts are required for comparison
```

## Clarification Quality

Clarification quality was acceptable for governed implementation/evidence prompts.

Clarification quality was insufficient for advisory prompts that begin ambiguous and become advisory only after the operator response. The system preserves continuity, but the second-turn content does not currently change the workflow target.

## Root Cause

Primary root cause:

```text
Clarification continuation selects the first-turn expected_workflow_targets and does not re-evaluate advisory intent from the clarification response.
```

Secondary root cause:

```text
Direct OCS advisory routing can fail closed when the OCS cognition path lacks the comparison artifact set required by its runtime.
```

## Recommended Repair Order

1. Add deterministic clarification-response target refinement for `AMBIGUOUS_INTENT` so advisory/planning/no-implementation replies can select `OCS_LLM_COGNITION`.
2. Add focused real-world regression prompts covering ambiguous-to-advisory clarification.
3. Audit the direct OCS cognition fail-closed path for advisory prompts that have one cognition artifact instead of the comparison-required artifact set.

## Final Fields

```text
REAL_PROMPTS_TESTED = 10
INTENTS_RESOLVED = 6
MISROUTINGS = 4
FAILED_CLOSED = 1
HUMAN_CORRECTIONS_REQUIRED = 5
HIRR_REAL_WORLD_SUCCESS_RATE = 50
PRIMARY_INTERFACE_ACCEPTED = NO
NEXT_HIGHEST_LEVERAGE_REPAIR = Add clarification-response workflow target refinement for ambiguous-to-advisory human intent.
```
