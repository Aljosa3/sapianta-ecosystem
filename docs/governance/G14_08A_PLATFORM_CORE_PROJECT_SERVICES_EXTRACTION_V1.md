# G14-08A Platform Core Project Services Extraction V1

Status: Platform Core project services extracted.

Final verdict: PLATFORM_CORE_PROJECT_SERVICES_CERTIFIED

## 1. Executive Summary

G14-07A detected responsibility drift in the Generation 14 human interface implementation.

The drift was localized to project workspace, project guidance, goal mapping, contextual task mapping, and project knowledge reuse logic implemented inside AiGOL Next.

G14-08A restores the certified Unified Human Interface architecture by extracting those responsibilities into reusable Platform Core project services while preserving the existing AiGOL Next user experience.

AiGOL Next now:

- manages local REPL interaction;
- renders Platform Core service outputs;
- collects human clarification and approval;
- delegates runtime execution.

Platform Core project services now own:

- Project Workspace construction;
- Project Guidance;
- Goal Mapping;
- Contextual Task Mapping;
- Project Knowledge Reuse.

## 2. Platform Core Project Services Implementation

New implementation:

```text
aigol/runtime/platform_core_project_services.py
```

The module provides:

- `build_persistent_workspace_state_artifact(...)`;
- `project_guidance_from_workspace_state(...)`;
- `project_guidance_model(...)`;
- `goal_mapping_from_workspace(...)`;
- `project_knowledge_index_model(...)`;
- `project_knowledge_context_from_workspace(...)`;
- clarification and guided-development request classification services.

The service emits authority evidence:

```text
project_workspace_authority: PLATFORM_CORE
project_guidance_authority: PLATFORM_CORE
project_knowledge_reuse_authority: PLATFORM_CORE
contextual_task_mapping_authority: PLATFORM_CORE
goal_mapping_authority: PLATFORM_CORE
guidance_authority: PLATFORM_CORE
knowledge_reuse_authority: PLATFORM_CORE
```

## 3. AiGOL Next Refactoring

AiGOL Next no longer defines the extracted business logic.

Removed from `aigol/acli_next/conversational.py`:

- `_persistent_workspace_state_artifact(...)`;
- `_project_guidance_model(...)`;
- `_goal_mapping_from_workspace(...)`;
- `_project_knowledge_index_model(...)`;
- `_project_knowledge_context_from_workspace(...)`;
- `_guided_development_clarification_required(...)`.

AiGOL Next now imports the Platform Core project services and only:

- calls services;
- renders returned summaries;
- collects `/send`, `/preview`, `/clear`, `/cancel`, and `/approve`;
- writes replay-visible artifacts returned by the service.

## 4. Responsibility Migration Matrix

| Capability | Previous location | New owner | AiGOL Next role |
| --- | --- | --- | --- |
| Project Workspace | `aigol/acli_next/conversational.py` | Platform Core project services | Render and persist returned workspace artifact |
| Project Guidance | `aigol/acli_next/conversational.py` | Platform Core project services | Render returned guidance |
| Goal Mapping | `aigol/acli_next/conversational.py` | Platform Core project services | Render returned mapping |
| Contextual Task Mapping | `aigol/acli_next/conversational.py` | Platform Core project services | Render returned classification |
| Project Knowledge Reuse | `aigol/acli_next/conversational.py` | Platform Core project services | Render returned reuse evidence |
| Message Composer | AiGOL Next | AiGOL Next | Local UI state |
| Approval Collection | AiGOL Next | AiGOL Next | Collect human confirmation |
| Runtime Execution | Certified runtime | Platform Core / Governance / Providers / Workers / Replay | Delegate only |

## 5. Runtime Evidence

Validated user-visible flow:

```text
I want AiGOL Next to support GitHub Actions.
/send
exit
```

Observed terminal evidence remains unchanged:

```text
contextual_task_mapping:
classification: RELATES_TO_CERTIFIED_CAPABILITY
reuse_recommended: True
```

Workspace evidence now records Platform Core authority:

```text
platform_core_project_services_version: G14_08A_PLATFORM_CORE_PROJECT_SERVICES_EXTRACTION_V1
project_workspace_authority: PLATFORM_CORE
project_guidance_authority: PLATFORM_CORE
project_knowledge_reuse_authority: PLATFORM_CORE
contextual_task_mapping_authority: PLATFORM_CORE
```

Pending summary evidence:

```text
goal_mapping_authority: PLATFORM_CORE
contextual_task_mapping_authority: PLATFORM_CORE
acli_next_executes: False
```

## 6. Replay Evidence

Replay-visible workspace artifacts continue to be written under:

```text
workspace_state/*_acli_next_workspace_state_recorded.json
```

The artifacts now include Platform Core project service version and authority fields.

The user-visible artifact shape remains compatible with G14-05 through G14-08 behavior.

## 7. Future Interface Reuse

The extracted services can be reused unchanged by:

- Web;
- Android;
- Voice;
- REST;
- Desktop;
- future human interfaces.

Future interfaces should call the same Platform Core project service functions through their PGSP-bound runtime integration and render the returned state in modality-specific form.

They do not need to copy AiGOL Next goal mapping, project guidance, workspace, or knowledge reuse logic.

## 8. Updated Ownership Map

| Responsibility | Certified owner after G14-08A |
| --- | --- |
| Local input and presentation | Human Interface |
| Message composition | Human Interface |
| Human approval and clarification collection | Human Interface |
| Project Workspace | Platform Core |
| Project Guidance | Platform Core |
| Goal Mapping | Platform Core |
| Contextual Task Mapping | Platform Core |
| Project Knowledge Reuse | Platform Core |
| Semantic interpretation | UBTR |
| Structured intent | CSA |
| Workflow orchestration | Platform Core / OCS |
| Authorization | Governance |
| Provider invocation | Provider Platform through Platform Core |
| Worker execution | Worker Platform |
| Evidence and reconstruction | Replay |

## 9. Architectural Compliance Assessment

G14-08A removes the responsibility drift identified by G14-07A.

Compliance findings:

- AiGOL Next remains a thin Human Interface adapter.
- Platform Core now owns the project services.
- AiGOL Next no longer computes project guidance.
- AiGOL Next no longer computes contextual task mapping.
- AiGOL Next no longer owns knowledge reuse.
- User-visible behavior remains unchanged.
- Existing runtime execution remains certified and unchanged.
- Future human interfaces can reuse the extracted services without copying CLI business logic.

No Platform Core architecture redesign was introduced.

## 10. Validation Evidence

Validation performed:

```text
python -m py_compile aigol/acli_next/conversational.py aigol/runtime/platform_core_project_services.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g14_08a_platform_core_project_services_extraction_v1.py tests/test_g14_08_project_knowledge_reuse_v1.py tests/test_g14_07_goal_oriented_development_experience_v1.py tests/test_g14_06_project_guidance_assistant_v1.py tests/test_g14_05_persistent_development_workspace_v1.py tests/test_g14_04_conversational_development_workflow_v1.py tests/test_g14_03_aigol_next_runtime_binding_v1.py tests/test_g11_acli_next_conversational_session.py -q
git diff --check
```

Observed result:

```text
22 passed
```

Final verdict: PLATFORM_CORE_PROJECT_SERVICES_CERTIFIED
