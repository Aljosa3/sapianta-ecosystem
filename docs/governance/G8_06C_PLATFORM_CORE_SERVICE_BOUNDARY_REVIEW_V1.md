# G8-06C Platform Core Service Boundary Review V1

Status: Platform Core internal refactoring required.

Final verdict: PLATFORM_CORE_INTERNAL_REFACTORING_REQUIRED

## 1. Executive Summary

G8-06C reviews the G8-06B Platform Core execution planning service:

```text
aigol/runtime/platform_core_execution_planning_service.py
```

The service successfully corrects the G8-06A thin-entrypoint issue by moving execution planning, mutation preview, read-only Worker handoff preview, capability lookup, risk summary, governance checkpoint synthesis, and replay planning out of ACLI Next.

ACLI Next now consumes the service as a thin adapter.

However, the service currently centralizes several Platform Core sub-responsibilities inside one module:

- advisory authorization evidence;
- governance checkpoint synthesis;
- execution risk classification;
- replay plan construction;
- read-only capability lookup;
- read-only Worker result summary construction.

Because those responsibilities belong to existing Platform Core authorities, the service should be refactored internally before mutating execution milestones begin. The concern is not that ACLI Next remains thick; that was corrected. The concern is that `platform_core_execution_planning_service` could become a second orchestration or policy layer if it continues to grow.

No repository mutation, Git operation, deployment, provider invocation, write-capable Worker path, replay reconstruction engine, or new external authority layer was introduced.

## 2. Service Responsibility Review

| Responsibility | Current Service Behavior | Proper Owner | Boundary Assessment |
| --- | --- | --- | --- |
| Adapter reuse | Accepts `command_name` and `runtime_version` from callers. | Platform Core service | Compliant |
| Confirmed session evidence check | Requires completed interactive session, confirmation, replay evidence, and non-mutation flags. | Platform Core / Governance | Acceptable guard, but should use Governance contract later |
| Read-only capability lookup | Uses `SUPPORTED_READONLY_CAPABILITIES`. | Canonical Platform Knowledge / Worker Platform | Internal refactoring required |
| Read-only Worker authorization evidence | Builds `AUTHORIZED_READONLY_WORKER`. | Governance | Internal refactoring required |
| Read-only Worker result summary | Builds replay, validation, and mapping summaries. | Worker Platform / Canonical Platform Knowledge | Internal refactoring required |
| Execution plan construction | Builds selected Worker sequence, capabilities, expected artifacts, and impact. | OCS / Worker Platform / Governance | Internal refactoring required |
| Governance checkpoint synthesis | Builds checkpoint list locally. | Governance | Internal refactoring required |
| Execution risk classification | Builds `LOW`/`MEDIUM` risk summary locally. | Governance / policy evaluation | Internal refactoring required |
| Mutation preview generation | Builds descriptive mutation preview. | OCS / Governance preview policy | Internal refactoring required |
| Replay plan construction | Builds planned replay artifacts locally. | Replay contract provider | Internal refactoring required |
| Replay artifact persistence | Writes append-only artifacts. | Runtime transport / Replay-visible persistence | Acceptable if reconstruction remains Replay-owned |

## 3. Ownership Matrix

| Platform Component | Expected Ownership | Current Interaction | Finding |
| --- | --- | --- | --- |
| PGSP | Session protocol and governed routing. | Service consumes an already-confirmed session result; it is not itself PGSP-routed. | Needs future PGSP contract exposure. |
| UBTR | Semantic translation. | Not invoked or duplicated. | Compliant |
| CSA | Canonical semantic representation. | Not invoked or duplicated. | Compliant |
| OCS | Proposal and execution plan formation. | Service constructs advisory execution plans directly. | Refactoring required |
| Governance | Certification, admissibility, checkpoints, risk policy. | Service constructs authorization labels, checkpoints, and risk summaries directly. | Refactoring required |
| Replay | Evidence reconstruction authority and replay contract. | Service writes append-only artifacts and constructs replay plans; it does not reconstruct. | Partial; replay plan should move to Replay contract |
| Worker Platform | Worker capability semantics and Worker result ownership. | Service owns read-only capability lookup and summary generation. | Refactoring required |
| EPP | Provider integration. | Not invoked. | Compliant |
| Human interfaces | Thin adapters. | ACLI Next consumes the service without owning planning logic. | Compliant |

## 4. Dependency Graph

Current G8-06B shape:

```text
ACLI Next / future interface
        |
        v
Platform Core execution planning service
        |
        +--> local capability lookup
        +--> local authorization labels
        +--> local governance checkpoint list
        +--> local risk summary
        +--> local mutation preview
        +--> local replay plan
        +--> append-only replay-visible artifacts
```

Recommended target shape:

```text
ACLI Next / Web / REST / Mobile / Voice
        |
        v
PGSP
        |
        v
Platform Core execution planning facade
        |
        +--> OCS plan preview
        +--> Governance checkpoint and risk policy
        +--> Canonical Platform Knowledge capability lookup
        +--> Worker Platform read-only summary provider
        +--> Replay contract provider
        |
        v
Replay-visible envelope returned to adapter
```

The current service is reusable by future interfaces, but it is not yet decomposed along certified Platform Core authority boundaries.

## 5. Reuse Analysis

Reuse preserved:

- ACLI Next no longer owns execution planning logic.
- The service accepts adapter-neutral `command_name` and `runtime_version` values.
- Tests prove a non-ACLI command name can consume the same service.
- Existing replay-visible behavior is preserved.
- Existing G8-03 through G8-06 tests remain valid.

Reuse incomplete:

- capability lookup is local, not sourced from canonical mappings;
- governance checkpoint and risk policy are local, not sourced from Governance;
- replay plan is local, not sourced from Replay;
- read-only Worker summary is local, not sourced from Worker Platform.

## 6. Duplication Analysis

| Possible Duplication | Present? | Notes |
| --- | --- | --- |
| UBTR duplication | No | No semantic translation logic exists in the service. |
| CSA duplication | No | No canonical semantic representation is created. |
| OCS duplication | Partial | Execution plan construction resembles OCS preview behavior. |
| Governance duplication | Partial | Authorization labels, checkpoint list, and risk summary are local. |
| Replay duplication | Partial | No reconstruction exists, but replay plan construction is local. |
| Worker Platform duplication | Partial | Read-only capability lookup and summary generation are local. |
| EPP duplication | No | No provider path exists. |
| Adapter duplication | No | Service is interface-neutral. |

The duplication is bounded and non-mutating, but it is real enough to require internal Platform Core refactoring before execution authority expands.

## 7. Architectural Risks

| Risk | Severity | Description | Mitigation |
| --- | --- | --- | --- |
| Service becomes mini-OCS | High | Plan construction grows into orchestration. | Move plan preview generation behind OCS-owned function. |
| Service becomes mini-Governance | High | Authorization labels and risk policy grow locally. | Move checkpoint/risk/admissibility generation to Governance-owned function. |
| Service becomes Worker registry | Moderate | `SUPPORTED_READONLY_CAPABILITIES` becomes a de facto registry. | Replace with canonical capability projection lookup. |
| Service becomes Replay policy owner | Moderate | Replay plan structure grows locally. | Source replay requirements from Replay contract provider. |
| Future interfaces bypass PGSP | Moderate | Service can be called directly by adapters. | Require PGSP route for production interface consumption. |
| Preview becomes execution | High | Future work may add mutating Worker calls to this service. | Prohibit provider, Worker dispatch, Git, deployment, and mutation in this module. |

## 8. Recommendations

Recommended next internal refactoring:

1. Introduce a Platform Core planning facade that delegates internally rather than owning all preview logic.
2. Move capability lookup to canonical capability projection or Worker Platform lookup.
3. Move authorization labels, checkpoints, and risk summary to Governance.
4. Move Worker read-only result summary generation to a certified read-only Worker runtime.
5. Move replay plan construction to a Replay contract helper.
6. Expose the facade through PGSP before Web, REST, Mobile, or Voice adapters consume it in production.
7. Keep current behavior as compatibility during the refactor, with no mutation path.

Suggested follow-up milestone:

```text
G8_06D_PLATFORM_CORE_EXECUTION_PLANNING_INTERNAL_DECOMPOSITION_V1
```

Purpose:

- preserve G8-06B external service contract;
- split internal responsibilities across OCS, Governance, Replay, Worker Platform, and canonical capability lookup;
- keep all human interfaces thin.

## 9. Future Guardrails

Required guardrails:

- `platform_core_execution_planning_service.py` must remain preview-only.
- It must not dispatch Workers.
- It must not invoke providers.
- It must not authorize execution.
- It must not create commits.
- It must not mutate repository contents.
- It must not deploy.
- It must not reconstruct replay.
- It must not become the only owner of planning policy.
- Future adapter tests must verify ACLI Next, Web, REST, Mobile, and Voice consume the same Platform Core facade.
- Source tests should prevent mutation, provider invocation, and Worker dispatch terms inside the preview service.

## 10. Final Determination

The G8-06B service is a reusable Platform Core capability and successfully restores ACLI Next to a thin adapter role.

The service boundary is not yet fully clean inside Platform Core. It centralizes preview logic that should be delegated to OCS, Governance, Replay, Worker Platform, and canonical capability lookup.

Therefore, internal Platform Core refactoring is required before extending toward mutating execution.

## 11. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: PLATFORM_CORE_INTERNAL_REFACTORING_REQUIRED
