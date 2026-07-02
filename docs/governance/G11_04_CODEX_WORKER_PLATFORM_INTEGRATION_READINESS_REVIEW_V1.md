# G11-04 Codex Worker Platform Integration Readiness Review V1

Status: Codex integration ready for specification.

Final verdict: CODEX_WORKER_PLATFORM_INTEGRATION_READY_FOR_SPECIFICATION

## 1. Executive Summary

Generation 10 certified ACLI Next as the canonical operational development interface. Generation 11 certified conversational and persistent ACLI Next usage as architecture-preserving UX layers.

Codex remains a major practical development participant in the current hybrid workflow. It performs repository inspection, implementation assistance, file mutation through the local workspace, validation command execution, and governance artifact drafting.

Current finding:

```text
Codex should not remain an indefinite external development tool.
```

However, Codex must not be integrated as a single broad authority.

Codex is ready for specification as governed capability only if the integration preserves strict role separation:

1. Codex as non-authoritative cognition/provider capability.
2. Codex as bounded Worker Platform execution capability.

These roles must be separately authorized, separately replayed, separately governed, and separately certified.

## 2. Current Codex Usage In Development Workflow

Current usage pattern:

```text
Human
-> ACLI Next / governance intent
-> Codex
-> repository inspection
-> file edits
-> terminal validation
-> governance artifact creation
-> human review
```

Codex currently assists with:

- reading repository state;
- interpreting governance artifacts;
- drafting readiness, specification, implementation, architecture review, and certification documents;
- editing files;
- running validation commands;
- summarizing results;
- preserving practical continuity across the hybrid workflow.

This use is operationally valuable, but it remains outside certified AiGOL execution authority unless explicitly routed through governed capabilities.

## 3. Certified Baseline

Certified architecture already provides the required integration owners:

| Component | Certified Role |
| --- | --- |
| ACLI Next | Thin human interface: show, guide, delegate. |
| Platform Core | Orchestration authority. |
| Governance | Authorization, approval, admissibility, certification. |
| Replay | Evidence, reconstruction, execution history. |
| Worker Platform | Bounded authorized execution. |
| External Provider Platform / provider boundary | Non-authoritative cognition or proposal support. |
| Platform Digital Twin | Canonical architectural evidence projection. |
| Architectural Health | Deterministic advisory findings only. |

No new authority layer is required to integrate Codex.

## 4. Codex Role Classification

Codex can act in two distinct roles today.

| Role | Current Behavior | Required Certified Boundary |
| --- | --- | --- |
| Cognition provider | Interprets tasks, proposes plans, drafts artifacts, explains code and governance context. | Must remain non-authoritative provider/cognition output. |
| Execution worker | Edits files, runs commands, validates changes, inspects local state. | Must run only through Worker Platform authorization and Replay evidence. |

Codex must not be treated as both roles in one undifferentiated capability.

Role separation is required.

## 5. Worker Platform Boundary Review

Worker Platform owns execution only.

If Codex is integrated as a Worker capability, it must:

- receive an explicit authorized worker request;
- operate inside a declared workspace scope;
- perform only allowlisted operation classes;
- produce bounded output;
- preserve before/after evidence where mutation occurs;
- fail closed on scope ambiguity;
- never self-authorize;
- never approve its own plan;
- never mutate Governance or Replay outside certified paths;
- never perform deployment or remote operations unless those capabilities are separately certified.

Codex-as-worker should initially be limited to narrow tasks such as:

- read-only repository inspection;
- governance artifact drafting;
- governed file mutation through existing mutation envelopes;
- targeted validation through existing validation workers;
- summarization of Replay-visible evidence.

It should not begin as broad shell access.

## 6. External Provider Platform Boundary Review

LLM providers remain non-authoritative.

If Codex is integrated as a cognition/provider capability, it must:

- generate proposals, explanations, classifications, or candidate artifacts only;
- never authorize execution;
- never approve changes;
- never certify outcomes;
- never override Governance;
- never repair Replay;
- never execute hidden operations;
- clearly label provider output as advisory or candidate material.

Provider output may inform OCS or Platform Core, but Governance and Human Authority remain responsible for approval and certification.

## 7. Governance Authorization Requirements

Any Codex integration requires explicit Governance policy.

Minimum Governance requirements:

- role declaration: provider, worker, or both as separated capabilities;
- allowed operation class;
- workspace scope;
- mutation scope;
- command allowlist where commands are involved;
- network policy;
- provider/cognition policy;
- approval requirements;
- authorization artifact;
- fail-closed conditions;
- post-operation validation requirements.

Codex must not inherit authority from the human conversation or from ACLI Next presentation state.

## 8. Replay Evidence Requirements

Replay must remain the evidence authority.

Required evidence for Codex-as-provider:

- prompt/input hash;
- provider identity;
- response hash;
- model/tool identity where applicable;
- advisory classification;
- no-authority flags;
- downstream use reference.

Required evidence for Codex-as-worker:

- authorized request;
- worker identity;
- operation scope;
- pre-state where applicable;
- command or mutation intent;
- bounded stdout/stderr or result summary;
- post-state where applicable;
- validation result;
- failure reason if fail-closed;
- no self-authorization flags.

Codex must not maintain an alternate evidence ledger.

## 9. ACLI Next Role

ACLI Next remains a thin human interface.

ACLI Next may:

- present Codex capability availability;
- show whether Codex would be used as provider or worker;
- display required approvals;
- display Replay summaries;
- display hybrid/external status;
- guide the human through confirmation.

ACLI Next must not:

- invoke Codex with hidden authority;
- authorize Codex execution;
- treat Codex output as approval;
- bypass Governance;
- bypass Replay;
- bypass Worker Platform.

## 10. Platform Core Orchestration

Platform Core remains the orchestration authority.

If Codex is integrated, Platform Core should coordinate:

- capability discovery;
- role selection;
- Governance authorization request;
- Worker or provider delegation;
- Replay reference collection;
- validation sequencing;
- result presentation through ACLI Next.

Platform Core must not become the Codex execution engine or a provider authority.

## 11. Role Separation Requirement

Codex integration requires two separately specified tracks.

### 11.1 Codex As Cognition Provider

Purpose:

```text
advisory reasoning, proposal drafting, explanation, and candidate formation
```

Authority:

```text
non-authoritative
```

Certified owners:

- OCS may use candidate material.
- Governance decides admissibility.
- Replay records provider evidence.
- ACLI Next displays advisory output.

### 11.2 Codex As Execution Worker

Purpose:

```text
bounded authorized development work inside certified Worker Platform scope
```

Authority:

```text
execution only after Governance authorization
```

Certified owners:

- Governance authorizes.
- Worker Platform executes.
- Replay records evidence.
- Platform Core coordinates.
- ACLI Next displays status.

### 11.3 Mixed Role Prohibition

The same Codex invocation must not both:

- propose the plan;
- approve the plan;
- execute the plan;
- certify the outcome.

When both cognition and execution are needed, they must be separated into distinct governed steps with Replay evidence between them.

## 12. Readiness Assessment

| Criterion | Finding |
| --- | --- |
| Operational value | Very high. Codex currently reduces development friction significantly. |
| Hybrid reduction | High. Integration would reduce external copy/paste and terminal dependence. |
| Architectural readiness | Ready for specification if role separation is enforced. |
| Governance readiness | Requires explicit authorization policy before implementation. |
| Replay readiness | Existing evidence patterns are sufficient for specification. |
| Worker Platform readiness | Ready for narrow bounded worker specification, not broad shell authority. |
| Provider readiness | Ready for non-authoritative cognition/provider specification. |
| Risk | High if Codex is integrated as broad undifferentiated authority. Manageable if split by role. |

## 13. Required Specification Scope

The next artifact should specify:

```text
G11_05_CODEX_GOVERNED_CAPABILITY_INTEGRATION_SPECIFICATION_V1
```

Minimum scope:

- Codex role taxonomy;
- provider-mode boundary;
- worker-mode boundary;
- authorization model;
- Replay evidence model;
- ACLI Next presentation model;
- Platform Core coordination model;
- fail-closed behavior;
- initial allowed use cases;
- explicitly forbidden use cases;
- architecture review requirements.

Recommended first implementation scope after specification:

```text
Codex read-only / advisory provider integration
```

Worker execution should follow only after provider/cognition boundaries are certified or as a separate worker-only capability with no provider reasoning authority.

## 14. Non-Goals

This readiness review does not authorize:

- Codex implementation;
- Codex worker execution;
- provider invocation;
- broad shell access;
- autonomous development;
- self-authorization;
- hidden repository mutation;
- deployment;
- Git remote operations;
- dependency management;
- Governance replacement;
- Replay replacement.

## 15. Final Determination

Codex should not remain an indefinite external temporary tool.

The certified Platform Core architecture is ready to specify Codex integration, provided that Codex is split into separately governed provider/cognition and worker/execution roles.

Codex remains external until that specification, architecture review, implementation, and certification are complete.

Final verdict: CODEX_WORKER_PLATFORM_INTEGRATION_READY_FOR_SPECIFICATION

## 16. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: CODEX_WORKER_PLATFORM_INTEGRATION_READY_FOR_SPECIFICATION
