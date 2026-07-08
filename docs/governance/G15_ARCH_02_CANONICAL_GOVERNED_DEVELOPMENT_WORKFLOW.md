# G15-ARCH-02 - Canonical Governed Development Workflow

Status: ARCHITECTURE DEFINITION COMPLETE

Date: 2026-07-08

Milestone: G15-ARCH-02

Scope: Canonical Platform Core governed development workflow definition. This milestone does not modify production code, runtime behavior, routing behavior, replay semantics, governance semantics, approval behavior, Platform Core ownership, or Human Interface behavior.

## Canonical Governed Development Workflow

The canonical governed development workflow is the reusable Platform Core sequence that every Human Interface must use without owning or modifying semantics.

```text
Human Request
-> Human Intent Resolution
-> Clarification Resolution
-> Canonical Semantic Artifact
-> Knowledge Reuse
-> Governance
-> Runtime Entry
-> Runtime Continuation
-> Worker Execution
-> Replay Certification
-> Workflow Completion
```

Human Interfaces, including AiCLI, Web, REST, Voice, and future surfaces, may capture user input, render Platform Core outputs, collect explicit human approval, and delegate to Platform Core runtime entry. They do not own semantic interpretation, clarification planning, governance, replay, runtime continuation, worker dispatch, certification, or completion status.

## Stage Ownership Matrix

| Stage | Owner | Inputs | Outputs | Replay evidence | Certification evidence | Transition criteria |
| --- | --- | --- | --- | --- | --- | --- |
| Human Request | Human Interface capture boundary | Natural-language request, session id, workspace reference | Submitted request text and interface transcript | Interface session state and UHI project context request hash | G14/G15 UHI boundary reports | Request is non-empty and submitted to Platform Core. |
| Human Intent Resolution | Platform Core Project Services | Request text, prior workspace state, project guidance, capability catalog | Development Intent Resolution, admissibility flags, candidate goals | `UNIFIED_HUMAN_INTERFACE_PROJECT_CONTEXT_ARTIFACT_V1` | G14-19, G14-47, G15-HIR reports | Intent is deterministic enough for summary, clarification, or fail-closed response. |
| Clarification Resolution | Platform Core HIR / Project Services | Active clarification state, question bindings, submitted clarification reply | Answered question ids, resolved clarification state, updated development intent | Clarification continuity and workspace state replay | G15-HIR-02, G15-HIR-07, G15-HIR-08, G15-HIR-09 | Pending clarification is resolved or remains clarification-bound. |
| Canonical Semantic Artifact | Platform Core Semantics / UBTR path | Valid human-to-governance translation, resolved semantic fields, routing context | Hash-bound Canonical Semantic Artifact or compatibility-visible routing evidence | CSA replay artifact and routing artifacts | G15-SEMANTICS-01 and CSA specification evidence | CSA is valid and unambiguous when used as routing authority; otherwise compatibility routing remains fail-closed and visible. |
| Knowledge Reuse | Platform Core Project Services | Workspace state, goal mapping, certification registry references, prior implementation history | Knowledge reuse classification, contextual task mapping, recommended governed action | UHI project context and workspace state artifacts | G14-08A, G14-23, G15-ARCH-01 | Reuse evidence is recorded before governed implementation summary or runtime entry. |
| Governance | Platform Core Governance / Approval Boundary | Development intent, knowledge reuse, proposed governed action, human approval state | Governed implementation summary, approval prompt, authorization prerequisites | Approval summary, transcript, runtime entry evidence | G14 approval and governance reports, G15 runtime reports | Human explicitly approves a summary that is runtime-binding admissible. |
| Runtime Entry | Canonical Human Interface Runtime Entry Service | Approved canonical runtime prompt, session id, workspace, runtime root | Runtime prompts, runtime-entry decision, governed runner invocation | Runtime entry replay and project workspace state | G14-30, G14-41, G15-RUNTIME-05, G15-RUNTIME-06 | Prompt is runtime-binding admissible and approval is recorded. |
| Runtime Continuation | Platform Core Runtime Orchestration | Runtime prompt, routing artifacts, bridge proposal, native development context | Governed development bridge continuation, worker request, downstream runtime evidence | Turn summary, bridge replay, continuation replay | G15-ROUTING-01, G15-RUNTIME-06 | Governed workflow routing and continuation gates are satisfied or fail closed with prerequisite reason. |
| Worker Execution | Worker lifecycle and provider adapter boundaries under Platform Core orchestration | Authorized worker request, assignment, dispatch, invocation, task package | Worker execution candidate, external task package, result package, validation artifact | Worker request, assignment, dispatch, invocation, candidate, task package, result validation replay | Worker/runtime certification reports and G15-RUNTIME-06 | Worker lifecycle prerequisites are present and result validation completes. |
| Replay Certification | Platform Core Replay Certification Runtime | Completed result validation artifact, validation evidence, replay lineage | Replay certification artifact, replay observation layer, certification status | Replay observation layer and replay certification replay | G15-01, G15-REPLAY-01, G15-RUNTIME-05 | Result validation is complete, lineage-preserving, deterministic, governance-valid, and ready for certification. |
| Workflow Completion | Platform Core Runtime Completion | Runtime continuation result, replay certification result, workspace state | `WORKFLOW_COMPLETE`, `REPLAY_CERTIFIED`, governed return and completion state | Workspace state, runtime result, governed return, replay references | G15-RUNTIME-05, G15-RUNTIME-06, Certification Registry | Runtime reaches workflow completion with replay certification or fails closed with a deterministic downstream prerequisite. |

## Transition Matrix

| From | To | Required condition | Fail-closed condition |
| --- | --- | --- | --- |
| Human Request | Human Intent Resolution | Human Interface submits request to Platform Core. | Empty input or canceled compose state. |
| Human Intent Resolution | Clarification Resolution | Clarification is required or active clarification state exists. | Ambiguous request cannot be resolved and no valid clarification path exists. |
| Human Intent Resolution | Governance | Summary is admissible and no clarification is pending. | Summary is not admissible and no deterministic governed action exists. |
| Clarification Resolution | Human Intent Resolution | Clarification answer resolves active question bindings. | Reply is non-substantive or does not resolve active slots. |
| Human Intent Resolution | Canonical Semantic Artifact | Semantic fields are sufficient for CSA or CSA-aware routing participation. | CSA is ambiguous, invalid, or absent; compatibility routing remains visible and fail-closed. |
| Canonical Semantic Artifact | Knowledge Reuse | Semantic target is deterministic enough for project context and capability mapping. | Semantic target is unresolved. |
| Knowledge Reuse | Governance | Reuse evidence and governed action are recorded. | Required context is missing or request remains underspecified. |
| Governance | Runtime Entry | Human explicitly approves Platform Core summary. | Approval missing, canceled, or invalid. |
| Runtime Entry | Runtime Continuation | Runtime binding is admissible and canonical prompt is forwarded. | Prompt is non-admissible or runtime entry is not required. |
| Runtime Continuation | Worker Execution | Governed workflow selection and authorization prerequisites are satisfied. | Routing, bridge, authorization, dispatch, provider, or worker prerequisite is missing. |
| Worker Execution | Replay Certification | Result validation completes and is ready for replay certification. | Worker execution result is missing, invalid, or lineage-broken. |
| Replay Certification | Workflow Completion | Replay certification completes. | Certification fails closed with deterministic failure reason. |

## Replay Evidence Flow

Replay evidence must remain append-only, reconstructable, and Platform Core-owned.

Canonical replay flow:

```text
UHI project context
-> clarification continuity
-> workspace state
-> runtime entry
-> conversational routing and CSA/UBTR evidence
-> governed development bridge
-> runtime continuation
-> worker lifecycle replay
-> result validation
-> replay observation layer
-> replay certification
-> governed return and workflow completion
```

Replay evidence responsibilities:

- Human Interfaces provide request and approval events but do not author replay semantics.
- Platform Core Project Services record project context, guidance, knowledge reuse, development intent, clarification state, and conversation artifacts.
- Runtime orchestration records routing, bridge, continuation, worker lifecycle, and result validation evidence.
- Replay Observation normalizes existing replay evidence without mutating it.
- Replay Certification certifies only completed, validated, lineage-preserving results.
- Certification Registry indexes governance reports and does not replace replay or report evidence.

## Governance Review

The canonical workflow preserves the Generation 14 architecture and the Generation 15 baseline.

Governance guarantees:

- No Human Interface owns semantic interpretation.
- No Human Interface owns approval semantics beyond collecting explicit human approval.
- No Human Interface owns runtime continuation, worker dispatch, provider selection, replay, or certification.
- Platform Core owns HIR, clarification planning, clarification resolution, project context, governance summaries, runtime entry, runtime continuation, replay certification, and certification metadata.
- CSA is semantic authority only; it does not grant execution authority by itself.
- Runtime entry requires approved, runtime-binding admissible prompts.
- Worker execution is reached only through governed authorization and runtime continuation.
- Replay certification is downstream of result validation and remains fail-closed.
- Governance reports remain immutable certification evidence.

## Boundary Confirmation

This milestone documents the workflow only.

No responsibilities move.

No production code changes are introduced.

No runtime behavior changes are introduced.

No AiCLI redesign is introduced.

No Platform Core redesign is introduced.

AiCLI, Web, REST, Voice, and future Human Interfaces must all reuse this same Platform Core workflow by delegating to Platform Core boundaries rather than recreating semantics locally.

## Validation Summary

Validation performed:

- `python -m py_compile aigol/runtime/platform_core_project_services.py aigol/runtime/human_interface_runtime_entry_service.py aigol/runtime/canonical_semantic_artifact_runtime.py aigol/runtime/conversational_cli_runtime.py aigol/runtime/replay_certification_runtime.py aigol/runtime/replay_observation_layer.py aigol/cli/aigol_cli.py aigol/cli/aicli.py`
- `python -m pytest -q` passed: `5835 passed, 4 skipped in 140.14s`.
- `git diff --check` passed.

Tracked runtime evidence regenerated by full validation was restored so the milestone diff remains documentation-only.

## Governance Report

G15-ARCH-02 defines the canonical Platform Core Governed Development Workflow for Generation 16 reuse.

The workflow composes established Generation 15 capabilities into one stable reference:

- Human Intent Resolution and clarification state remain in Platform Core Project Services.
- Canonical Semantic Artifact participation remains semantic and gated.
- Knowledge reuse remains Platform Core project context evidence.
- Governance and approval remain explicit and fail-closed.
- Runtime Entry is the canonical Human Interface-to-runtime boundary.
- Runtime Continuation carries approved governed development into worker lifecycle and result validation.
- Replay Certification closes the workflow only after validated replay lineage is present.
- Workflow Completion records deterministic completion or deterministic fail-closed prerequisite.

Canonical workflow verdict:

`G15_ARCH_02_CANONICAL_GOVERNED_DEVELOPMENT_WORKFLOW_DEFINED`

This workflow is Human Interface-neutral and reusable unchanged by AiCLI, Web, REST, Voice, and future Human Interfaces.
