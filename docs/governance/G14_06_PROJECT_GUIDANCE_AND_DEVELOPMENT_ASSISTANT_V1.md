# G14-06 Project Guidance And Development Assistant V1

Status: project guidance assistant implemented.

Final verdict: PROJECT_GUIDANCE_ASSISTANT_CERTIFIED

## 1. Executive Summary

G14-05 certified persistent AiGOL Next project workspaces.

G14-06 transforms that persistent workspace into a deterministic project guidance assistant. When a project session resumes, AiGOL Next now derives project guidance from the replay-visible workspace state and presents the current status, active generation, active milestone, pending implementation work, pending approvals, unresolved clarification state, and the next logical governed action.

The implementation does not reconstruct project authority from conversation history alone. The workspace state remains the deterministic source for guidance.

AiGOL Next remains advisory and conversational only. It does not execute recommended actions without explicit human approval.

## 2. Workspace Guidance Model

The workspace state now includes a `project_guidance` object with:

- guidance version;
- guidance source;
- active generation;
- active milestone;
- active development objective;
- pending implementation work;
- pending approvals;
- unresolved clarification status;
- implementation history count;
- runtime binding count;
- recommended next governed action;
- explicit non-execution flag.

The guidance source is always:

```text
deterministic_workspace_state
```

## 3. Resume Guidance UX

On session resume, AiGOL Next presents:

```text
Project guidance
guidance_source: deterministic_workspace_state
active_generation: Generation 14
active_milestone: ...
pending_implementation_work: ...
pending_approvals: ...
unresolved_clarification: ...
recommended_next_governed_action: ...
acli_next_executes_recommendation: False
```

This guidance is advisory only.

If a pending implementation summary exists, the recommended action is:

```text
Review the pending implementation summary, then type /approve or /cancel.
```

If a pending clarification exists, the recommended action is:

```text
Answer the pending clarification, then type /send.
```

## 4. Runtime Evidence

Validated scenario:

1. Start `aigol next`.
2. Submit:

```text
Implement CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1.
Goal: Extend the certified provider-neutral external worker architecture with Claude support while reusing existing governance, replay, validation, mutation, and worker lifecycle infrastructure.
/send
```

3. AiGOL Next presents a governed implementation summary.
4. Exit before approval.
5. Resume the same session.
6. AiGOL Next restores the workspace and presents deterministic project guidance:

```text
active_generation: Generation 14
active_milestone: CLAUDE_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1
pending_approvals: IMPLEMENTATION_SUMMARY_APPROVAL
recommended_next_governed_action: Review the pending implementation summary, then type /approve or /cancel.
acli_next_executes_recommendation: False
```

7. The operator types:

```text
/approve
```

8. The certified runtime executes and records:

```text
runtime_binding_status: AIGOL_NEXT_RUNTIME_BOUND
```

## 5. Ownership Verification

| Component | Certified responsibility | Result |
| --- | --- | --- |
| AiGOL Next | Conversational UX, deterministic workspace guidance display, explicit approval capture, delegation | Preserved |
| PGSP | Governed interface attachment and session invocation boundary | Preserved |
| UBTR | Semantic interpretation and intent normalization | Preserved |
| CSA | Structured intent handling | Preserved |
| Platform Core / OCS | Runtime orchestration and workflow progression | Preserved |
| Governance | Authorization and decisions | Preserved |
| Provider Platform | Provider identity and invocation boundary | Preserved |
| Worker Platform | Worker execution lifecycle | Preserved |
| Replay | Evidence and reconstruction | Preserved |
| Platform Digital Twin | Canonical architectural evidence source | Preserved |
| Architectural Health | Deterministic advisory review | Preserved |

AiGOL Next recommends actions but does not execute them without explicit approval.

## 6. Operational Readiness Assessment

AiGOL Next now behaves as a project-oriented development assistant over the persistent workspace.

An operator no longer needs to remember:

- current project objective;
- active milestone;
- pending approval;
- unresolved clarification;
- recent implementation continuity;
- next safe governed action.

Remaining improvements are UX refinements:

- richer milestone ordering can be added from future workspace evidence;
- broader project history summaries can be rendered;
- workspace selection can be made easier for multiple simultaneous sessions.

These are operational improvements, not architectural blockers.

## 7. Validation Evidence

Validation performed:

```text
python -m py_compile aigol/acli_next/conversational.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g14_06_project_guidance_assistant_v1.py tests/test_g14_05_persistent_development_workspace_v1.py tests/test_g14_04_conversational_development_workflow_v1.py tests/test_g14_03_aigol_next_runtime_binding_v1.py tests/test_g11_acli_next_conversational_session.py -q
git diff --check
```

Observed result:

```text
15 passed
```

Final verdict: PROJECT_GUIDANCE_ASSISTANT_CERTIFIED
