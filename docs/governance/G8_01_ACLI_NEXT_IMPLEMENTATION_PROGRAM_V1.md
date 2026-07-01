# G8-01 ACLI Next Implementation Program V1

Status: ACLI Next implementation program approved.

Final verdict: ACLI_NEXT_IMPLEMENTATION_PROGRAM_APPROVED

## 1. Executive Summary

Generation 8 certified that Platform Core is ready to begin replacing the current manual ChatGPT -> Codex -> Terminal -> Git workflow with a Platform Core driven runtime centered around ACLI Next.

Certified input verdict:

```text
PLATFORM_RUNTIME_READY_FOR_ACLI_NEXT
```

This program defines how ACLI Next should become the canonical human entrypoint for governed development.

ACLI Next is not a new Platform Core. It is an entrypoint and orchestration consumer over the certified Platform Core:

```text
Human
-> ACLI Next
-> PGSP
-> UBTR
-> CSA
-> OCS
-> Governance
-> Replay
-> UHCL
-> Provider / Worker Services where certified and authorized
```

The implementation must proceed incrementally and preserve:

- PGSP as session protocol;
- UBTR as semantic translation authority;
- CSA as canonical semantic representation;
- OCS as orchestration and proposal owner;
- Governance as certification and admissibility authority;
- Replay as runtime evidence reconstruction authority;
- UHCL as reusable communication owner;
- EPP as external provider integration architecture;
- Worker Platform as Worker execution owner;
- interface adapters as capture and rendering surfaces only.

## 2. ACLI Next Purpose

ACLI Next exists to replace manual development workflow steps one at a time.

It should eliminate first:

- external prompt copying;
- manual session bootstrap;
- manual replay root selection;
- manual capability lookup where canonical records exist;
- manual status and evidence presentation.

It should defer:

- autonomous repository mutation;
- commit creation;
- deployment;
- unrestricted terminal command execution;
- Worker execution without authorization;
- provider execution outside EPP and PGSP boundaries.

ACLI Next must be:

- a primary governed human conversation entrypoint;
- a PGSP session starter and continuation surface;
- a UHCL renderer;
- a human confirmation capture surface;
- a replay-visible interaction event producer;
- a consumer of canonical evidence and conflict/fallback policy.

ACLI Next must not be:

- a translator;
- an OCS replacement;
- a governance engine;
- a replay engine;
- a provider layer;
- a Worker layer;
- an approval or authorization engine;
- a Git automation shortcut.

## 3. Legacy ACLI Reuse Review

Existing reusable surfaces:

| Existing Surface | Reuse Decision | Notes |
| --- | --- | --- |
| `aigol/cli/aigol_cli.py` | Partial reuse | Keep as legacy CLI and compatibility dispatcher; avoid making it the long-term ACLI Next core. |
| `aigol/cli/commands/*` | Reuse selectively | Existing command modules remain useful for compatibility, diagnostics, replay, approval, and execution inspection. |
| `aigol/cli/render/*` | Reuse selectively | Terminal rendering helpers can be reused when they render UHCL/Platform evidence without creating reusable communication. |
| `aigol/runtime/g4_live_acli_governed_development_session_entrypoint.py` | Reuse as lineage/reference | Proves live ACLI entrypoint into PGSP lineage; not the final ACLI Next runtime. |
| `aigol/runtime/conversational_cli_runtime.py` | Reuse as routing evidence | Existing conversational routing is valuable but should not own ACLI Next session protocol. |
| `aigol/runtime/acli_uhcl_adapter_rendering.py` | Reuse | Supports adapter rendering boundary. |
| `aigol/runtime/acli_development_session_lifecycle.py` | Reuse/inspect | Useful lifecycle evidence for ACLI Next session model. |
| `aigol/runtime/acli_governed_development_execution_bridge.py` | Reuse cautiously | Existing bridge evidence can inform proposal/approval continuity, but ACLI Next must route through PGSP and Governance. |
| `aigol/runtime/operator/*` | Reuse selectively | Operator summaries and runtime query surfaces may support ACLI Next visibility. |
| Replay command and inspection modules | Reuse | Replay inspection should remain separate from Replay authority. |

What should be replaced:

- monolithic command registration as the primary interaction model;
- freeform conversational routing that returns human suggestions without executable continuation where a certified continuation exists;
- implicit approval through prompt wording;
- operator-visible summaries that are not tied to replay-visible ACLI Next session state.

Legacy ACLI should live beside ACLI Next during transition.

## 4. Proposed Module And Location Structure

Recommended package:

```text
aigol/acli_next/
```

Recommended modules:

| Module | Purpose |
| --- | --- |
| `aigol/acli_next/__init__.py` | Package marker and exported entrypoint names. |
| `aigol/acli_next/entrypoint.py` | Primary ACLI Next session command entrypoint. |
| `aigol/acli_next/session.py` | Session request, response, state, and continuation models. |
| `aigol/acli_next/pgsp_client.py` | Thin PGSP invocation adapter; no PGSP ownership. |
| `aigol/acli_next/replay_events.py` | ACLI Next interaction event records and replay references. |
| `aigol/acli_next/rendering.py` | UHCL rendering adapter and terminal display binding. |
| `aigol/acli_next/confirmation.py` | Human confirmation capture model. |
| `aigol/acli_next/canonical_lookup.py` | Consumer of canonical projection lookup contract once certified. |
| `aigol/acli_next/migration.py` | Legacy ACLI compatibility and migration helpers. |

Recommended CLI integration:

```text
python -m aigol.cli.aigol_cli next session
```

or:

```text
aigol next session
```

The CLI shim should call ACLI Next. It should not implement ACLI Next logic inside the legacy monolith.

## 5. MVP Workflow

ACLI Next MVP should be non-mutating and replay-visible.

MVP flow:

1. Human enters a natural-language development request.
2. ACLI Next creates a session id and turn id.
3. ACLI Next records input capture evidence.
4. ACLI Next invokes PGSP.
5. PGSP routes through UBTR, CSA, OCS, Governance, UHCL, and Replay.
6. ACLI Next renders UHCL output.
7. Human confirms, rejects, modifies, or asks a clarification.
8. ACLI Next records confirmation evidence.
9. ACLI Next emits replay-visible session summary.
10. No repository mutation occurs.
11. No Worker execution occurs unless explicitly certified in a later phase.
12. No provider execution occurs except through a certified read-only provider cognition path in later phase.

MVP eliminates:

- external prompt copying;
- manual session bootstrap;
- manual summary composition;
- manual replay root decision;
- manual indication of advisory-only non-execution state.

MVP defers:

- file edits;
- terminal command execution;
- Git commits;
- deployment;
- autonomous provider/Worker invocation.

## 6. Command And Session Model

Recommended command family:

| Command | Purpose |
| --- | --- |
| `aigol next session` | Start an ACLI Next governed development session. |
| `aigol next resume --session-id ...` | Resume a prior ACLI Next session. |
| `aigol next continue --session-id ...` | Continue from pending confirmation or clarification. |
| `aigol next status --session-id ...` | Show session state from replay-visible evidence. |
| `aigol next replay --session-id ...` | Inspect replay references for the session. |
| `aigol next explain --session-id ...` | Render UHCL explanation for current state. |

Canonical session fields:

- `session_id`;
- `turn_id`;
- `created_at`;
- `workspace`;
- `operator_request`;
- `operator_response`;
- `adapter_id`;
- `adapter_version`;
- `pgsp_session_reference`;
- `replay_root`;
- `replay_reference`;
- `governance_checkpoint_references`;
- `uhcl_rendering_reference`;
- `confirmation_state`;
- `execution_state`.

Execution state values for MVP:

- `advisory_only`;
- `non_mutating`;
- `provider_not_invoked`;
- `worker_not_invoked`;
- `approval_not_created`;
- `authorization_not_created`;
- `deployment_not_performed`.

## 7. Platform Core Integration Points

| Platform Core Component | ACLI Next Integration | Boundary |
| --- | --- | --- |
| PGSP | Start, continue, and inspect governed sessions. | ACLI Next calls PGSP; PGSP owns session protocol. |
| UBTR | Receives human language through PGSP path. | ACLI Next never translates. |
| CSA | Receives canonical semantic artifacts through Platform Core. | ACLI Next never creates CSA directly. |
| OCS | Produces proposals and advisory execution intent. | ACLI Next renders and captures response only. |
| Governance | Evaluates checkpoints and admissibility. | ACLI Next records and displays governance evidence. |
| Replay | Records/reconstructs runtime evidence. | ACLI Next emits adapter events; Replay remains authority. |
| UHCL | Produces reusable human communication. | ACLI Next renders UHCL. |
| EPP | Provides certified provider integration paths. | ACLI Next does not select or invoke providers by authority. |
| Worker Platform | Executes only through certified authorization and handoff. | ACLI Next does not bypass Worker boundaries. |
| Canonical records | Supply source, mapping, status, conflict, and fallback evidence. | ACLI Next consumes, never certifies. |

## 8. Human Confirmation Flow

ACLI Next confirmation states:

| State | Meaning |
| --- | --- |
| `presented` | UHCL output has been rendered to the human. |
| `clarification_requested` | Human or Governance requires clarification. |
| `confirmed_advisory` | Human confirms advisory plan or next non-mutating step. |
| `modification_requested` | Human requests a change to the proposal. |
| `rejected` | Human rejects the proposal or next step. |
| `execution_approval_required` | Future state for execution-capable phases only. |
| `authorization_required` | Future state for Worker execution only. |

MVP confirmation must not create execution authorization.

## 9. Provider Invocation Boundaries

Provider usage in ACLI Next must remain bounded:

- read-only cognition only until further certification;
- provider identity must remain separate from Worker identity;
- EPP owns provider integration;
- PGSP/OCS/Governance decide whether provider cognition may be used;
- UHCL renders provider evidence summaries;
- Replay records provider participation evidence.

ACLI Next may request provider cognition only after a certified PGSP/EPP integration milestone.

ACLI Next must not:

- directly call provider APIs;
- store provider credentials;
- select providers authoritatively;
- treat provider output as decision authority.

## 10. Worker Execution Boundaries

Worker execution is deferred beyond MVP.

Worker execution requires:

- explicit human approval where required;
- execution authorization artifact;
- Worker handoff package;
- Worker identity validation;
- replay-visible dispatch and invocation;
- result capture;
- post-execution review.

ACLI Next may eventually initiate Worker-bound requests, but only by consuming certified PGSP/OCS/Governance/Authorization/Worker paths.

ACLI Next must not:

- execute terminal commands directly;
- mutate repository files outside Worker authorization;
- create commits directly;
- deploy software;
- bypass post-execution review.

## 11. Replay Requirements

ACLI Next must produce replay-visible evidence for:

- session creation;
- turn creation;
- human request capture;
- PGSP invocation reference;
- canonical lookup reference where used;
- UHCL rendering reference;
- human confirmation or rejection;
- governance checkpoint references;
- non-execution state;
- continuation or suspension state;
- error and fail-closed state.

Replay requirements:

- replay artifacts must be deterministic;
- replay references must be included in ACLI Next output;
- missing replay must fail closed;
- runtime-produced canonical records must be hash-bound where introduced;
- documentation-only references must not be treated as runtime replay.

## 12. Governance Checkpoints

Required governance checkpoints:

| Checkpoint | Requirement |
| --- | --- |
| Adapter boundary | ACLI Next captures and renders only. |
| Translation boundary | UBTR remains translation owner. |
| Orchestration boundary | OCS remains proposal owner. |
| Communication boundary | UHCL remains reusable communication owner. |
| Replay boundary | Replay remains reconstruction authority. |
| Provider boundary | EPP/provider services own provider integration. |
| Worker boundary | Worker Platform owns execution. |
| Human confirmation | Confirmation is replay-visible and does not imply authorization. |
| Non-mutation MVP | MVP performs no repository mutation. |
| Conflict/fallback | G7-04 policy governs missing, stale, partial, or conflicting evidence. |

## 13. Migration Strategy From Legacy ACLI

Migration phases:

1. Keep legacy `aigol conversation`, `aigol g4-live-session`, replay, governance, approval, provider, and diagnostic commands intact.
2. Add `aigol next ...` as a new namespace.
3. Implement ACLI Next in `aigol/acli_next/` rather than expanding the monolithic CLI.
4. Reuse rendering helpers and selected command modules where they preserve boundaries.
5. Route new governed development sessions through ACLI Next.
6. Keep legacy commands available for inspection, diagnostics, and compatibility.
7. Add migration notices only after ACLI Next MVP is validated.
8. Retire legacy entrypoints only through a future certification review.

Compatibility that must remain:

- existing replay artifacts;
- existing command-line diagnostics;
- existing governance and replay commands;
- existing provider credential safety boundaries;
- existing Worker execution boundaries;
- existing PGSP public API contract.

## 14. Implementation Phases

### Phase 0: Contract And Skeleton

Deliver:

- ACLI Next entrypoint contract;
- module skeleton;
- no runtime mutation;
- no provider or Worker invocation.

Validation:

- `git diff --check`;
- `python -m py_compile` for new modules if code is added.

### Phase 1: Non-Mutating Session MVP

Deliver:

- `aigol next session`;
- PGSP invocation;
- replay-visible session events;
- UHCL rendering;
- human confirmation capture;
- advisory-only output.

Validation:

- targeted ACLI Next MVP tests;
- replay reconstruction test;
- `git diff --check`;
- full pytest only if shared runtime behavior changes.

### Phase 2: Canonical Lookup Consumption

Deliver:

- PGSP projection lookup contract consumption;
- G7 source/mapping/conflict references in session evidence;
- fallback routing for missing/stale/conflicting evidence.

Validation:

- targeted lookup contract tests;
- conflict/fallback scenario tests.

### Phase 3: Provider Cognition Adoption

Deliver:

- bounded read-only provider cognition review through certified EPP/PGSP path;
- UHCL provider summary rendering;
- replay-visible provider participation evidence.

Validation:

- provider cognition boundary tests;
- credential non-leakage checks where applicable.

### Phase 4: Worker Readiness Gate

Deliver:

- Worker execution readiness review from ACLI Next;
- no direct terminal execution;
- no Git mutation;
- authorization prerequisite enforcement.

Validation:

- Worker boundary tests;
- fail-closed authorization tests if code is added.

### Phase 5: Certification Review

Deliver:

- ACLI Next MVP certification review;
- authority review;
- replay review;
- migration impact review.

## 15. Validation Strategy

Documentation-only packages:

```text
git diff --check
```

Code packages:

```text
git diff --check
python -m py_compile <changed python modules>
python -m pytest tests/<targeted_acli_next_tests>.py
```

Broader validation:

- full pytest only when shared runtime behavior changes;
- replay artifact cleanup after runtime tests;
- explicit report of generated `.runtime` or replay artifacts.

## 16. Manual Workflow Steps Eliminated In Phase 1

Phase 1 should eliminate:

- composing a prompt outside Platform Core for session bootstrap;
- copying the prompt into a separate tool;
- manually choosing a replay root;
- manually summarizing non-execution state;
- manually recording human confirmation for advisory plans.

Phase 1 should reduce but not eliminate:

- manual validation selection;
- manual capability lookup;
- manual provider choice.

## 17. Manual Workflow Steps Deferred

Deferred intentionally:

- repository mutation;
- file edits;
- terminal command execution;
- Git commit creation;
- deployment;
- autonomous retry/fallback;
- direct provider execution outside EPP;
- Worker execution without authorization.

These require later certification and must not be smuggled into ACLI Next MVP.

## 18. Final Determination

ACLI Next implementation program is approved.

ACLI Next should be implemented as a side-by-side canonical human entrypoint over certified Platform Core, reusing legacy ACLI and CLI surfaces where safe while preserving all Platform Core ownership boundaries.

## 19. Validation Evidence

Validation performed:

```text
git diff --check
```

Validation result: clean.

Final verdict: ACLI_NEXT_IMPLEMENTATION_PROGRAM_APPROVED
