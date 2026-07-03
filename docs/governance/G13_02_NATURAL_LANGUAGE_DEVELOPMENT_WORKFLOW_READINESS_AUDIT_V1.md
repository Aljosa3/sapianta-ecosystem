# G13-02 Natural Language Development Workflow Readiness Audit V1

Status: natural language development workflow readiness audited.

Final verdict: NATURAL_LANGUAGE_DEVELOPMENT_WORKFLOW_PARTIALLY_READY

## 1. Executive Summary

Generation 12 certified the operational conversational entry pipeline, and Generation 13 confirmed that UBTR is operational as the canonical semantic runtime.

This audit determines whether an ordinary natural language request can already become a complete governed development workflow without requiring the human to know internal milestones, governance artifacts, implementation plans, Capability Discovery terminology, architecture names, or internal commands.

The answer is:

```text
partially ready
```

The platform already implements the required architectural components:

```text
Terminal
    -> aigol next
    -> AiGOL Next
    -> PGSP
    -> UBTR
    -> CSA
    -> Platform Core / OCS
    -> Governance
    -> Worker Platform
    -> Replay
```

Natural-language intake, UBTR translation, CSA artifact generation, OCS handoff, clarification routing, execution-plan preview, dashboard rendering, Governance separation, Worker separation, and Replay evidence all exist in the implementation.

However, the current default `aigol next` path does not yet automatically use the full UBTR -> CSA -> OCS development workflow path for a plain request such as:

```text
Add GitHub Actions support.
```

Instead, `aigol next --prompt "Add GitHub Actions support."` currently presents a governed conversational status, execution-plan preview, dashboard, and Replay-visible run without actually generating a full governed implementation workflow, worker delegation, validation plan, or development artifact proposal.

The older conversational routing runtime can process the same ordinary prompt through UBTR / CSA and does not fail closed, but it routes the prompt to clarification rather than a complete governed development workflow.

Therefore, AiGOL has the certified architectural substrate and much of the implementation needed for ordinary natural-language development. The remaining work is integration and UX wiring, not architecture redesign.

## 2. Architecture Audit

The certified architecture already defines the required natural-language path.

| Component | Certified role for natural-language development |
| --- | --- |
| AiGOL Next | CLI adapter, conversational UX, message composition, presentation, guidance |
| PGSP | Universal governed interface attachment and session invocation boundary |
| UBTR | Semantic interpretation, intent normalization, governed conversational understanding |
| CSA | Structured semantic artifact output from semantic interpretation |
| Platform Core / OCS | Workflow orchestration, candidate/proposal formation, execution planning, capability coordination |
| Governance | Approval and authorization authority |
| Replay | Evidence, reconstruction, and execution history authority |
| Worker Platform | Bounded execution through certified workers |
| Provider Platform | Non-authoritative provider cognition or external provider access under governance |
| Platform Digital Twin | Canonical evidence projection |
| Architectural Health | Deterministic advisory-only architecture review |

The architecture supports ordinary natural language as an interface input. No new subsystem is required to make natural-language development possible.

## 3. Implementation Audit

Implementation evidence confirms that the major runtime pieces exist.

### 3.1 AiGOL Next

Implemented evidence:

- `aigol/acli_next/conversational.py`
- `aigol/acli_next/interactive.py`
- `aigol/acli_next/execution_plan.py`
- `aigol/acli_next/daily_dashboard.py`
- `aigol/cli/aigol_cli.py`

Current behavior:

- supports `aigol next`;
- supports persistent REPL and message composer;
- creates one conversational turn per submitted message;
- generates execution-plan preview and dashboard presentation;
- records Replay-visible presentation artifacts;
- preserves show-guide-delegate boundaries.

Limitation:

- default `aigol next` presentation does not call the full UBTR / CSA conversational routing runtime as the default governed development path.

### 3.2 PGSP

Implemented evidence:

- certified PGSP session architecture;
- G12 canonical entry pipeline and PGSP responsibility clarification;
- ACLI Next session invocation artifacts.

Current behavior:

- provides the certified interface attachment and session boundary.

Limitation:

- practical evidence is strongest for CLI attachment; non-CLI interface adapters remain less mature.

### 3.3 UBTR

Implemented evidence:

- `aigol/runtime/human_to_governance_translation_runtime.py`
- `aigol/runtime/governance_to_human_translation_runtime.py`
- `aigol/runtime/universal_translation_artifact_schema.py`
- `aigol/runtime/universal_translation_runtime_integration.py`
- `aigol/runtime/ubtr_semantic_cognition_orchestration_runtime.py`
- `aigol/runtime/ubtr_ocs_cognition_handoff_runtime.py`
- `aigol/runtime/ubtr_cognition_result_integration_runtime.py`
- G13-01 verdict: `UBTR_RUNTIME_OPERATIONAL`

Current behavior:

- translates natural-language human requests into governance-intent candidates;
- detects ambiguity and clarification requirements;
- generates normalized intent;
- preserves provider and worker non-authority;
- records Replay-visible translation evidence.

Limitation:

- default `aigol next` does not yet consistently make UBTR the first visible semantic stage for ordinary daily development requests.

### 3.4 CSA

Implemented evidence:

- `aigol/runtime/canonical_semantic_artifact_runtime.py`
- CSA usage in `aigol/runtime/conversational_cli_runtime.py`

Current behavior:

- creates canonical semantic artifacts from UBTR translation;
- records semantic identity, workflow identity, confidence, ambiguity, approval state, execution intent, provider projection, and worker projection.

Limitation:

- CSA artifacts are available in the conversational routing runtime but are not surfaced as first-class default output in `aigol next` presentation.

### 3.5 Platform Core / OCS

Implemented evidence:

- `aigol/runtime/platform_core_execution_planning_service.py`
- `aigol/runtime/platform_core_daily_operational_exposure.py`
- `aigol/runtime/governed_development_workflow_runtime.py`
- `aigol/runtime/conversational_cli_runtime.py`
- OCS semantic resolution, context assembly, execution readiness, cognition, and handoff modules.

Current behavior:

- execution-plan preview exists;
- daily operational dashboard exists;
- conversational routing runtime can select workflows;
- OCS cognition handoff exists for semantic cognition paths.

Limitation:

- the default plain `aigol next` flow remains primarily a presentation and preview flow, not a complete natural-language-to-implementation workflow generator.

### 3.6 Governance

Implemented evidence:

- governance preview and authorization modules;
- approval runtime modules;
- platform-core governance modules for mutations, validation, rollback, Git, dependencies, and deployment.

Current behavior:

- Governance remains separate from interface and semantic interpretation layers;
- authorization is not created by ACLI Next;
- approval and authorization state remain governance-owned.

Limitation:

- ordinary natural-language development still requires a stronger bridge from semantic intent to governance-ready implementation proposal.

### 3.7 Replay

Implemented evidence:

- transport replay;
- unified replay reconstruction;
- Replay summaries;
- per-capability replay modules;
- Replay-visible conversational, UBTR, CSA, execution-plan, and dashboard artifacts.

Current behavior:

- both `aigol next` and conversational routing produce Replay-visible records;
- composing a message does not itself create execution records until submission.

Limitation:

- Replay continuity exists, but the complete natural-language-to-development chain is split across separate runtime surfaces rather than one default `aigol next` path.

### 3.8 Worker Platform

Implemented evidence:

- worker registration, assignment, dispatch, invocation, result capture, and validation modules;
- concrete workers for filesystem mutation, patching, validation, Git, dependency management, and deployment.

Current behavior:

- Worker Platform can execute bounded certified operations.

Limitation:

- ordinary natural-language requests are not yet automatically transformed into a worker-ready governed development plan through default `aigol next`.

## 4. Canonical Pipeline Verification

| Pipeline stage | Operational today | Evidence | Readiness |
| --- | --- | --- | --- |
| Terminal -> `aigol next` | Yes | `aigol/cli/aigol_cli.py`, ACLI Next modules | Ready |
| AiGOL Next conversational UX | Yes | persistent REPL, message composer, dashboard rendering | Ready |
| PGSP session attachment | Yes | certified G12 PGSP responsibility clarification | Ready |
| UBTR semantic interpretation | Yes | UBTR translation and cognition modules; G13-01 | Ready |
| CSA structured semantic output | Yes | canonical semantic artifact runtime | Ready |
| Platform Core / OCS workflow generation | Partial | execution-plan preview and conversational routing exist | Partially ready |
| Governance preparation | Partial | governance modules exist; semantic-to-proposal bridge not default | Partially ready |
| Worker delegation | Partial | workers exist; ordinary NL request does not default to worker-ready plan | Partially ready |
| Replay generation | Yes | conversational, execution-plan, dashboard, UBTR, CSA replay evidence | Ready |

## 5. Natural Language Readiness Matrix

| Capability | Current support | Status |
| --- | --- | --- |
| Ordinary natural-language input | `aigol next` accepts prompts and the conversational routing runtime accepts plain prompts | Ready |
| Multi-line message composition | Message Composer supports buffer, preview, clear, cancel, and send | Ready |
| Intent understanding | UBTR and conversational routing detect action, domain, ambiguity, clarification, and workflow candidates | Ready |
| Semantic normalization | UBTR creates normalized intent and translation artifacts | Ready |
| Structured development intent | CSA creates canonical semantic artifacts, but default `aigol next` does not surface them as the primary development path | Partially ready |
| Governed workflow generation | Conversational routing can select workflows; default `aigol next` mainly presents workflow state and preview | Partially ready |
| Execution planning | Platform Core execution-plan preview exists | Ready for preview, partial for full implementation plan |
| Governance preparation | Governance modules exist; natural-language-to-approval package is not fully defaulted | Partially ready |
| Worker delegation | Worker Platform and workers exist; natural-language automatic worker delegation is not default | Partially ready |
| Replay generation | Replay-visible artifacts are produced by each implemented stage | Ready |
| Human-friendly response | ACLI Next renders summaries and dashboard; rich UBTR governance-to-human rendering is still uneven in the default path | Partially ready |

## 6. Example Request Assessment

Example:

```text
aigol next

Add GitHub Actions support.
```

Observed implementation evidence:

1. The conversational routing runtime can process the prompt through UBTR / CSA without failing closed.
2. The same prompt is classified as requiring clarification through `HUMAN_INTENT_CLARIFICATION_INTAKE`.
3. The default `aigol next --prompt "Add GitHub Actions support."` creates a conversational presentation artifact, execution-plan preview, dashboard update, and Replay-visible run.
4. The default `aigol next` path does not produce a complete implementation proposal, governance approval package, worker delegation, validation suite, or mutation plan for this request.

Assessment:

```text
the prompt is accepted and governed, but it is not yet automatically transformed into a full governed development workflow
```

This is partial readiness. The missing work is integration of existing semantic routing and governed development workflow generation into the default `aigol next` experience.

## 7. Human Experience Assessment

An ordinary developer can start `aigol next`, compose a message, submit it, and receive a governed dashboard and execution-plan preview.

The developer does not need to know Replay paths, Platform Core module names, worker names, or governance internals to initiate the conversation.

However, the developer may still need platform knowledge when:

- a request is too broad or ambiguous and requires clarification;
- the default `aigol next` output presents internal workflow labels instead of a direct next human action;
- the prompt requires translation into a milestone or governance artifact;
- the prompt requires implementation planning rather than presentation-only workflow visibility;
- the task requires choosing among existing capabilities, operational extensions, or unsupported work;
- the workflow needs to progress from semantic intent into proposal, approval, worker delegation, validation, and certification.

The human experience is suitable for governed conversational entry, but not yet fully natural-language-native development execution.

## 8. Remaining Implementation and Integration Gaps

| Gap | Type | Impact | Recommendation |
| --- | --- | --- | --- |
| Default `aigol next` does not invoke full UBTR / CSA routing path | Integration gap | Ordinary prompts produce presentation/preview rather than full development workflow | Integrate existing conversational routing into default `aigol next` without moving ownership |
| Plain development requests may route to clarification without a guided clarification loop | UX and integration gap | User may not know how to proceed | Surface clarification questions and resume the same governed session |
| Semantic workflow selection is separate from ACLI Next dashboard flow | Integration gap | Replay exists but the user sees fragmented workflow surfaces | Present UBTR, CSA, and OCS routing evidence in the dashboard |
| Natural-language-to-governance-artifact proposal is incomplete as default behavior | Implementation gap | User still needs milestone/artifact knowledge for governance docs | Reuse Governed Development Workflow and OCS proposal formation from semantic intent |
| Worker-ready plan generation is not automatic from ordinary natural language | Implementation gap | User still needs implementation details or manual Codex/Terminal assistance | Bridge approved semantic intent into existing Platform Core candidate and Worker workflows |
| Human-friendly explanation of next action is uneven | UX improvement | Internal labels can leak into the operator experience | Use UBTR governance-to-human translation as default presentation source |
| Non-CLI interfaces remain less mature | Implementation gap | Natural-language support is CLI-primary | Attach future Web/REST/Voice/Mobile through PGSP only |

## 9. Prioritized Recommendations

1. Make the existing UBTR / CSA conversational routing runtime the default semantic intake path for `aigol next`.

2. Preserve ACLI Next as show-guide-delegate only; do not move routing, governance, execution, or Replay ownership into ACLI Next.

3. Surface the following in the ACLI Next dashboard after `/send`:

```text
UBTR translation result
CSA semantic artifact summary
workflow candidate
clarification requirement
next governed human action
Replay references
```

4. Implement a governed clarification loop for ordinary prompts that are semantically valid but underspecified.

5. Bridge semantic development intent into the existing Governed Development Workflow stages:

```text
Capability Discovery
-> Existing Capability Audit
-> Reuse
-> Canonicalization
-> Minimal Extension
-> Implementation Proposal
-> Governance
-> Worker Platform
-> Validation
-> Replay
```

6. Use UBTR governance-to-human translation for operator-facing summaries so ordinary users are not exposed to unnecessary internal architecture labels.

7. Treat future natural-language execution as integration of existing certified components, not as a new natural-language subsystem.

## 10. Responsibility Verification

No ownership migration is required or recommended.

| Component | Responsibility remains |
| --- | --- |
| AiGOL Next | CLI adapter, conversational UX, operator interaction, presentation |
| PGSP | Interface attachment and session invocation boundary |
| UBTR | Semantic interpretation and intent normalization |
| CSA | Structured semantic artifact output |
| Platform Core / OCS | Workflow orchestration, candidate/proposal formation, execution planning |
| Governance | Approval and authorization |
| Replay | Evidence, reconstruction, and execution history |
| Worker Platform | Bounded execution |
| Provider Platform | Non-authoritative provider access and provider governance |
| Platform Digital Twin | Canonical evidence projection |
| Architectural Health | Advisory-only architecture review |

Natural-language development should emerge by composing these certified components. ACLI Next must not become a semantic interpreter, orchestrator, Governance authority, Replay authority, or Worker executor.

## 11. Certification Summary

AiGOL is architecturally capable of supporting ordinary natural-language governed development.

The implementation already contains:

- natural-language conversational entry;
- persistent message composition;
- UBTR translation;
- CSA structured semantic artifacts;
- semantic routing;
- clarification detection;
- execution-plan preview;
- dashboard presentation;
- Governance separation;
- Worker Platform execution surfaces;
- Replay-visible evidence.

The implementation is not yet fully ready for ordinary natural-language development where a user can simply say:

```text
Add GitHub Actions support.
```

and receive a complete governed development workflow without additional platform knowledge.

The missing work is targeted integration and UX refinement over existing certified capabilities.

Final verdict: NATURAL_LANGUAGE_DEVELOPMENT_WORKFLOW_PARTIALLY_READY

## 12. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: NATURAL_LANGUAGE_DEVELOPMENT_WORKFLOW_PARTIALLY_READY
