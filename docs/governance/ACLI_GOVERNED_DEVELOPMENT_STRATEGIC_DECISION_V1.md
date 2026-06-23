# ACLI_GOVERNED_DEVELOPMENT_STRATEGIC_DECISION_V1

Status: Defined

Scope: Strategic decision on whether ACLI should evolve from conversational governance runtime into governed development interface.

Runtime inspection basis:

```text
HIRR exists
workflow routing exists
replay exists
workflow registry exists
governed development workflow absent
governance artifact creation workflow absent
ACLI development execution workflow absent
```

Prior gap analysis verdict:

```text
FOUNDATIONAL_GAPS
```

Strategic recommendation:

```text
STRATEGICALLY_RECOMMENDED
```

Final artifact verdict:

```text
ACLI_GOVERNED_DEVELOPMENT_STRATEGIC_DECISION_V1_DEFINED
```

## 1. Purpose

This artifact determines whether ACLI should evolve into a governed development interface.

This is a strategic decision artifact. It does not claim that governed development workflows currently exist. It does not redesign ACLI, governance, replay, repository mutation, or Product 1.

The decision is grounded in verified runtime findings:

- ACLI has conversational workflow routing.
- ACLI has a workflow registry.
- ACLI has HIRR / clarification capability.
- ACLI has replay-visible runtime behavior.
- ACLI does not currently register governed development workflows.
- ACLI does not currently register governance artifact creation workflows.
- ACLI does not currently expose repository mutation as a governed ACLI workflow.

## 2. Current ACLI Mission

The currently verified ACLI mission is:

```text
conversational governance runtime
```

Current verified capabilities:

| Capability | Runtime status | Strategic meaning |
| --- | --- | --- |
| HIRR / clarification | Present | ACLI can preserve human intent before execution. |
| Workflow routing | Present | ACLI can deterministically select among registered conversational workflows. |
| Workflow registry | Present | ACLI has an explicit executable workflow surface. |
| Replay integration | Present | ACLI can preserve runtime evidence for routed interactions. |
| Fail-closed unsupported intent behavior | Present | ACLI does not silently execute unsupported governed actions. |
| Repository mutation runtime | Present outside ACLI workflow registry | Mutation capability exists, but not as ACLI governed development interface. |

Current mission boundary:

```text
ACLI can govern conversational routing.
ACLI cannot yet execute governed development lifecycles.
```

This boundary is operationally important. ACLI should not be described as a governed development interface until a registered development workflow exists and produces reviewable evidence.

## 3. Governed Development Expansion

Governed development ACLI would mean:

```text
Natural Language
-> HIRR
-> deterministic governed development workflow invocation
-> repository context acquisition
-> proposal
-> human approval
-> bounded authorization
-> repository mutation
-> validation
-> replay
-> review
```

The minimal expansion would not require unrestricted development autonomy. The smallest strategically coherent path is a narrow, explicitly registered workflow for:

```text
GOVERNANCE_ARTIFACT_CREATION
```

This would allow ACLI to execute a bounded development lifecycle for governance artifact creation while preserving:

- Human = Authority
- Replay = Source Of Truth
- LLM proposes
- AiGOL governs
- Worker executes
- Replay records

The expansion should be understood as a governed interface layer over already constrained runtime components, not as autonomous self-modifying governance.

## 4. Benefits

Expected benefits of evolving ACLI into a governed development interface:

| Benefit | Explanation |
| --- | --- |
| Reduced manual prompt-to-copy workflow | Human development requests could move through governed invocation instead of external manual selection. |
| Certification path completion | AEC-001 and later scenarios require an executable governed development path. |
| Evidence continuity | Runtime evidence could be generated at the same point where development action is requested. |
| Deterministic workflow selection | Development requests could be mapped to certified workflows rather than informal operator judgment. |
| Stronger replay auditability | Development lifecycle evidence could be reconstructed from ACLI execution records. |
| Better governance consistency | Approval, authorization, validation, and replay could become part of one governed lifecycle. |
| Dogfooding value | AiGOL would use its own governance model to evolve governance artifacts. |

Strategic benefit summary:

```text
Governed development ACLI closes the gap between specified governance and executable certification evidence.
```

## 5. Costs

Expected implementation and maintenance costs:

| Cost | Explanation |
| --- | --- |
| Workflow implementation | A new registered workflow must be implemented and maintained. |
| Routing updates | Intent classification must route governed development requests to the new workflow without weakening fail-closed behavior. |
| Evidence persistence | HIRR, workflow invocation, approval, authorization, validation, mutation, and replay evidence must be persisted. |
| Approval lifecycle maintenance | Human approval records must be precise, durable, and reviewable. |
| Authorization scope management | Repository mutation must be tightly scoped to approved files and actions. |
| Validation maintenance | Development workflows must preserve deterministic validation behavior such as `git diff --check`. |
| Replay reconstruction burden | Replay must reconstruct each development lifecycle stage. |
| Test and certification upkeep | Each workflow evolution adds certification surface area. |

Cost summary:

```text
The cost is substantial but bounded if the first workflow is narrow.
```

The cost becomes unacceptable only if ACLI is expanded directly into a broad generic development executor without first certifying a minimal governed path.

## 6. Architectural Impact

Architectural impact is significant but not architectural replacement.

Existing runtime components already provide part of the required substrate:

- HIRR / clarification intake
- workflow registry
- deterministic conversational routing
- replay-visible routing artifacts
- lower-level repository mutation worker
- fail-closed unsupported intent detection

Required architectural impact:

| Area | Impact |
| --- | --- |
| Workflow registry | Add explicit governed development workflow entries. |
| Workflow selection | Route recognized governed development intent to certified workflows. |
| Runtime lifecycle | Bridge routing to proposal, approval, authorization, mutation, validation, and replay. |
| Repository mutation | Integrate or wrap mutation runtime under ACLI workflow authority. |
| Replay | Record complete development lifecycle evidence, not only routing evidence. |
| Validation | Bind validation output to the execution evidence package. |

Non-impact boundaries:

- No constitutional redesign is required.
- No governance redesign is required.
- No replay redesign is required.
- No Product 1 redesign is required.
- No unrestricted autonomous mutation path is required.

Architectural impact summary:

```text
ACLI needs a new executable workflow bridge, not a new governance architecture.
```

## 7. Risks

Governance and operational risks:

| Risk | Impact | Required control |
| --- | --- | --- |
| Overbroad development workflow | Could weaken mutation boundaries | Start with narrow governance artifact creation workflow. |
| Approval ambiguity | Could create unclear human authority evidence | Require explicit approval artifacts. |
| Authorization drift | Could allow mutation beyond approved scope | Bind mutation to bounded authorization scope. |
| Replay incompleteness | Could prevent certification | Fail closed when evidence is missing. |
| Workflow selection ambiguity | Could route unsafe requests incorrectly | Preserve deterministic selection and escalation. |
| Governance artifact mutation risk | Could alter constitutional artifacts incorrectly | Restrict first workflow to approved artifact class and validation gates. |
| Operator overtrust | Could mistake routing for execution readiness | Maintain visible readiness status and limitations. |

Primary strategic risk:

```text
ACLI could be mistaken for a governed development interface before runtime support exists.
```

Risk posture:

```text
acceptable only if expansion is narrow, explicitly registered, approval-bound, authorization-bound, validation-bound, replay-bound, and fail-closed
```

## 8. Alternatives

### 8.1 Governance-Only ACLI

Description:

```text
ACLI remains a conversational governance and routing interface.
```

Benefits:

- lowest implementation cost
- lowest mutation risk
- preserves current runtime boundary
- avoids expanding certification scope

Costs:

- does not close governed development readiness gap
- does not replace manual ChatGPT -> prompt -> Codex -> copy/paste development workflow
- does not enable AEC-001 positive execution path
- keeps certification evidence dependent on external manual work

Assessment:

```text
safe but strategically insufficient
```

### 8.2 Governed Development ACLI

Description:

```text
ACLI becomes the governed entrypoint for development workflows.
```

Benefits:

- directly addresses foundational gap
- enables executable certification evidence
- aligns runtime with governed development specifications
- supports dogfooding of AiGOL governance

Costs:

- substantial implementation work
- larger certification surface
- higher replay and approval evidence burden
- stronger testing and review obligations

Assessment:

```text
strategically valuable but must begin narrowly
```

### 8.3 Hybrid Model

Description:

```text
ACLI remains governance-first while adding a narrow governed development workflow family.
```

Benefits:

- preserves current conversational governance mission
- adds only certified development workflows
- avoids generic unrestricted development execution
- allows phased certification beginning with governance artifact creation

Costs:

- still requires implementation work
- requires clear operator messaging
- requires strict workflow boundaries

Assessment:

```text
preferred
```

## 9. Recommendation

Recommended direction:

```text
hybrid governed development ACLI
```

ACLI should evolve into a governed development interface, but only through a narrow, certified workflow path.

The recommended first workflow is:

```text
GOVERNANCE_ARTIFACT_CREATION
```

Reasoning:

- The runtime already has registry, routing, HIRR, and replay primitives.
- The current gap is foundational but bounded.
- Governed development is necessary to close certification evidence gaps.
- A narrow governance artifact workflow is the safest first positive path.
- Repository mutation capability exists but should only be used through approved, authorized, replayed workflow execution.

Recommended strategic constraints:

- Do not introduce generic autonomous development execution first.
- Do not bypass human approval.
- Do not bypass authorization scope.
- Do not treat routing as execution.
- Do not claim readiness until actual evidence exists.
- Preserve fail-closed behavior for unsupported development intent.

Strategic recommendation:

```text
STRATEGICALLY_RECOMMENDED
```

## 10. Final Verdict

Final verdict:

```text
STRATEGICALLY_RECOMMENDED
```

Rationale:

ACLI should evolve into a governed development interface because the verified runtime already contains the necessary governance-facing primitives: HIRR, workflow routing, workflow registry, replay integration, and fail-closed behavior. However, the expansion should proceed through a hybrid model: ACLI remains governance-first while adding narrowly registered governed development workflows.

The first strategic target should be a bounded `GOVERNANCE_ARTIFACT_CREATION` workflow. This directly addresses the verified absence of governed development execution without assuming generic development capabilities that do not yet exist.

Final artifact verdict:

```text
ACLI_GOVERNED_DEVELOPMENT_STRATEGIC_DECISION_V1_DEFINED
```
