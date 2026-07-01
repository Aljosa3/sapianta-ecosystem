# G8-06A ACLI Next Thin Entrypoint Architecture Review V1

Status: Platform Core responsibility leakage detected.

Final verdict: PLATFORM_CORE_RESPONSIBILITY_LEAKAGE_DETECTED

## 1. Executive Summary

This review evaluates whether ACLI Next remains a thin human entrypoint over certified Platform Core after the G8-03 through G8-06 runtime milestones.

Required invariant:

```text
Human
-> ACLI Next
-> PGSP
-> Platform Core
-> Replay
-> Human
```

Conclusion:

ACLI Next remains thin for bootstrap, interactive session transport, request capture, response rendering, confirmation capture, replay identifier presentation, and CLI routing.

However, G8-05 and G8-06 introduced responsibilities that are architecturally owned by Platform Core:

- read-only Worker capability resolution;
- Worker handoff authorization vocabulary;
- read-only Worker result summary construction;
- execution plan construction;
- mutation preview structure;
- risk classification;
- governance checkpoint synthesis;
- replay plan synthesis.

These are currently non-mutating and replay-visible, but they are not purely presentation, adapter, transport, or delegation behavior. They should be moved behind a Platform Core service boundary in the next implementation step.

No runtime mutation, provider orchestration, Worker write path, deployment, or Git operation was introduced.

## 2. Review Methodology

Reviewed implemented ACLI Next components:

| Component | Files Reviewed |
| --- | --- |
| Bootstrap | `aigol/acli_next/entrypoint.py` |
| Interactive runtime | `aigol/acli_next/interactive.py` |
| Read-only Worker handoff | `aigol/acli_next/readonly_worker.py` |
| Execution planning | `aigol/acli_next/execution_plan.py` |
| CLI routing | `aigol/cli/aigol_cli.py` |
| Package exports | `aigol/acli_next/__init__.py` |

Review criteria:

- ACLI Next may own terminal/UI interaction, session lifecycle, request transport, response rendering, confirmation capture, replay identifier presentation, and runtime delegation.
- ACLI Next must not own UBTR, CSA, OCS, Governance, Replay, Worker orchestration, Provider orchestration, execution planning logic, capability resolution, canonical mapping logic, conflict resolution, or policy evaluation.
- When ownership is unclear, ownership is assigned to Platform Core.

## 3. Ownership Matrix

| Responsibility | Current Location | Proper Owner | Assessment |
| --- | --- | --- | --- |
| CLI command parsing | `aigol/cli/aigol_cli.py` | ACLI Next / CLI adapter | Compliant |
| Human request capture | `entrypoint.py`, `interactive.py` | ACLI Next | Compliant |
| Human response capture | `entrypoint.py`, `interactive.py` | ACLI Next | Compliant |
| Session id and replay path transport | ACLI Next modules | ACLI Next | Compliant if limited to identifiers and paths |
| PGSP invocation | `entrypoint.py` delegates to G4 PGSP entrypoint | ACLI Next delegation to Platform Core | Compliant |
| Semantic translation | PGSP delegated runtime | Platform Core / UBTR | Compliant |
| CSA creation | PGSP delegated runtime | Platform Core / CSA | Compliant |
| OCS proposal/orchestration | PGSP delegated runtime | Platform Core / OCS | Compliant |
| Governance decisions | PGSP delegated runtime | Governance | Mostly compliant, but G8-05/G8-06 synthesize authorization labels |
| Replay reconstruction | Existing Replay runtime | Replay | Compliant; ACLI Next records append-only artifacts only |
| Worker capability lookup | `readonly_worker.py` allowlist | Platform Core | Leakage |
| Read-only Worker result generation | `readonly_worker.py` summary builders | Worker Platform / Platform Core | Leakage |
| Execution plan construction | `execution_plan.py` | Platform Core / OCS / Governance | Leakage |
| Mutation preview model | `execution_plan.py` | Platform Core / Governance | Leakage |
| Execution risk classification | `execution_plan.py` | Platform Core / Governance | Leakage |
| Governance checkpoint synthesis | `execution_plan.py` | Platform Core / Governance | Leakage |
| Canonical mapping summary | `readonly_worker.py` | Canonical Platform Knowledge / Platform Core | Leakage |
| Conflict resolution | Not implemented | Platform Core / Governance | Compliant |
| Provider orchestration | Not implemented | EPP / Platform Core | Compliant |
| Mutating Worker execution | Not implemented | Worker Platform / Governance | Compliant |

## 4. Responsibility Audit

### Bootstrap

`aigol/acli_next/entrypoint.py` is mostly compliant.

It:

- captures operator request and response;
- writes ACLI Next transport artifacts;
- delegates to `run_g4_live_acli_governed_development_session_entrypoint`;
- records PGSP references;
- renders a summary.

It does not translate, orchestrate, govern, reconstruct replay, invoke providers, invoke Workers, mutate repositories, or authorize execution.

Assessment: thin entrypoint.

### Interactive Runtime

`aigol/acli_next/interactive.py` is mostly compliant.

It:

- sequences turns;
- delegates every turn through `run_acli_next_session`;
- records turn replay references;
- stops continuation after terminal response classes.

Risk:

- `CONTINUABLE_RESPONSE_CLASSES` and `TERMINAL_RESPONSE_CLASSES` are simple adapter-side continuation gates, but future expansion could become policy evaluation.

Assessment: acceptable adapter behavior for MVP, with guardrail required.

### Read-only Worker Handoff

`aigol/acli_next/readonly_worker.py` is not fully thin.

Leakage:

- `SUPPORTED_READONLY_CAPABILITIES` performs capability resolution inside ACLI Next.
- `_governance_authorization_check` creates authorization vocabulary inside ACLI Next.
- `_readonly_worker_summary` constructs read-only Worker outputs.
- canonical mapping and validation summaries are generated locally.

Even though the behavior is read-only and non-mutating, these responsibilities belong to Platform Core:

- capability resolution belongs to canonical mappings / Platform Core;
- authorization belongs to Governance;
- Worker output belongs to Worker Platform or a certified read-only Worker runtime;
- canonical mapping lookup belongs to Canonical Platform Knowledge.

Assessment: Platform Core responsibility leakage.

Recommended refactoring:

- replace local capability allowlist with a Platform Core lookup call;
- replace local authorization artifact generation with Governance service output;
- replace local summary builders with Worker Platform read-only Worker runtimes;
- keep ACLI Next as request/response/replay-reference adapter only.

### Execution Planning

`aigol/acli_next/execution_plan.py` is not thin.

Leakage:

- default Worker sequence is selected in ACLI Next;
- default requested capabilities are selected in ACLI Next;
- execution plan model is constructed in ACLI Next;
- mutation preview model is constructed in ACLI Next;
- governance checkpoints are synthesized in ACLI Next;
- risk level is classified in ACLI Next;
- replay plan is synthesized in ACLI Next;
- advisory authorization vocabulary is created in ACLI Next.

These responsibilities belong to Platform Core:

- OCS should own execution proposal and plan formation;
- Governance should own checkpoint and admissibility vocabulary;
- Replay should define replay plan requirements;
- Worker Platform should own Worker sequence semantics;
- canonical mappings should own capability resolution.

Assessment: Platform Core responsibility leakage.

Recommended refactoring:

- move plan construction behind a Platform Core `execution_plan_preview` service;
- have ACLI Next submit confirmed session evidence and render returned plan;
- have OCS/Governance produce Worker sequence, capability list, risk summary, mutation preview, and replay plan;
- keep ACLI Next responsible only for transport, display, and replay reference presentation.

### CLI Routing

`aigol/cli/aigol_cli.py` remains mostly compliant.

It:

- registers routes;
- parses adapter arguments;
- invokes ACLI Next runtime functions;
- renders summaries.

Risk:

- CLI argument names such as `--worker-step`, `--capability`, and `--potential-impact` are acceptable as transport fields, but should not become policy selectors interpreted by ACLI Next long-term.

Assessment: adapter compliant if interpretation moves to Platform Core.

## 5. Dependency Analysis

| Module | Current Category | Allowed In ACLI Next? | Notes |
| --- | --- | --- | --- |
| `aigol/acli_next/__init__.py` | Presentation/export | Yes | Export-only surface. |
| `aigol/acli_next/entrypoint.py` | Adapter / transport / delegation | Yes | Delegates to existing PGSP runtime. |
| `aigol/acli_next/interactive.py` | Adapter / transport / delegation | Yes with guardrail | Continuation gate should remain minimal. |
| `aigol/acli_next/readonly_worker.py` | Orchestration / governance / capability logic | No | Must move behind Platform Core. |
| `aigol/acli_next/execution_plan.py` | Execution planning / governance / policy logic | No | Must move behind Platform Core. |
| `aigol/cli/aigol_cli.py` | Presentation / adapter | Yes | CLI must remain routing-only. |

Only presentation, adapter, transport, and delegation should exist inside ACLI Next.

Current non-compliant categories:

- orchestration-like logic;
- governance-like authorization labels;
- capability resolution;
- execution planning;
- policy/risk evaluation.

## 6. Thin-Entrypoint Compliance Review

| Required ACLI Next Ownership | Status | Evidence |
| --- | --- | --- |
| Terminal/UI interaction | Present | CLI routes and renderers. |
| Session lifecycle | Present | Session ids, turn sequencing, replay directories. |
| Request transport | Present | Operator request/response capture. |
| Response rendering | Present | Summary renderers. |
| Confirmation capture | Present | `operator_response` transport and canonical response class reference. |
| Replay identifier presentation | Present | Replay paths and hashes are surfaced. |
| Runtime delegation | Present | Bootstrap delegates to PGSP. |

| Forbidden ACLI Next Ownership | Status | Notes |
| --- | --- | --- |
| UBTR | Not owned | Delegated through PGSP. |
| CSA | Not owned | Delegated through PGSP. |
| OCS | Partially leaked | Execution plan construction resembles OCS planning. |
| Governance | Partially leaked | Authorization statuses and checkpoint lists are synthesized locally. |
| Replay | Mostly not owned | Replay artifact writing exists; replay reconstruction is not owned. |
| Worker orchestration | Partially leaked | Read-only Worker capability and result generation are local. |
| Provider orchestration | Not owned | No provider route. |
| Execution planning logic | Leaked | `execution_plan.py` constructs plans. |
| Capability resolution | Leaked | `SUPPORTED_READONLY_CAPABILITIES` and defaults. |
| Canonical mapping logic | Leaked | `canonical_mapping_lookup` local summary. |
| Conflict resolution | Not owned | No conflict engine introduced. |
| Policy evaluation | Leaked | risk and governance checkpoint logic in execution planning. |

## 7. Platform Core Boundary Review

No evidence was found that ACLI Next has introduced:

- UBTR replacement;
- CSA replacement;
- OCS replacement;
- Replay replacement;
- provider orchestration;
- mutating Worker execution;
- Git operation;
- deployment;
- repository mutation.

Evidence was found that ACLI Next has started absorbing Platform Core advisory logic:

- local Worker capability table;
- local governance authorization vocabulary;
- local execution plan schema and synthesis;
- local mutation preview schema and synthesis;
- local risk summary logic;
- local governance checkpoint construction.

This is early and bounded, but it should be corrected before mutating execution milestones begin.

## 8. Architectural Risks

| Risk | Severity | Description | Recommended Guardrail |
| --- | --- | --- | --- |
| ACLI Next becomes mini-OCS | High | Execution planning defaults and risk classification grow in adapter code. | Move plan generation to Platform Core service. |
| ACLI Next becomes mini-Governance | High | Authorization labels and checkpoint synthesis grow locally. | Require Governance-produced authorization artifacts. |
| ACLI Next becomes Worker registry | High | Capability allowlists become runtime registries. | Use canonical Platform Core capability lookup only. |
| ACLI Next becomes canonical mapping owner | Moderate | Local mapping summaries encode canonical response semantics. | Read mappings from canonical mapping projections. |
| Replay writing becomes Replay ownership | Moderate | Append-only artifacts are acceptable, but reconstruction logic must not move into ACLI Next. | Ban reconstruction functions in `aigol/acli_next/`. |
| Future web/mobile/REST adapters copy ACLI Next logic | High | Platform logic could fragment across interfaces. | Define universal adapter contract for all human interfaces. |

## 9. Recommended Refactoring

Refactoring is recommended before any mutating execution milestone.

Recommended target shape:

```text
Human
-> ACLI Next
-> PGSP
-> Platform Core execution-plan-preview service
-> Governance authorization artifact
-> Replay evidence
-> ACLI Next rendering
-> Human
```

Move from ACLI Next to Platform Core:

| Current ACLI Next Item | Move To |
| --- | --- |
| `SUPPORTED_READONLY_CAPABILITIES` | Canonical Platform Knowledge / capability projection lookup |
| `_governance_authorization_check` | Governance runtime/service |
| `_readonly_worker_summary` | Worker Platform read-only Worker runtimes |
| default Worker sequence | OCS / Worker Platform |
| default requested capabilities | OCS / canonical capability projection |
| execution plan artifact construction | OCS / Platform Core execution-plan-preview |
| mutation preview artifact construction | Governance / OCS preview service |
| `_governance_checkpoints` | Governance |
| `_risk_summary` | Governance / execution risk policy |
| `_replay_plan` | Replay contract provider |

Keep in ACLI Next:

- command parsing;
- prompt and response capture;
- session id generation or transport;
- replay path presentation;
- invocation of Platform Core services;
- rendering returned Platform Core summaries.

## 10. Recommended Guardrails

Required guardrails for future ACLI Next work:

1. ACLI Next modules may not define capability registries or allowlists except as temporary transport fixtures explicitly marked for removal.
2. ACLI Next modules may not define authorization statuses beyond adapter transport statuses.
3. ACLI Next modules may not synthesize governance checkpoints.
4. ACLI Next modules may not classify execution risk.
5. ACLI Next modules may not construct execution plans except by rendering Platform Core output.
6. ACLI Next modules may not construct mutation previews except by rendering Platform Core output.
7. ACLI Next modules may not reconstruct replay.
8. ACLI Next modules may not invoke providers directly.
9. ACLI Next modules may not dispatch Workers directly.
10. All future human interfaces, including Web, Mobile, REST, and Voice, must reuse the same Platform Core service boundaries rather than copying ACLI Next logic.

Recommended test guardrails:

- source tests asserting `aigol/acli_next/` does not contain provider invocation terms;
- source tests asserting `aigol/acli_next/` does not contain Worker dispatch functions;
- source tests asserting execution plan generation delegates to Platform Core once refactored;
- source tests asserting capability lookup does not live in ACLI Next once refactored;
- replay tests proving ACLI Next records references but does not reconstruct.

## 11. Transition Recommendation

Do not proceed to mutating execution implementation until G8-06A follow-up refactoring is complete.

Recommended next milestone:

```text
G8_06B_PLATFORM_CORE_EXECUTION_PLAN_PREVIEW_SERVICE_V1
```

Purpose:

- move execution plan and mutation preview generation into Platform Core;
- expose a PGSP-consumable execution-plan-preview service;
- return Governance and Replay-owned evidence to ACLI Next;
- reduce ACLI Next back to a thin adapter.

## 12. Final Determination

ACLI Next is still non-mutating and replay-visible, but it no longer remains purely thin after G8-05 and G8-06.

Platform Core responsibilities have begun to appear inside ACLI Next in bounded advisory form. This should be corrected before any mutating Worker, Git, deployment, provider, or execution authorization milestone.

## 13. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: PLATFORM_CORE_RESPONSIBILITY_LEAKAGE_DETECTED
