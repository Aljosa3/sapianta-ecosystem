# G14_47_HUMAN_INTENT_TO_CAPABILITY_RESOLUTION_V1

Status: IMPLEMENTED

Final verdict: HUMAN_INTENT_TO_CAPABILITY_RESOLUTION_CERTIFIED

## Objective

Complete the Generation 14 Platform Core usability objective:

Humans describe goals, problems, and desired outcomes. Platform Core derives candidate capabilities.

Humans are not required to know internal Platform Core capability names, milestones, workflows, governance terminology, or implementation structure.

## Scope Boundary

This milestone changes Platform Core project services only.

It does not redesign:

- Runtime Entry;
- Governance;
- Provider Platform;
- Human Interfaces;
- Conversation Ownership.

Human Interfaces remain thin adapters that collect input and render Platform Core artifacts.

## Implementation Report

Implemented deterministic candidate capability discovery in:

`aigol/runtime/platform_core_project_services.py`

New Platform Core version marker:

`G14_47_HUMAN_INTENT_TO_CAPABILITY_RESOLUTION_V1`

New behavior:

1. Extract human objective from ordinary language.
2. Infer candidate capabilities from deterministic keyword, workspace, and certified-artifact evidence.
3. Inspect Project Workspace and Knowledge Reuse state.
4. Classify the request as:
   - `EXISTING_CAPABILITY`
   - `EXTENDS_EXISTING_CAPABILITY`
   - `NEW_CAPABILITY`
5. Ask clarification only when deterministic analysis still lacks enough goal information.

The implementation records:

- `candidate_capability_discovery`;
- `candidate_capabilities`;
- `selected_goal_target`;
- `capability_resolution_decision`;
- `human_capability_name_required: false`.

## Capability Inference Report

Deterministic inference now recognizes ordinary language for:

| Human phrase family | Inferred goal target |
|---|---|
| governance documentation, governance docs | `governance_documentation` |
| governance validation, validator | `governance_validation` |
| replay, replay evidence, replay certification | `replay` |
| certification, make certification simpler | `certification` |
| make development easier, development experience | `development_experience` |
| human intent, natural language, capability resolution | `human_intent_resolution` |
| provider attachment, provider boundary | `provider_attachment` |
| interface, aicli, aigol next, mobile interface | `human_interface` |
| this/current/previous with workspace state | `active_objective` |

Example certified outcomes:

- `I have an idea to improve governance documentation.` -> `governance_documentation`
- `I want to make development easier.` -> `development_experience`
- `Let's make certification simpler.` -> `certification`
- `Can we improve replay?` -> `replay`

No example requires the human to name an internal capability.

## Knowledge Reuse Integration Report

Knowledge Reuse now receives inferred candidate capability discovery evidence before clarification.

Evidence:

- `project_knowledge_context_from_workspace(...)` accepts `candidate_capability_discovery`.
- Knowledge Reuse records:
  - `candidate_capabilities_received`;
  - `candidate_capability_discovery`;
  - `capability_resolution_decision`.
- Relevant certified artifacts are included for inferred goal targets.
- If certified artifacts or workspace matches exist, Knowledge Reuse classifies the request as reuse/extension before asking any clarification.

For governance documentation improvement, Knowledge Reuse classifies:

`RELATES_TO_CERTIFIED_CAPABILITY`

with reuse recommended.

## Conversation Report

Clarification questions are now goal-oriented.

Allowed clarification:

- `What user-visible outcome should this development work produce?`
- `What outcome would make the improvement successful?`
- `I inferred governance documentation as the target. What outcome should this produce?`

Disallowed pattern:

- `What capability do you want?`
- `Which internal Platform Core capability should be used?`

For `I have an idea.`, Platform Core still clarifies because no deterministic target exists, but it asks for an outcome rather than an internal capability name.

## Replay Evidence

Regression replay is produced by:

`tests/test_g14_47_human_intent_to_capability_resolution_v1.py`

Real validation evidence:

- `./aicli` accepted `I have an idea to improve governance documentation.` and produced approval-ready governed development context without asking for an internal capability name.
- `python -m aigol.cli.aigol_cli next` accepted the same natural-language request in a noninteractive validation run and produced conversational replay under `/tmp/sapianta_g14_47_next_runtime/G14-47-REAL-VALIDATION/RUN-000001`.

The `aigol next` noninteractive presentation remained partially runtime-bound in that validation run, but it did not require internal capability terminology from the human.

## Regression Report

Added:

`tests/test_g14_47_human_intent_to_capability_resolution_v1.py`

Coverage proves:

- ordinary natural-language requests infer candidate capabilities;
- inferred candidates are replay-visible;
- Knowledge Reuse receives inferred candidates before clarification;
- clarification remains goal-oriented when inference is insufficient;
- `aicli` remains a thin adapter and does not own capability resolution.

Updated:

`tests/test_g14_38_platform_core_human_conversation_experience_v1.py`

The old assertion expecting capability-oriented architecture clarification was replaced with outcome-oriented wording.

## Governance Report

G14.47 preserves:

- Platform Core authority over Human Intent to Capability Resolution;
- Project Workspace authority;
- Project Guidance authority;
- Knowledge Reuse authority;
- Human Conversation Experience authority;
- Human Interface thin-adapter boundaries;
- replay-visible deterministic evidence.

Generation 14 is ready for final certification with respect to Human Intent to Capability Resolution.

