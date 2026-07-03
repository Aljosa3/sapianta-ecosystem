# G14-07A Unified Human Interface Thin Adapter Audit V1

Status: responsibility drift detected.

Final verdict: UNIFIED_HUMAN_INTERFACE_RESPONSIBILITY_DRIFT_DETECTED

## 1. Executive Summary

This audit reviews the Generation 14 implementation after:

- G14-03 Runtime Binding;
- G14-04 Conversational Development Workflow;
- G14-05 Persistent Development Workspace;
- G14-06 Project Guidance;
- G14-07 Goal-Oriented Development;
- G14-08 Project Knowledge Reuse.

Generation 14.01 certified the Unified Human Interface architecture. That architecture requires AiGOL Next, Web, Android, Voice, REST, Desktop, and future human interfaces to remain thin adapters over the same PGSP-bound runtime.

Audit finding:

```text
runtime execution delegation remains preserved, but project workspace, project guidance, goal mapping, and knowledge reuse logic currently reside inside AiGOL Next
```

This is not an execution-authority violation. AiGOL Next does not execute Workers, authorize Governance, invoke Providers directly, own Replay, or replace Platform Core runtime execution.

However, the implementation does contain reusable project and contextual task logic inside the CLI adapter. Under the G14-01 invariant, this is responsibility drift because future Web, Android, Voice, REST, and Desktop interfaces could not reuse the capability unchanged without copying AiGOL Next business logic.

## 2. Architectural Baseline

G14-01 defines all human interfaces as thin adapters.

Interfaces may own:

- human input capture;
- presentation;
- local UI state;
- session rendering;
- approval and clarification collection.

Interfaces must not own:

- semantic interpretation;
- intent resolution;
- workflow orchestration;
- project knowledge authority;
- project workspace authority;
- contextual task mapping;
- milestone planning;
- implementation planning;
- Governance;
- Provider selection;
- Worker execution;
- Replay authority.

Canonical runtime:

```text
Human Interface
-> PGSP
-> UBTR
-> CSA
-> Platform Core / OCS
-> Governance
-> Providers
-> Workers
-> Replay
```

## 3. Human Interface Responsibility Matrix

| Capability | Current implementation location | Evidence | Classification |
| --- | --- | --- | --- |
| Message composition | `aigol/acli_next/conversational.py` REPL buffer and `/send`, `/preview`, `/clear`, `/cancel` handling | Local buffer, command parsing, and prompt rendering in `run_acli_next_persistent_conversational_session(...)` | Correct Human Interface Responsibility |
| Approval collection | `aigol/acli_next/conversational.py` `/approve` branch | Collects human confirmation, then delegates to `turn_runner` | Correct Human Interface Responsibility |
| Runtime binding | `aigol/cli/aigol_cli.py` `_run_acli_next_runtime_bound_session(...)` | Calls `run_interactive_conversation(...)` after confirmation and records runtime status | Presentation Logic / Delegation |
| Conversational clarification questions | `aigol/acli_next/conversational.py` `_guided_development_clarification_required(...)` and `_guided_development_clarification(...)` | Determines whether clarification is needed and creates questions in AiGOL Next | Platform Service Candidate |
| Persistent workspace snapshot | `aigol/acli_next/conversational.py` `_persistent_workspace_state_artifact(...)` | Creates active objective, pending approval, history, guidance, and knowledge index | Responsibility Drift |
| Project guidance | `aigol/acli_next/conversational.py` `_project_guidance_model(...)` | Computes generation, milestone, pending work, recommended next action | Responsibility Drift |
| Goal-oriented mapping | `aigol/acli_next/conversational.py` `_goal_mapping_from_workspace(...)` | Maps natural goals such as GitHub Actions, deployment, and mobile interface to governed requests | Responsibility Drift |
| Project knowledge reuse | `aigol/acli_next/conversational.py` `_project_knowledge_index_model(...)` and `_project_knowledge_context_from_workspace(...)` | Computes known targets, related artifacts, duplicate avoidance, and contextual classifications | Responsibility Drift |
| Summary rendering | `aigol/acli_next/conversational.py` `_render_guided_development_summary(...)` | Displays existing summary and mapping fields | Presentation Logic |
| Replay display references | `aigol/acli_next/conversational.py` renderers | Displays replay references produced by runtime artifacts | Correct Human Interface Responsibility |

## 4. Runtime Binding Audit

Runtime binding remains a delegation layer.

Implementation evidence:

```text
_run_acli_next_runtime_bound_session(...)
```

The function first creates an ACLI Next presentation artifact, then invokes:

```text
run_interactive_conversation(...)
```

The result records:

- `governance_authorization_reached`;
- `provider_invocation_reached`;
- `worker_execution_reached`;
- `replay_certification_reached`;
- `manual_chatgpt_codex_transfer_required`.

AiGOL Next does not execute the Worker directly. It delegates into the certified runtime and renders the returned evidence.

Classification:

```text
Presentation Logic / Delegation
```

## 5. Conversational Workflow Audit

The REPL correctly owns local interaction state:

- message buffer;
- command recognition;
- preview;
- clearing;
- cancellation;
- exit handling;
- approval collection.

These are interface-local responsibilities.

However, the same module also determines:

- whether clarification is required;
- what clarification questions should be asked;
- whether a goal is goal-oriented;
- which governed request should be produced.

These decisions are not merely presentation. They affect development workflow shape before PGSP, UBTR, CSA, and Platform Core receive the request.

Classification:

```text
Correct Human Interface Responsibility for REPL state
Platform Service Candidate for clarification and workflow-intent shaping
```

## 6. Project Workspace Audit

The Project Workspace is currently created by:

```text
_persistent_workspace_state_artifact(...)
```

This function computes:

- `active_development_objective`;
- `pending_clarification_request`;
- `pending_implementation_summary`;
- `pending_approval`;
- `implementation_history`;
- `project_guidance`;
- `project_knowledge_index`;
- `recent_governed_decisions`.

The resulting artifact is replay-visible, but it is constructed inside the AiGOL Next adapter.

Under G14-01, workspace authority belongs to the certified platform runtime, not an individual human interface. A CLI-created workspace snapshot may be acceptable as cached presentation state only if it reflects a Platform Core workspace artifact. The current implementation creates and updates the workspace model in AiGOL Next.

Classification:

```text
Responsibility Drift
```

Required migration:

```text
Project Workspace Service inside Platform Core / OCS
```

## 7. Project Guidance Audit

Project guidance is computed by:

```text
_project_guidance_model(...)
_guidance_generation(...)
_guidance_milestone(...)
_guidance_pending_work(...)
_guidance_next_action(...)
```

The implementation determines:

- active generation;
- active milestone;
- pending implementation work;
- pending approvals;
- recommended next governed action.

This is more than rendering. It is project guidance logic and should be reusable by all human interfaces through Platform Core.

Classification:

```text
Responsibility Drift
```

Required migration:

```text
Project Guidance Service inside Platform Core / OCS
```

## 8. Goal-Oriented Development Audit

Goal-oriented development is implemented by:

```text
_goal_oriented_request_detected(...)
_goal_mapping_from_workspace(...)
```

The implementation maps natural language goals to governed requests:

| Input pattern | Current mapped result |
| --- | --- |
| `github actions` | `Add GitHub Actions support.` |
| `deployment` | `Add governed deployment workflow support.` |
| `mobile` | `Continue the governed mobile interface.` |
| `continue` | active workspace objective |

This is intent interpretation and goal normalization. The certified architecture assigns semantic interpretation to UBTR, structured intent to CSA, and orchestration to Platform Core / OCS.

Classification:

```text
Responsibility Drift
```

Required migration:

```text
Goal Mapping / Intent-to-Workflow Service behind PGSP -> UBTR -> CSA -> Platform Core
```

## 9. Project Knowledge Reuse Audit

G14-08 introduced:

```text
project_knowledge_index
contextual_task_mapping
duplicate_work_avoided
related_milestones
relevant_certified_artifacts
implementation_history_matches
```

Implementation evidence:

```text
_project_knowledge_index_model(...)
_project_knowledge_context_from_workspace(...)
_certified_artifacts_for_goal_target(...)
```

The implementation computes classifications:

```text
RELATES_TO_CERTIFIED_CAPABILITY
ALREADY_SATISFIED
MODIFIES_EXISTING_CAPABILITY
EXTENDS_EXISTING_MILESTONE
NEW_GOVERNED_WORK
```

These are not UI presentation decisions. They are project knowledge, duplicate detection, contextual task mapping, and reuse decisions. Under the certified invariant, these responsibilities belong to Platform Core.

Classification:

```text
Responsibility Drift
```

Required migration:

```text
Knowledge Reuse Service and Contextual Task Mapping Service inside Platform Core / OCS
```

## 10. Workspace Snapshot Ownership

Current workspace snapshots are replay-visible artifacts created by AiGOL Next.

The artifacts are useful and deterministic, but they currently behave as authoritative project state for:

- restored objectives;
- pending approvals;
- pending clarification;
- project guidance;
- project knowledge reuse.

For Unified Human Interface compliance, AiGOL Next may cache and render workspace state, but the authoritative workspace state must be produced by Platform Core.

Classification:

```text
Cached Platform State if generated by Platform Core
Responsibility Drift in current implementation because AiGOL Next generates it
```

## 11. Future Interface Reuse Assessment

| Capability | Reusable unchanged by Web/Android/Voice/REST/Desktop? | Reason |
| --- | --- | --- |
| Message composition | No, but acceptable | Each interface has modality-specific local UI state. |
| Approval collection | Yes conceptually | Each interface can collect approval and delegate. |
| Runtime binding | Mostly yes | Binding should be exposed through PGSP-compatible platform API. |
| Workspace restore | No | Logic is embedded in AiGOL Next. |
| Project guidance | No | Guidance computation is embedded in AiGOL Next. |
| Goal mapping | No | Mapping rules are embedded in AiGOL Next. |
| Project knowledge reuse | No | Knowledge reuse and classification rules are embedded in AiGOL Next. |
| Summary rendering | No, but acceptable | Rendering can be per-interface if summary data is platform-produced. |

Future interfaces would need to copy business logic from AiGOL Next unless the workspace, guidance, goal mapping, and knowledge reuse logic migrates into reusable Platform Core services.

## 12. Platform Service Candidate Inventory

| Candidate service | Current location | Recommended owner |
| --- | --- | --- |
| Project Workspace Service | `aigol/acli_next/conversational.py` | Platform Core / OCS |
| Project Guidance Service | `aigol/acli_next/conversational.py` | Platform Core / OCS |
| Workspace Resume Service | `aigol/acli_next/conversational.py` | Platform Core / OCS produces state; interfaces render |
| Goal Mapping Service | `aigol/acli_next/conversational.py` | UBTR / CSA / Platform Core composition |
| Contextual Task Mapping Service | `aigol/acli_next/conversational.py` | Platform Core / OCS |
| Knowledge Reuse Service | `aigol/acli_next/conversational.py` | Platform Core / OCS |
| Clarification Planning Service | `aigol/acli_next/conversational.py` | Platform Core / OCS with UBTR/CSA semantic input |

## 13. Updated Ownership Map

Recommended ownership after correction:

| Responsibility | Canonical owner | Interface role |
| --- | --- | --- |
| Message buffer and local commands | Human Interface | Owns local interaction |
| Approval and clarification collection | Human Interface | Collects human input |
| Workspace state production | Platform Core / OCS | Interface renders |
| Workspace state persistence authority | Platform Core / Replay | Interface displays references |
| Project guidance | Platform Core / OCS | Interface renders |
| Goal interpretation | UBTR | Interface forwards input |
| Structured goal intent | CSA | Interface displays references |
| Contextual task mapping | Platform Core / OCS | Interface renders recommendation |
| Project knowledge reuse | Platform Core / OCS | Interface renders recommendation |
| Governance authorization | Governance | Interface displays and collects human confirmation |
| Worker execution | Worker Platform | Interface never executes |
| Replay evidence | Replay | Interface displays evidence |

## 14. Architectural Compliance Assessment

Compliant areas:

- AiGOL Next remains non-executing.
- AiGOL Next does not authorize Governance.
- AiGOL Next does not invoke Workers directly.
- AiGOL Next does not own Provider execution.
- AiGOL Next does not replace Replay reconstruction.
- Runtime binding delegates to the certified runtime.
- Human confirmation remains explicit.

Non-compliant areas:

- Workspace authority is partially implemented inside AiGOL Next.
- Project guidance is computed inside AiGOL Next.
- Goal-oriented mapping is computed inside AiGOL Next.
- Project knowledge reuse is computed inside AiGOL Next.
- Contextual task mapping and duplicate avoidance are computed inside AiGOL Next.
- Future interfaces cannot reuse these capabilities unchanged without copying CLI logic.

Certification result:

```text
Generation 14 implementation preserved execution authority boundaries but violated the thin-adapter invariant for reusable project intelligence and workspace-derived development guidance.
```

## 15. Recommendations

Do not expand AiGOL Next further in these areas.

Recommended next milestone:

```text
G14_07B_PLATFORM_CORE_PROJECT_WORKSPACE_AND_KNOWLEDGE_SERVICE_MIGRATION_SPECIFICATION_V1
```

Scope:

- specify Platform Core ownership of Project Workspace;
- specify Platform Core ownership of Project Guidance;
- specify Platform Core ownership of Contextual Task Mapping;
- specify Platform Core ownership of Knowledge Reuse;
- convert AiGOL Next behavior into rendering and input collection over Platform Core-produced state;
- preserve existing Replay evidence;
- preserve current user-facing behavior where valid.

No architecture redesign is required. This is a responsibility correction to satisfy the already certified Unified Human Interface architecture.

## 16. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: UNIFIED_HUMAN_INTERFACE_RESPONSIBILITY_DRIFT_DETECTED
