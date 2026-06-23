# ACLI_GOVERNED_DEVELOPMENT_GAP_ANALYSIS_V1

Status: Defined

Scope: Gap analysis from actual ACLI runtime capabilities to governed development interface readiness.

Runtime inspection basis:

```text
workflow registry exists
workflow routing exists
HIRR exists
replay integration exists
repository mutation runtime exists
```

Verified missing:

```text
GOVERNANCE_ARTIFACT_CREATION workflow
ACLI_GOVERNED_DEVELOPMENT_WORKFLOW
generic governed development workflow
repository mutation registered as ACLI workflow
```

Final gap verdict:

```text
FOUNDATIONAL_GAPS
```

Final artifact verdict:

```text
ACLI_GOVERNED_DEVELOPMENT_GAP_ANALYSIS_V1_DEFINED
```

## 1. Purpose

This artifact determines what is required to transform ACLI from a conversational governance runtime into a governed development interface.

This analysis is based on actual runtime inspection. It does not assume that specification-defined capabilities are executable unless runtime code currently exposes them.

This artifact does not redesign ACLI, governance, replay, workflows, repository mutation, or Product 1.

## 2. Current ACLI Capabilities

Verified runtime capabilities:

| Capability | Runtime evidence | Current assessment |
| --- | --- | --- |
| Conversational workflow registry | `aigol/runtime/conversational_cli_runtime.py::workflow_registry` | Present |
| Conversational workflow routing | `route_conversational_cli_intent` | Present |
| Replay-visible routing artifacts | conversational routing replay steps | Present |
| HIRR / clarification intake | `human_intent_clarification_intake_runtime.py` | Present |
| Native development intent routing | `conversation_native_development_intent_routing.py` | Present |
| Repository mutation worker | `repository_mutation_worker_runtime.py` | Present as lower-level runtime |
| Fail-closed generic governed artifact detection | `human_execution_intent_detection.py` | Present |

The current ACLI runtime can route conversational prompts to a static set of registered workflow IDs. The registry is deterministic and in-code, not discovered dynamically from governance specifications.

The current registry includes workflows such as:

- `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION`
- `NATIVE_DEVELOPMENT_INTENT_ROUTING`
- `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION`
- `DOMAIN_EXECUTION_AUTHORIZATION`
- `DOMAIN_WORKER_EXECUTION`
- `HUMAN_INTENT_CLARIFICATION_INTAKE`
- `DEFAULT_PROVIDER_ASSISTED_CONVERSATION`

Current routing artifacts preserve safety flags such as:

- provider not invoked during routing
- worker not invoked during routing
- authorization not created during routing
- execution not requested during routing
- approval not bypassed
- governance not mutated
- replay not mutated

## 3. Missing Capabilities

Missing governed development capabilities:

| Missing capability | Current runtime state | Impact |
| --- | --- | --- |
| `GOVERNANCE_ARTIFACT_CREATION` workflow | Not registered | Blocks AEC-001 positive path |
| `ACLI_GOVERNED_DEVELOPMENT_WORKFLOW` workflow | Not registered | Blocks direct governed development lifecycle execution |
| Generic governed development workflow | Not registered | Generic development prompts cannot enter governed development lifecycle |
| Repository mutation as ACLI workflow | Repository mutation runtime exists but is not registered as ACLI workflow | Blocks natural-language-to-mutation path |
| Governance artifact creation path | Generic governed artifact creation fails closed | Blocks documentation-governance artifact creation through ACLI |
| Development evidence continuity | Not emitted by current routing workflow | Blocks certification evidence completeness |

The missing capabilities are not merely naming gaps. They are executable interface gaps: the runtime has no registered workflow that takes a normal development request through intent, workflow invocation, repository context, approval, authorization, mutation, validation, and replay.

## 4. Workflow Gap Analysis

Current workflow registry behavior:

```text
workflow_registry()
-> static registered workflow tuple
-> _workflow_by_id()
-> _classify_workflow()
-> route_conversational_cli_intent()
```

Current selection behavior:

- deterministic prompt rules select a registered workflow
- unsupported generic governed execution intent fails closed
- selected workflows produce replay-visible routing and workflow selection artifacts
- selection does not invoke providers, workers, authorization, execution, governance mutation, or replay mutation

Verified gap:

```text
GOVERNANCE_ARTIFACT_CREATION is not in the registered workflow set.
```

Verified gap:

```text
ACLI_GOVERNED_DEVELOPMENT_WORKFLOW is not in the registered workflow set.
```

Current generic governed artifact creation handling:

```text
GENERIC_GOVERNED_ARTIFACT_CREATION
-> FAIL_CLOSED_NO_CERTIFIED_ARTIFACT_CREATION_ENTRYPOINT
```

Current generic governed execution handling:

```text
GENERIC_GOVERNED_EXECUTION_REQUEST
-> FAIL_CLOSED_NO_CERTIFIED_GENERIC_EXECUTION_ENTRYPOINT
```

Conclusion:

The workflow registry is real, but governed development is not registered as an executable workflow. ACLI therefore remains a conversational workflow router rather than a governed development interface.

## 5. Repository Mutation Integration Gap

Verified repository mutation runtime:

```text
aigol/runtime/repository_mutation_worker_runtime.py
```

Capabilities present:

- create certified patch proposal artifact
- apply approved file mutations
- persist repository mutation replay evidence
- reconstruct mutation replay
- prevent unauthorized mutation
- fail closed on invalid source artifacts, unapproved mutations, forbidden paths, target escape, and replay reuse

Critical current limitations for ACLI-governed development:

- repository mutation worker is not registered as an ACLI conversational workflow
- natural-language ACLI routing does not select repository mutation worker for governed development requests
- generic governed artifact creation fails closed before reaching mutation
- mutation proposal requires approved file mutations and authorization references
- mutation runtime explicitly forbids governance artifact mutation through its proposal scope

Current mutation runtime is therefore a lower-level governed mutation component, not an ACLI-level governed development workflow.

Implication:

Repository mutation capability exists, but the interface chain from:

```text
Human request
-> ACLI workflow selection
-> repository mutation
```

is not currently executable for governed development.

## 6. Governance Artifact Creation Gap

AEC-001 requires:

```text
Governance Artifact Creation
```

Current runtime state:

- no `GOVERNANCE_ARTIFACT_CREATION` workflow is registered
- generic governed artifact creation is detected but fails closed
- repository mutation worker explicitly marks governance artifact mutation as not allowed in patch proposal scope
- no ACLI workflow currently bridges approval, authorization, and governance markdown creation

This means ACLI cannot currently perform the AEC-001 positive path as an actual runtime workflow.

Current safe behavior:

```text
fail closed
```

Readiness consequence:

The fail-closed behavior is correct, but the positive governed development capability is absent.

## 7. Minimal Viable Governed Development Workflow

The smallest possible runtime workflow required to move ACLI toward governed development is:

```text
Human Request
-> HIRR / Intent Evidence
-> Workflow Selection: GOVERNANCE_ARTIFACT_CREATION
-> Repository Context Evidence
-> Development Proposal
-> Human Approval
-> Bounded Authorization
-> Governance Artifact Creation
-> Validation: git diff --check
-> Replay Package
-> Review Artifact
```

Minimum workflow class:

```text
GOVERNANCE_ARTIFACT_CREATION
```

Minimum registered workflow entry:

```text
workflow_id: GOVERNANCE_ARTIFACT_CREATION
existing_cli_command: aigol conversation
existing_runtime: governed_development_governance_artifact_creation_runtime
clarification_required: false or conditional
```

Minimum runtime behavior:

- accept resolved governance artifact creation intent
- require repository context
- produce proposal before mutation
- require explicit human approval
- issue bounded authorization
- create only approved artifact
- run documentation validation
- emit replay-visible evidence
- fail closed when any mandatory evidence is missing

This workflow must be narrower than full governed development. It should certify one minimal positive path before expanding to runtime code or test mutation.

## 8. Dependency Analysis

Required dependencies:

| Dependency | Current state | Required for governed development |
| --- | --- | --- |
| HIRR / intent resolution | Present | Must emit governed development evidence |
| Workflow registry | Present | Must register governed development workflow |
| Workflow selection logic | Present | Must route governed artifact creation to registered workflow |
| Repository context runtime | Specification exists; runtime integration incomplete | Must produce context evidence |
| Approval runtime | Adjacent components exist | Must bind human approval to proposed mutation |
| Authorization runtime | Adjacent components exist | Must bind approved scope to mutation permission |
| Repository mutation worker | Present | Must be integrated or wrapped for approved development mutation |
| Validation command runner | Adjacent capability exists | Must persist `git diff --check` result |
| Replay runtime | Present in adjacent forms | Must reconstruct governed development lifecycle |
| Review artifact generation | Specification exists | Must produce scenario review evidence |

Dependency order:

```text
registered workflow
-> intent-to-workflow routing
-> repository context evidence
-> proposal and approval evidence
-> authorization evidence
-> mutation integration
-> validation evidence
-> replay package
-> review artifact
```

The registered workflow must come before AEC-001 rerun. Without it, ACLI cannot deterministically select the certification scenario workflow.

## 9. Readiness Impact

Impact on:

```text
ACLI_GOVERNED_DEVELOPMENT_READY
```

is:

```text
BLOCKED
```

Reason:

ACLI currently has real conversational governance routing and lower-level mutation capability, but it does not expose governed development as a registered executable ACLI workflow.

Current readiness state:

| Readiness area | Status |
| --- | --- |
| Conversational workflow routing | READY |
| HIRR / clarification intake | READY |
| Replay-visible routing | READY |
| Repository mutation worker | PARTIALLY_READY |
| Governance artifact creation workflow | NOT_READY |
| Governed development workflow | NOT_READY |
| AEC-001 runtime execution | NOT_READY |
| ACLI governed development readiness | BLOCKED |

This is a foundational gap because the missing component is the actual runtime entrypoint from ACLI into governed development.

## 10. Final Verdict

Final gap verdict:

```text
FOUNDATIONAL_GAPS
```

Rationale:

The current ACLI runtime has a deterministic workflow registry, workflow routing, HIRR, replay-visible routing, and lower-level repository mutation capability. However, the governed development workflow itself is not registered or executable through ACLI. Generic governed artifact creation fails closed, and repository mutation is not exposed as an ACLI workflow.

Therefore ACLI is not yet a governed development interface. It remains a conversational governance runtime with adjacent mutation components.

Final artifact verdict:

```text
ACLI_GOVERNED_DEVELOPMENT_GAP_ANALYSIS_V1_DEFINED
```
