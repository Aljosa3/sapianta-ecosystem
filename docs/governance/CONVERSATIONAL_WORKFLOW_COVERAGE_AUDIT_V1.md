# CONVERSATIONAL_WORKFLOW_COVERAGE_AUDIT_V1

Status: Complete

Purpose: Audit ACLI conversational workflow coverage from routing through proposal, approval, explanation, execution, validation, and replay.

Target verdict:

```text
CONVERSATIONAL_WORKFLOW_COVERAGE_AUDIT_COMPLETE
```

## 1. Audit Scope

This audit evaluates actual ACLI runtime coverage.

It does not redesign:

- ACLI;
- HIRR;
- workflow selection;
- governance;
- replay;
- approval;
- repository mutation.

The audit distinguishes:

- registered workflow;
- routable workflow;
- interactive ACLI branch support;
- proposal support;
- approval support;
- human-friendly explanation support;
- execution support;
- replay support.

## 2. Source Evidence

### 2.1 Workflow Registry

The conversational workflow registry is defined in:

```text
aigol/runtime/conversational_cli_runtime.py:280
```

Key registered development workflows:

```text
aigol/runtime/conversational_cli_runtime.py:370
GOVERNANCE_ARTIFACT_CREATION

aigol/runtime/conversational_cli_runtime.py:375
GOVERNED_REPOSITORY_MUTATION

aigol/runtime/conversational_cli_runtime.py:380
GOVERNED_DEVELOPMENT_WORKFLOW
```

The registry also includes provider onboarding and bounded file-write session entries:

```text
aigol/runtime/conversational_cli_runtime.py:303
BOUNDED_FILE_WRITE_WORKER_USER_SESSION

aigol/runtime/conversational_cli_runtime.py:391
PROVIDER_ONBOARDING_DOMAIN
```

### 2.2 Operator Summaries

Operator summaries advertise route-level intent in:

```text
aigol/runtime/conversational_cli_runtime.py:1365
```

Relevant summaries:

```text
aigol/runtime/conversational_cli_runtime.py:1420
GOVERNANCE_ARTIFACT_CREATION:
Select the certified governance artifact creation workflow without mutation or approval bypass.

aigol/runtime/conversational_cli_runtime.py:1423
GOVERNED_REPOSITORY_MUTATION:
Select the governed repository mutation workflow without mutation or approval bypass.

aigol/runtime/conversational_cli_runtime.py:1426
GOVERNED_DEVELOPMENT_WORKFLOW:
Select the governed development orchestration workflow without mutation or approval bypass.
```

### 2.3 Interactive Runtime Imports

The interactive CLI imports many conversational workflow constants in:

```text
aigol/cli/aigol_cli.py:201
```

Observed missing imports:

- `GOVERNANCE_ARTIFACT_CREATION`
- `GOVERNED_REPOSITORY_MUTATION`
- `BOUNDED_FILE_WRITE_WORKER_USER_SESSION`
- `PROVIDER_ONBOARDING_DOMAIN`

This means those registered workflows can be routed by `conversational_cli_runtime.py`, but the interactive runtime has no corresponding `CONVERSATIONAL_*` constants for direct branch handling.

### 2.4 Interactive Branches

Selection-only/read-only group:

```text
aigol/cli/aigol_cli.py:4034
```

Read-only handler:

```text
aigol/cli/aigol_cli.py:7868
```

Domain staged lifecycle branches:

```text
aigol/cli/aigol_cli.py:4074
aigol/cli/aigol_cli.py:4113
aigol/cli/aigol_cli.py:4152
aigol/cli/aigol_cli.py:4191
aigol/cli/aigol_cli.py:4239
aigol/cli/aigol_cli.py:4280
aigol/cli/aigol_cli.py:4389
aigol/cli/aigol_cli.py:4431
aigol/cli/aigol_cli.py:4483
aigol/cli/aigol_cli.py:4528
aigol/cli/aigol_cli.py:4575
```

Governed development branch:

```text
aigol/cli/aigol_cli.py:4755
```

Human-friendly explanation integration:

```text
aigol/cli/aigol_cli.py:4769
```

Unsupported workflow fallback:

```text
aigol/cli/aigol_cli.py:5442
```

## 3. CURRENT_CONVERSATIONAL_WORKFLOW_MATRIX

Legend:

- `YES`: supported in the operational interactive ACLI path.
- `PARTIAL`: present only for a stage, selection, cognition, or dependent continuation.
- `NO`: absent in the operational interactive ACLI path.
- `N/A`: not applicable to the workflow intent.
- `FAILS_BEFORE_PROPOSAL`: routing can select the workflow, but interactive ACLI reaches unsupported fallback.

| Workflow | Routing | Proposal | Approval | Explanation | Execution | Replay | Current Coverage |
|---|---:|---:|---:|---:|---:|---:|---|
| `CREATE_DOMAIN_TRADING` | YES | PARTIAL | PARTIAL | NO | PARTIAL | YES | Native development route/handoff path |
| `CREATE_DOMAIN_MARKETING` | YES | PARTIAL | PARTIAL | NO | PARTIAL | YES | Native development route/handoff path |
| `CREATE_DOMAIN_COMPLIANCE_CLARIFICATION` | YES | PARTIAL | PARTIAL | NO | PARTIAL | YES | Clarification/domain proposal path |
| `DOMAIN_ADAPTATION_REFERENCE` | YES | NO | NO | NO | YES | YES | Semantic reference resolution only |
| `OPERATOR_DECISION_SUPPORT` | YES | PARTIAL | PARTIAL | NO | YES | YES | Recommendation/continuity path |
| `SHOW_LATEST_REPLAY_CHAIN` | YES | N/A | N/A | NO | YES | YES | Read-only command |
| `REVIEW_LATEST_AUDIT` | YES | N/A | N/A | NO | YES | PARTIAL | Read-only audit preview |
| `IMPROVE_PROVIDER_LAYER` | YES | NO | NO | NO | YES | PARTIAL | Read-only guidance |
| `SHOW_STATUS` | YES | N/A | N/A | NO | YES | PARTIAL | Read-only status |
| `SHOW_DASHBOARD` | YES | N/A | N/A | NO | YES | PARTIAL | Read-only dashboard |
| `NATIVE_DEVELOPMENT_INTENT_ROUTING` | YES | PARTIAL | PARTIAL | NO | PARTIAL | YES | Native development handoff path |
| `NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION` | YES | PARTIAL | PARTIAL | NO | PARTIAL | YES | Context integration with optional continuation |
| `DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME` | YES | NO | NO | NO | NO | YES | Selection-only/read-only |
| `CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME` | YES | NO | NO | NO | NO | YES | Selection-only/read-only |
| `PROPOSAL_RUNTIME` | YES | NO | NO | NO | NO | YES | Selection-only/read-only |
| `IMPROVEMENT_PROPOSAL_RUNTIME` | YES | NO | NO | NO | NO | YES | Selection-only/read-only |
| `FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH` | YES | NO | NO | NO | NO | YES | Selection-only/read-only |
| `IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME` | YES | NO | NO | NO | NO | YES | Selection-only/read-only |
| `AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION` | YES | NO | NO | NO | NO | YES | Selection-only/read-only |
| `AI_DECISION_VALIDATOR_CAPABILITY_MODEL` | YES | NO | NO | NO | NO | YES | Selection-only/read-only |
| `AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE` | YES | NO | NO | NO | NO | YES | Selection-only/read-only |
| `OCS_LLM_COGNITION` | YES | N/A | N/A | NO | YES | YES | Cognition/advisory execution |
| `BOUNDED_FILE_WRITE_WORKER_USER_SESSION` | YES | NO | NO | NO | NO | YES | Registered/routable, unsupported interactive branch |
| `AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW` | YES | PARTIAL | YES | NO | PARTIAL | YES | Domain approval binding path |
| `DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE` | YES | N/A | PARTIAL | NO | YES | YES | Domain execution-ready bridge |
| `DOMAIN_EXECUTION_AUTHORIZATION` | YES | N/A | YES | NO | YES | YES | Authorization artifact creation |
| `DOMAIN_WORKER_REQUEST` | YES | N/A | PARTIAL | NO | YES | YES | Worker request creation |
| `DOMAIN_WORKER_ASSIGNMENT` | YES | N/A | N/A | NO | YES | YES | Worker assignment |
| `DOMAIN_WORKER_DISPATCH` | YES | N/A | N/A | NO | YES | YES | Worker dispatch |
| `DOMAIN_WORKER_INVOCATION` | YES | N/A | N/A | NO | YES | YES | Worker invocation |
| `DOMAIN_WORKER_EXECUTION` | YES | N/A | N/A | NO | YES | YES | Worker execution start |
| `DOMAIN_WORKER_RESULT_CAPTURE` | YES | N/A | N/A | NO | YES | YES | Result capture |
| `DOMAIN_WORKER_RESULT_VALIDATION` | YES | N/A | N/A | NO | YES | YES | Result validation |
| `DOMAIN_POST_EXECUTION_REPLAY_REVIEW` | YES | N/A | N/A | NO | YES | YES | Replay review |
| `DOMAIN_GOVERNED_TERMINATION` | YES | N/A | N/A | NO | YES | YES | Governed termination |
| `GOVERNANCE_ARTIFACT_CREATION` | YES | NO | NO | NO | NO | YES | FAILS_BEFORE_PROPOSAL |
| `GOVERNED_REPOSITORY_MUTATION` | YES | NO | NO | NO | NO | YES | FAILS_BEFORE_PROPOSAL |
| `GOVERNED_DEVELOPMENT_WORKFLOW` | YES | YES | YES | YES | YES | YES | Full certified bridge |
| `HUMAN_INTENT_CLARIFICATION_INTAKE` | YES | N/A | N/A | NO | YES | YES | Clarification/read-only handler |
| `PROVIDER_ONBOARDING_DOMAIN` | YES | NO | NO | NO | NO | YES | Registered/routable, unsupported interactive branch |
| `DEFAULT_PROVIDER_ASSISTED_CONVERSATION` | YES | N/A | N/A | NO | YES | YES | Provider conversation/fallback path |

## 4. Coverage Analysis

### 4.1 Fully Covered Workflow

Only one workflow currently satisfies the full operator-facing development chain:

```text
GOVERNED_DEVELOPMENT_WORKFLOW
```

Coverage:

- routing supported;
- proposal supported;
- approval supported;
- human-friendly explanation supported;
- execution supported;
- validation supported;
- replay supported.

Evidence:

```text
aigol/cli/aigol_cli.py:4755
aigol/cli/aigol_cli.py:4769
tests/test_acli_governed_development_execution_bridge_v1.py
```

### 4.2 Registered But Unsupported In Interactive Branching

The following workflows are registered and routable, but the interactive ACLI loop does not handle them as executable conversational branches:

- `GOVERNANCE_ARTIFACT_CREATION`
- `GOVERNED_REPOSITORY_MUTATION`
- `BOUNDED_FILE_WRITE_WORKER_USER_SESSION`
- `PROVIDER_ONBOARDING_DOMAIN`

They fall through to:

```text
aigol/cli/aigol_cli.py:5442
unsupported conversational workflow selection: <workflow_id>
```

### 4.3 Selection-Only Workflows

Several workflows intentionally select an entrypoint without execution:

- `DOMAIN_LIFECYCLE_GOVERNANCE_RUNTIME`
- `CAPABILITY_LIFECYCLE_GOVERNANCE_RUNTIME`
- `PROPOSAL_RUNTIME`
- `IMPROVEMENT_PROPOSAL_RUNTIME`
- `FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH`
- `IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME`
- Product 1 definition workflows.

They are routed into the read-only handler at:

```text
aigol/cli/aigol_cli.py:4034
aigol/cli/aigol_cli.py:7939
```

They should not be treated as execution-capable unless a specific bridge is implemented.

### 4.4 Domain Lifecycle Workflows

Domain worker lifecycle workflows have interactive branches and replay support, but they are staged operator actions rather than one complete proposal-to-execution development bridge.

They are supported as lifecycle steps, not as a single human-friendly proposal-and-approval path.

### 4.5 Explanation Coverage

Human-friendly explanation is currently integrated only in the governed development bridge:

```text
aigol/cli/aigol_cli.py:4769
```

All other workflows bypass human-friendly explanation.

This is expected for the first implementation tranche, but it matters for operator usability: route-only, fail-closed, and selection-only paths still expose technical output.

## 5. Gap Analysis

### GAP-001: Governance Artifact Creation Routes But Fails Before Proposal

Observed:

```text
workflow: GOVERNANCE_ARTIFACT_CREATION
FAILED_CLOSED: unsupported conversational workflow selection: GOVERNANCE_ARTIFACT_CREATION
```

Root cause:

- registered in `workflow_registry`;
- routing logic selects it;
- no `CONVERSATIONAL_GOVERNANCE_ARTIFACT_CREATION` import;
- no branch in `run_interactive_conversation`;
- no conversational bridge from selected workflow to proposal/approval/execution.

Impact:

Normal operator governance-artifact prompts fail before proposal and bypass human-friendly explanation.

### GAP-002: Governed Repository Mutation Routes But Lacks Direct Conversational Bridge

`GOVERNED_REPOSITORY_MUTATION` is registered, but not imported or handled in the interactive loop.

The capability exists under governed development, but not as a direct ACLI conversational workflow.

### GAP-003: Explanation Layer Is Not Universal

The explanation layer does not yet cover:

- read-only selections;
- clarification turns;
- fail-closed unsupported workflow turns;
- OCS cognition turns;
- domain lifecycle branches;
- direct governance artifact routing.

### GAP-004: Registry Implies Capability That Interactive Runtime Does Not Provide

The registry contains entries whose operator summaries imply safe selection, but the interactive runtime has no handler for some of them.

This creates operator surprise because `ROUTING DECISION` appears successful before the runtime fails closed as unsupported.

## 6. REQUIRED_CONVERSATIONAL_BRIDGES

### Bridge 1: Governance Artifact Creation Conversational Bridge

Required if `GOVERNANCE_ARTIFACT_CREATION` remains directly routable.

Minimum bridge responsibilities:

- accept selected `GOVERNANCE_ARTIFACT_CREATION`;
- generate proposal from routed prompt;
- render human-friendly explanation;
- require explicit approval;
- execute existing `governance_artifact_creation_runtime`;
- run validation;
- persist replay;
- reconstruct replay.

### Bridge 2: Governed Repository Mutation Conversational Bridge

Required only if `GOVERNED_REPOSITORY_MUTATION` should be directly operator-facing.

Alternative:

Keep direct repository mutation hidden behind `GOVERNED_DEVELOPMENT_WORKFLOW` to reduce operator surface area.

### Bridge 3: Unsupported Workflow Explanation Bridge

Required for user comprehension even when no execution bridge exists.

Minimum behavior:

- explain that routing succeeded;
- explain that no interactive execution bridge exists;
- state that no mutation occurred;
- state that no approval was consumed;
- provide recommended next prompt or supported workflow.

### Bridge 4: Selection-Only Explanation Bridge

Required for read-only workflows.

Minimum behavior:

- explain that the workflow is selection-only;
- explain no proposal/approval/execution will occur;
- show replay location.

## 7. Governance Artifact Creation Decision

Question:

Should `GOVERNANCE_ARTIFACT_CREATION` reuse the governed development bridge, receive its own bridge, or be intentionally blocked?

### Option A: Reuse Existing Governed Development Bridge

Recommended for near-term operator usability.

Rationale:

- `GOVERNED_DEVELOPMENT_WORKFLOW` already composes governance artifact creation and repository mutation.
- It already has proposal, approval, explanation, validation, replay, and reconstruction.
- It avoids introducing a second approval bridge for a similar operator intent.
- It makes prompts such as `Create governance artifact ACLI_USAGE_GUIDELINES_V1...` succeed through the already certified path.

Required change:

- route governance-artifact creation prompts that imply end-to-end repository artifact creation into `GOVERNED_DEVELOPMENT_WORKFLOW`, or
- in the interactive branch, hand selected `GOVERNANCE_ARTIFACT_CREATION` to the existing governed development bridge with workflow evidence preserving the original routing decision.

Risk:

- The governed development bridge currently generates bounded demo-style target names for generic prompts. It may not preserve the requested artifact name without additional proposal-generation work.

### Option B: Create Dedicated Governance Artifact Conversational Bridge

Recommended only if precise governance artifact naming and governance-only mutation are required.

Rationale:

- `governance_artifact_creation_runtime` already exists and is tested.
- Dedicated bridge can preserve artifact-specific intent better.
- It avoids adding repository runtime file mutations when the operator only requested a governance artifact.

Required change:

- import `GOVERNANCE_ARTIFACT_CREATION` in `aigol/cli/aigol_cli.py`;
- add direct branch before unsupported fallback;
- generate proposal and approval artifacts for the existing runtime;
- integrate human-friendly explanation;
- run validation and replay reconstruction.

Risk:

- Duplicates bridge patterns already solved by governed development.
- Increases operator-facing workflow surface.

### Option C: Intentionally Block

Not recommended unless the product decision is that direct governance artifact creation must never be an operator-facing workflow.

If blocked, routing should not present it as a selected certified workflow. It should route to clarification or governed development instead.

## 8. Recommendation

Primary recommendation:

```text
Reuse GOVERNED_DEVELOPMENT_WORKFLOW for normal operator governance-artifact creation prompts unless exact governance-only artifact creation is required.
```

Secondary recommendation:

```text
Add fail-closed explanation coverage for any selected workflow that lacks an interactive branch.
```

Specific priority:

1. Add regression test for `Create governance artifact ACLI_USAGE_GUIDELINES_V1...`.
2. Decide whether this phrase routes to `GOVERNED_DEVELOPMENT_WORKFLOW` or a dedicated governance artifact bridge.
3. If no dedicated bridge is built, remove direct operator routing to `GOVERNANCE_ARTIFACT_CREATION` for ordinary ACLI prompts.
4. Add human-friendly explanation for unsupported workflow fallback.
5. Add matrix coverage tests comparing `workflow_registry()` with supported interactive branch constants.

## 9. Implementation Recommendations

### P0

- Prevent `GOVERNANCE_ARTIFACT_CREATION` from falling through to unsupported fallback.
- Add explicit test proving the requested prompt either:
  - reaches `GOVERNED_DEVELOPMENT_WORKFLOW` with explanation and approval; or
  - reaches a dedicated governance artifact creation bridge with explanation and approval.
- Add fail-closed explanation rendering for unsupported selections.

### P1

- Decide whether `GOVERNED_REPOSITORY_MUTATION` remains internal under governed development or becomes directly operator-facing.
- If internal, route direct mutation prompts to governed development.
- If direct, add a conversational bridge.

### P2

- Extend human-friendly explanation to read-only, OCS, domain lifecycle, and clarification paths.
- Add a coverage matrix test that fails when registry entries are not categorized as one of:
  - interactive bridge;
  - lifecycle branch;
  - read-only/selection-only;
  - intentionally blocked.

## 10. Final Verdict

```text
CONVERSATIONAL_WORKFLOW_COVERAGE_AUDIT_COMPLETE
```
