# G14-08 Project Knowledge Reuse And Contextual Task Mapping V1

Status: project knowledge reuse implemented.

Final verdict: PROJECT_KNOWLEDGE_REUSE_CERTIFIED

## 1. Executive Summary

G14-07 certified goal-oriented development through AiGOL Next.

G14-08 adds deterministic project knowledge reuse before new governed implementation work is created.

When an operator submits a new development goal, AiGOL Next now evaluates the goal against the persistent Project Workspace. The interface identifies whether the goal relates to known project work, modifies an existing capability, extends an existing milestone, appears already satisfied, or requires new governed work.

The implementation preserves the certified Platform Core architecture. AiGOL Next remains a thin conversational adapter and does not perform orchestration, Governance authorization, Worker execution, Provider execution, or Replay ownership.

## 2. Project Knowledge Reuse Implementation

The persistent workspace state now records a deterministic `project_knowledge_index`.

The index records:

- known goal targets;
- certified artifacts related to each target;
- related milestones by target;
- implementation history matches by target;
- explicit evidence that conversation history is not authoritative;
- approval and non-execution flags.

The index is derived from deterministic workspace state and pending governed summaries, not from free-form conversation history alone.

## 3. Contextual Task Mapping Model

Each goal-oriented mapping now includes `contextual_task_mapping`.

The contextual mapping records:

| Field | Meaning |
| --- | --- |
| `classification` | Deterministic relationship between the new goal and workspace knowledge. |
| `workspace_inspected` | Confirms Project Workspace inspection occurred. |
| `related_milestones` | Workspace milestones related to the goal target. |
| `relevant_certified_artifacts` | Certified artifacts related to the goal target. |
| `implementation_history_matches` | Prior governed work related to the target. |
| `reuse_recommended` | Whether existing knowledge should be reused. |
| `duplicate_work_avoided` | Whether the request appears already satisfied. |
| `new_work_required` | Whether governed work remains necessary. |

Supported classifications:

```text
RELATES_TO_CERTIFIED_CAPABILITY
ALREADY_SATISFIED
MODIFIES_EXISTING_CAPABILITY
EXTENDS_EXISTING_MILESTONE
NEW_GOVERNED_WORK
```

## 4. Runtime Evidence

Validated scenario 1:

```text
I want AiGOL Next to support GitHub Actions.
/send
exit
```

Observed evidence:

```text
contextual_task_mapping:
classification: RELATES_TO_CERTIFIED_CAPABILITY
workspace_inspected: True
reuse_recommended: True
knowledge_reuse_count: 1
```

Workspace evidence:

```text
project_knowledge_index.knowledge_source: deterministic_workspace_state
project_knowledge_index.known_goal_targets: github_actions
project_knowledge_index.conversation_history_is_authority: False
project_knowledge_index.acli_next_executes_recommendation: False
```

Validated scenario 2:

```text
I want AiGOL Next to support GitHub Actions. It is already implemented.
Let's improve GitHub Actions support.
Continue GitHub Actions support.
I want AiGOL Next to support release notes.
```

Observed classifications:

```text
ALREADY_SATISFIED
MODIFIES_EXISTING_CAPABILITY
EXTENDS_EXISTING_MILESTONE
NEW_GOVERNED_WORK
```

Observed reuse evidence:

```text
duplicate_work_avoided: True
implementation_history_matches: Add GitHub Actions support.
knowledge_reuse_count: 4
runtime_bound_count: 0
```

No recommendation was executed automatically.

## 5. Replay Evidence

The project knowledge index is persisted inside the replay-visible workspace state artifact:

```text
workspace_state/*_acli_next_workspace_state_recorded.json
```

Contextual mappings are persisted inside pending implementation summaries. Approved work still enters the certified runtime only after explicit human confirmation.

## 6. Ownership Verification

| Component | Certified responsibility | Result |
| --- | --- | --- |
| AiGOL Next | Conversational UX, workspace presentation, contextual recommendation, approval gating | Preserved |
| PGSP | Governed interface attachment and session invocation boundary | Preserved |
| UBTR | Semantic interpretation and normalization | Preserved |
| CSA | Structured intent handling | Preserved |
| Platform Core / OCS | Runtime orchestration and workflow progression | Preserved |
| Governance | Authorization and decisions | Preserved |
| Provider Platform | Provider identity and invocation boundary | Preserved |
| Worker Platform | Worker execution lifecycle | Preserved |
| Replay | Evidence and reconstruction | Preserved |
| Platform Digital Twin | Canonical architectural evidence source | Preserved |
| Architectural Health | Deterministic advisory review | Preserved |

No responsibility moved into AiGOL Next.

## 7. Readiness Assessment

AiGOL Next now evaluates new goals against deterministic workspace knowledge before creating new governed work.

The validated behavior supports:

- extension of existing milestone work;
- modification of existing capability work;
- recognition of already satisfied requests;
- relationship to certified capability artifacts;
- creation of new governed work when no deterministic match exists.

Future refinements may broaden the goal taxonomy and enrich the deterministic workspace index, but the core project knowledge reuse capability is operational.

## 8. Validation Evidence

Validation performed:

```text
python -m py_compile aigol/acli_next/conversational.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g14_08_project_knowledge_reuse_v1.py tests/test_g14_07_goal_oriented_development_experience_v1.py tests/test_g14_06_project_guidance_assistant_v1.py tests/test_g14_05_persistent_development_workspace_v1.py tests/test_g14_04_conversational_development_workflow_v1.py tests/test_g14_03_aigol_next_runtime_binding_v1.py tests/test_g11_acli_next_conversational_session.py -q
git diff --check
```

Observed test result:

```text
19 passed
```

Final verdict: PROJECT_KNOWLEDGE_REUSE_CERTIFIED
