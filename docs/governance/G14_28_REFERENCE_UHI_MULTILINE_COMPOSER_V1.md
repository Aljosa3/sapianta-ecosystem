# G14-28 Reference UHI Multiline Composer V1

Status: reference UHI multiline composer certified.

Final verdict: REFERENCE_UHI_MULTILINE_COMPOSER_CERTIFIED

## 1. Executive Summary

G14-28 implements a multi-line request composer for the reference Unified Human Interface, `aicli`.

The implementation is a Human Interface usability improvement only. It does not modify Platform Core, Governance, Provider Platform, Worker Platform, Replay, or Development Intent Resolution.

`aicli` now collects user input into a temporary compose buffer and submits the complete request exactly once when the user enters:

```text
/send
```

or:

```text
.
```

EOF also submits any non-empty compose buffer once, then exits without executing unless human approval has already been supplied.

The complete composed request is sent unchanged into the already certified Platform Core project-services and runtime path.

## 2. Implementation Summary

Updated:

```text
aigol/cli/aicli.py
```

The composer owns only:

- input buffering;
- command recognition for `/send`, `.`, `/cancel`, `/approve`, `/exit`, and `/help`;
- terminal prompts;
- rendering returned Platform Core artifacts.

The composer does not own:

- intent classification;
- workspace analysis;
- project guidance;
- knowledge reuse;
- provider invocation;
- Governance;
- Worker execution;
- Replay.

The Platform Core path remains:

```text
Platform Core Project Services
↓
Development Intent Resolution
↓
PGSP
↓
UBTR
↓
CSA
↓
Governance
↓
Provider Platform
↓
Worker Platform
↓
Replay
```

## 3. User Experience

On startup, `aicli` now renders:

```text
Compose a request. Finish with /send or a single '.' line. Use /cancel to clear.
```

Prompt behaviour:

- `aicli>` appears before composition begins.
- `aicli compose>` appears while the compose buffer contains text.

Supported commands:

| Command | Behaviour |
| --- | --- |
| `/send` | Submits the current compose buffer once. |
| `.` | Submits the current compose buffer once. |
| EOF | Submits a non-empty compose buffer once and exits. |
| `/cancel` | Clears the compose buffer or discards pending summary state. |
| `/approve` | Approves a pending governed summary. If a single-line buffer exists, it is submitted first for backward-compatible single-line operation. |
| `/exit` | Exits only when no compose buffer is pending. |

## 4. Request Preservation

The composer joins buffered lines with newline characters and submits the resulting request without semantic preprocessing.

Validated multi-line prompt:

```text
Implement governance validation utility.

Requirements:
- preserve replay evidence
- add deterministic reporting
```

Replay evidence confirms Platform Core received the exact raw prompt:

```text
"Implement governance validation utility.\n\nRequirements:\n- preserve replay evidence\n- add deterministic reporting"
```

## 5. Regression Coverage

Updated:

```text
tests/test_g14_22_reference_unified_human_interface_v1.py
```

Regression coverage verifies:

- single-line prompts still work;
- multi-line prompts become one submitted request;
- the complete prompt reaches Platform Core unchanged;
- `/send` submits exactly once;
- `.` submits exactly once;
- `/cancel` clears the compose buffer without runtime execution;
- approval workflow remains unchanged;
- runtime binding remains unchanged;
- replay artifacts continue to be produced.

## 6. Runtime Evidence

### 6.1 Short Prompt

Command:

```text
./aicli --session-id G14-28-AICLI-SHORT --runtime-root /tmp/aigol_g14_28_aicli_short --workspace /home/pisarna/work/sapianta --created-at 2026-07-05T00:00:00Z
```

Input:

```text
Implement governance validation utility.
/send
/approve
/exit
```

Observed result:

- one request submitted;
- Platform Core project context produced;
- governed implementation summary produced;
- approval accepted;
- Governance authorization reached;
- Provider Platform reached;
- Worker Platform reached;
- Replay certification reached.

### 6.2 Multi-Line Prompt

Command:

```text
./aicli --session-id G14-28-AICLI-MULTILINE --runtime-root /tmp/aigol_g14_28_aicli_multiline --workspace /home/pisarna/work/sapianta --created-at 2026-07-05T00:00:00Z
```

Input:

```text
Implement governance validation utility.

Requirements:
- preserve replay evidence
- add deterministic reporting
.
/approve
/exit
```

Observed result:

- one composed request submitted;
- original newlines preserved;
- Platform Core project context produced;
- governed implementation summary produced;
- approval accepted;
- Governance authorization reached;
- Provider Platform reached;
- Worker Platform reached;
- Replay certification reached.

Replay evidence:

```text
/tmp/aigol_g14_28_aicli_multiline/G14-28-AICLI-MULTILINE/uhi_project_services/001_uhi_project_context_recorded.json
/tmp/aigol_g14_28_aicli_multiline/G14-28-AICLI-MULTILINE/workspace_state/001_platform_core_workspace_state_recorded.json
```

### 6.3 Clarification Flow

Command:

```text
./aicli --session-id G14-28-AICLI-CLARIFY --runtime-root /tmp/aigol_g14_28_aicli_clarify --workspace /home/pisarna/work/sapianta --created-at 2026-07-05T00:00:00Z
```

Input:

```text
Improve project.
/send
/exit
```

Observed result:

- one request submitted;
- Platform Core project context produced;
- clarification required;
- no runtime execution occurred;
- workspace state recorded pending clarification.

Replay evidence confirms:

```text
raw_prompt: Improve project.
clarification_required: true
```

### 6.4 EOF Completion

Command:

```text
./aicli --session-id G14-28-AICLI-EOF --runtime-root /tmp/aigol_g14_28_aicli_eof --workspace /home/pisarna/work/sapianta --created-at 2026-07-05T00:00:00Z
```

Input:

```text
Implement replay summary utility.
```

Then EOF.

Observed result:

- non-empty compose buffer submitted once;
- governed implementation summary produced;
- no execution occurred without approval;
- workspace state recorded pending approval.

## 7. Replay Evidence

Replay artifacts were created for each validation path:

```text
/tmp/aigol_g14_28_aicli_short/G14-28-AICLI-SHORT/uhi_project_services/001_uhi_project_context_recorded.json
/tmp/aigol_g14_28_aicli_short/G14-28-AICLI-SHORT/workspace_state/001_platform_core_workspace_state_recorded.json
/tmp/aigol_g14_28_aicli_multiline/G14-28-AICLI-MULTILINE/uhi_project_services/001_uhi_project_context_recorded.json
/tmp/aigol_g14_28_aicli_multiline/G14-28-AICLI-MULTILINE/workspace_state/001_platform_core_workspace_state_recorded.json
/tmp/aigol_g14_28_aicli_clarify/G14-28-AICLI-CLARIFY/uhi_project_services/001_uhi_project_context_recorded.json
/tmp/aigol_g14_28_aicli_clarify/G14-28-AICLI-CLARIFY/workspace_state/001_platform_core_workspace_state_recorded.json
/tmp/aigol_g14_28_aicli_eof/G14-28-AICLI-EOF/uhi_project_services/001_uhi_project_context_recorded.json
/tmp/aigol_g14_28_aicli_eof/G14-28-AICLI-EOF/workspace_state/001_platform_core_workspace_state_recorded.json
```

## 8. Ownership Verification

Ownership remains preserved:

- `aicli` owns input buffering only.
- Platform Core owns Project Workspace, Project Guidance, Knowledge Reuse, and Development Intent Resolution.
- Governance owns authorization.
- Provider Platform owns provider invocation.
- Worker Platform owns execution.
- Replay owns evidence.

No Platform Core logic was duplicated inside `aicli`.

No Governance, Provider, Worker, or Replay responsibility migrated into the interface.

## 9. Validation Evidence

Compile validation:

```text
python -m py_compile aigol/cli/aicli.py tests/test_g14_22_reference_unified_human_interface_v1.py
```

Regression validation:

```text
python -m pytest tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py -q
```

Initial result:

```text
10 passed
```

Final validation:

```text
python -m py_compile aigol/cli/aicli.py tests/test_g14_22_reference_unified_human_interface_v1.py
python -m pytest tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py -q
git diff --check
```

Result:

```text
10 passed
git diff --check clean
```

## 10. Certification Summary

G14-28 certifies that the reference UHI supports natural multi-line development request composition.

The complete request is submitted exactly once into the certified Platform Core runtime. Platform Core receives the original composed request with newlines preserved. Existing governance, runtime binding, provider, worker, and replay behaviour remain unchanged.

Final verdict: REFERENCE_UHI_MULTILINE_COMPOSER_CERTIFIED
