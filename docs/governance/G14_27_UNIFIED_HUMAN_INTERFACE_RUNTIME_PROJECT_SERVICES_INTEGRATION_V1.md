# G14-27 Unified Human Interface Runtime Project Services Integration V1

Status: Unified Human Interface Runtime Project Services integrated.

Final verdict: UNIFIED_HUMAN_INTERFACE_RUNTIME_PROJECT_SERVICES_CERTIFIED

## 1. Executive Summary

G14-27 implements the canonical integration of Platform Core Project Services into the Unified Human Interface Runtime.

The implementation closes the G14-26 continuity gap by ensuring that human interfaces receive deterministic Project Workspace, Project Guidance, Knowledge Reuse, and Development Intent Resolution through Platform Core-owned services before entering the governed runtime.

The integration is not interface-specific. `aicli` and `aigol next` now both consume the same Platform Core project-context service and record deterministic replay evidence for:

- Project Workspace;
- Project Guidance;
- Knowledge Reuse;
- Development Intent Resolution.

Human interfaces remain thin adapters. No interface owns workspace logic, guidance logic, knowledge reuse, provider selection, worker routing, Governance, or Replay.

## 2. Implementation Summary

Implemented in:

```text
aigol/runtime/platform_core_project_services.py
```

New canonical Platform Core service functions:

```text
prepare_unified_human_interface_project_context
record_unified_human_interface_workspace_state
latest_platform_core_workspace_state
next_workspace_state_index
next_uhi_project_context_index
```

The new project-context artifact is:

```text
UNIFIED_HUMAN_INTERFACE_PROJECT_CONTEXT_ARTIFACT_V1
```

It includes:

- restored workspace state reference;
- project guidance;
- knowledge reuse analysis;
- development intent resolution;
- Platform Core ownership markers;
- replay reference.

The workspace state artifact remains:

```text
ACLI_NEXT_PERSISTENT_WORKSPACE_STATE_ARTIFACT_V1
```

Despite its historical name, it is now recorded through Platform Core for Unified Human Interface runtime continuity.

## 3. Updated Runtime Call Graph

Canonical runtime:

```text
Human
↓
Human Interface
↓
Unified Human Interface Runtime
↓
Platform Core Project Services
↓
Project Workspace restoration
↓
Project Guidance generation
↓
Knowledge Reuse analysis
↓
Development Intent Resolution
↓
PGSP
↓
UBTR
↓
CSA
↓
Platform Core
↓
Governance
↓
Provider Platform
↓
Worker Platform
↓
Replay
```

Interfaces do not decide whether Project Services execute. The runtime invokes the Platform Core service before development intent resolution and records workspace state after runtime completion.

## 4. Interface Integration

### 4.1 `aicli`

Updated:

```text
aigol/cli/aicli.py
```

`aicli` now calls:

```text
prepare_unified_human_interface_project_context
record_unified_human_interface_workspace_state
```

`aicli` renders the Platform Core project-context artifact and stores only returned references.

Confirmed non-responsibilities:

- `aicli` does not implement workspace logic.
- `aicli` does not implement project guidance.
- `aicli` does not implement knowledge reuse.
- `aicli` does not perform Governance.
- `aicli` does not execute Workers.
- `aicli` does not own Replay.

### 4.2 `aigol next`

Updated:

```text
aigol/cli/aigol_cli.py
```

The runtime binding path now calls the same Platform Core project-context service before runtime prompt selection and records workspace state after runtime binding completion.

This eliminates the previous direct intent-resolution call with:

```text
workspace_state=None
```

## 5. Regression Tests

Updated:

```text
tests/test_g14_22_reference_unified_human_interface_v1.py
```

Added:

```text
tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py
```

Coverage verifies:

- `aicli` delegates to Platform Core Project Services;
- `aicli` restores Platform Core workspace state across sessions;
- `aicli` remains a thin adapter;
- `aigol next` runtime binding uses the same Platform Core project-context artifact;
- both paths record deterministic workspace state evidence;
- no interface contains provider, worker, Governance, or project-service business logic.

## 6. Runtime Evidence

Real `./aicli` validation:

```text
./aicli --session-id G14-27-AICLI-FINAL --runtime-root /tmp/aigol_g14_27_aicli_final --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
```

Prompt:

```text
I want AiGOL Next to support GitHub Actions.
```

Observed result:

- Platform Core project context presented;
- Project Workspace authority: `PLATFORM_CORE`;
- Project Guidance authority: `PLATFORM_CORE`;
- Project Knowledge Reuse authority: `PLATFORM_CORE`;
- governed implementation summary presented;
- approval accepted;
- Governance authorization reached;
- Provider Platform reached;
- Worker Platform reached;
- Replay certification reached.

Replay evidence:

```text
/tmp/aigol_g14_27_aicli_final/G14-27-AICLI-FINAL/uhi_project_services/001_uhi_project_context_recorded.json
/tmp/aigol_g14_27_aicli_final/G14-27-AICLI-FINAL/workspace_state/001_platform_core_workspace_state_recorded.json
```

Real `aigol next` validation:

```text
python -m aigol.cli.aigol_cli next --session-id G14-27-AIGOL-NEXT-FINAL --runtime-root /tmp/aigol_g14_27_aigol_next_final --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
```

Prompt:

```text
I want AiGOL Next to support GitHub Actions.
```

Observed result:

- runtime binding status: `AIGOL_NEXT_RUNTIME_BOUND`;
- Governance authorization reached;
- Provider Platform reached;
- Worker Platform reached;
- Replay certification reached;
- manual ChatGPT to Codex transfer not required.

Replay evidence:

```text
/tmp/aigol_g14_27_aigol_next_final/G14-27-AIGOL-NEXT-FINAL/uhi_project_services/001_uhi_project_context_recorded.json
/tmp/aigol_g14_27_aigol_next_final/G14-27-AIGOL-NEXT-FINAL/workspace_state/001_platform_core_workspace_state_recorded.json
```

The `aigol next` validation also produced project-context artifacts for `/approve` and `/exit` because the non-interactive piped execution supplied those lines as conversational prompts. The first artifact is the development request artifact and contains the governed project services evidence for the accepted request.

## 7. Replay Evidence Requirements

Replay now records deterministic evidence for:

| Evidence | `aicli` | `aigol next` |
| --- | --- | --- |
| Unified Human Interface project context | Present | Present |
| Project Workspace authority | Present | Present |
| Project Guidance authority | Present | Present |
| Project Knowledge Reuse authority | Present | Present |
| Development Intent Resolution authority | Present | Present |
| Workspace state artifact | Present | Present |
| Provider/Worker/Replay continuation | Present | Present |

## 8. Ownership Verification

Ownership remains unchanged:

- Platform Core owns Project Workspace, Project Guidance, Knowledge Reuse, and Development Intent Resolution.
- Human interfaces request and render Platform Core service artifacts.
- Human interfaces collect input and approval only.
- Governance remains the authorization authority.
- Provider Platform remains the provider boundary.
- Worker Platform remains the execution boundary.
- Replay remains the evidence authority.

No new authority layer was introduced.

No interface-specific workspace implementation was introduced.

## 9. Validation Evidence

Compile validation:

```text
python -m py_compile aigol/runtime/platform_core_project_services.py aigol/cli/aicli.py aigol/cli/aigol_cli.py tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py tests/test_g14_22_reference_unified_human_interface_v1.py
```

Regression validation:

```text
python -m pytest tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py tests/test_g14_08a_platform_core_project_services_extraction_v1.py tests/test_g14_06_project_guidance_assistant_v1.py tests/test_g14_08_project_knowledge_reuse_v1.py tests/test_g14_19_development_intent_resolution_unification_v1.py -q
```

Result:

```text
15 passed
```

Real runtime validation:

```text
./aicli --session-id G14-27-AICLI-FINAL --runtime-root /tmp/aigol_g14_27_aicli_final --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
python -m aigol.cli.aigol_cli next --session-id G14-27-AIGOL-NEXT-FINAL --runtime-root /tmp/aigol_g14_27_aigol_next_final --workspace /home/pisarna/work/sapianta --created-at 2026-07-04T00:00:00Z
```

Whitespace validation:

```text
git diff --check
```

Validation result: clean.

## 10. Certification Summary

G14-27 certifies that Platform Core Project Services are integrated into the Unified Human Interface Runtime.

Every current human interface validated in this milestone receives deterministic project context through Platform Core before entering Development Intent Resolution, and replay records Project Workspace, Project Guidance, and Knowledge Reuse evidence.

The certified architecture remains preserved.

Final verdict: UNIFIED_HUMAN_INTERFACE_RUNTIME_PROJECT_SERVICES_CERTIFIED
