# G31-R01 Generation 31 Retrospective Reuse and Minimality Audit

Status: completed retrospective audit; documentation only.

Date: 2026-07-16

Primary verdict:

`G31_BINDINGS_ACCEPTED_WITH_CONSOLIDATION_OBSERVATIONS`

Readiness verdict:

`READY_FOR_G31_11B_WITH_DEFERRED_CONSOLIDATION`

## 1. Audit scope and constitutional baseline

This audit treats Generation 30 and committed G31-01 through G31-11A as
accepted baselines. It does not reopen Platform Core, G24, G28, G29, G30,
Governance, Replay, Certification, Repository Cognition, Worker, Provider,
Human Conversation Experience, Canonical Presentation, or Human Interface
authority.

The production commits audited directly against their parents are:

| Generation | Commit | Transition |
|---|---|---|
| G31-04 | `01e6239ef0caa2a2a2c0bfe90156e8b4ce6881dd` | implementation turn to Durable Governed Work and proposal approval |
| G31-05 | `7dc327b08e8dcb2a70355c25c7b6d829f91af999` | approved work to goal-faithful Worker payload |
| G31-06 | `c04e811addae64d6131cf31b735d9b174fd85cbf` | unresolved payload to repository-scope grounding |
| G31-08 | `d18b0efde4e4e51da4d27ff30b214f844ab4bd19` | grounded request to execution-authorization review |
| G31-09 | `14f1f6167692196159ee404ca6fe260b31ffe937` | distinct human execution decision |
| G31-10 | `e5e8fa87db6fc13d5090ee9a1dce57c14d955cdf` | confirmed decision to existing execution authorization |

G31-07 is retained as an immutable documentation-only acceptance audit with
verdict `G31_06_MINIMALITY_ACCEPTED_WITH_OBSERVATIONS`. G31-11A is retained as
the documentation-only Worker-selection reuse audit with verdict
`EXISTING_CERTIFIED_WORKER_SELECTION_REUSABLE_BOUNDED_PROJECTION_REQUIRED`.

No runtime, CLI, test, schema, registry, artifact, policy, or Replay behavior
was changed by G31-R01. The only repository change is this report.

## 2. Method and classification vocabulary

The audit used committed parent diffs, current production source, accepted
governance reports, symbol searches, callers, validators, reconstructors,
focused tests, and checked-in certification evidence. Raw line count is
supporting evidence; responsibility ownership, immutable lineage, fail-closed
behavior, and availability of an equivalent public contract determine the
classification.

Every G31 production symbol below is assigned exactly one of the required
classifications:

- `ESSENTIAL_BINDING`;
- `ESSENTIAL_PROJECTION`;
- `ESSENTIAL_VALIDATION`;
- `ESSENTIAL_REPLAY`;
- `ESSENTIAL_PRESENTATION`;
- `JUSTIFIED_LOCAL_HELPER`;
- `DUPLICATE_HELPER_OBSERVATION`;
- `EXISTING_PUBLIC_FUNCTION_UNDERUSED`;
- `REDUNDANT_PROJECTION`;
- `DUPLICATE_RESPONSIBILITY`.

No introduced production symbol is classified `REDUNDANT_PROJECTION` or
`DUPLICATE_RESPONSIBILITY`. The existing public transport function
`verify_replay_hash` is classified `EXISTING_PUBLIC_FUNCTION_UNDERUSED` by
G31-04 through G31-06. The affected local hash helpers are separately
classified `DUPLICATE_HELPER_OBSERVATION`.

## 3. Exact per-generation change accounting

Counts are direct `git show --numstat` totals. Production includes `aigol/`
runtime and CLI files. Tests and documentation are counted separately.

| Generation | Production + / - | Tests + / - | Docs + / - | New / modified production modules | New public / private functions |
|---|---:|---:|---:|---:|---:|
| G31-04 | 1,064 / 19 | 390 / 0 | 671 / 0 | 1 / 3 | 7 / 13 |
| G31-05 | 1,039 / 13 | 534 / 31 | 534 / 0 | 1 / 5 | 4 / 15 |
| G31-06 | 957 / 4 | 565 / 2 | 514 / 0 | 1 / 4 | 6 / 17 |
| G31-08 | 757 / 3 | 559 / 2 | 599 / 0 | 1 / 3 | 4 / 10 |
| G31-09 | 492 / 3 | 507 / 0 | 693 / 0 | 1 / 3 | 4 / 7 |
| G31-10 | 339 / 7 | 272 / 2 | 394 / 0 | 1 / 2 | 2 / 0 |
| **Total** | **4,648 / 49** | **2,827 / 37** | **3,405 / 0** | **6 / 20 generation-local modifications** | **27 / 62** |

The six new production modules contain 3,439 current lines. The larger
production total includes the required existing-owner projections into
Project Services, operational composition, Human Interface transport,
Canonical Presentation, Worker-request validation, and execution
authorization. The G31-06 follow-up commit `24b5d908` removes one test-only
blank line and changes no production accounting.

## 4. Transition-by-transition responsibility map

| Transition | Exact production files | Existing capabilities reused | New bounded responsibility | Stop boundary |
|---|---|---|---|---|
| G31-04 | `platform_implementation_turn_durable_work_binding.py`; bounded changes in `platform_core_project_services.py`, `human_interface_runtime_entry_service.py`, `aicli.py` | Project Objective, Platform Knowledge, capability coverage, development plan, Durable Governed Work, approval request, Human Conversation Experience, immutable transport | Bind one implementation turn, source identities, preview, and approval consumption | approval is consumed; no execution authorization or Worker stage |
| G31-05 | `approved_durable_work_worker_payload_binding.py`; bounded changes in governed request and Worker-request bridges, operational CLI, Human Interface | G31-04 artifacts, PPP candidate, governed implementation request, `WORKER_REQUEST_ARTIFACT_V1`, native reconstructors | Project approved source fields into existing non-executing task/request/payload families and one lineage root | unresolved repository scope; no authorization, selection, dispatch, invocation, or mutation |
| G31-06 | `approved_durable_work_repository_scope_grounding.py`; Worker-request scope projection and bounded presentation wiring | G31-05, `detect_capabilities`, existing source/test association, existing mutation-layer classification, Worker-request validator | Bind exact existing paths, content hashes, symbols, tests, layers, and cognition snapshot; project only unresolved scope fields | no execution authorization or Worker selection |
| G31-08 | `grounded_worker_request_execution_authorization_binding.py`; bounded operational and presentation wiring | G31-06 validation/reconstruction, Worker-request validation, existing execution-summary contract, public hash transport | Bind exact grounded scope to an existing pending execution summary and distinct review checkpoint | pending distinct human decision; no authorization artifact or Worker selection |
| G31-09 | `grounded_execution_authorization_human_decision_binding.py`; contextual command transport and projection | G31-08, existing execution-summary human confirmation, session state, immutable transport | Record exactly one contextual approve/reject result with full lineage and explicit rejection evidence | second decision recorded; no execution authorization or Worker selection |
| G31-10 | `confirmed_grounded_execution_authorization_binding.py`; bounded execution-authorization compatibility projection and AiCLI continuation | G31-09, existing execution-ready packet/validation/ready artifacts, `authorize_execution_ready`, native authorization reconstruction | Project confirmed grounded evidence into existing artifact families and call the existing authorization owner without a third confirmation | execution authorized; no Worker selection, assignment, dispatch, invocation, command, or mutation |

The transitions are adjacent lineage bindings. They do not form competing
planners, selectors, approval engines, authorization engines, Repository
Cognition systems, Worker runtimes, or Replay subsystems.

## 5. New canonical artifact-family audit

| Generation | New family | Why the existing family was insufficient | Finding |
|---|---|---|---|
| G31-04 | `PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_ARTIFACT_V1` | Existing coverage, plan, and Durable Governed Work artifacts did not bind the original turn, all nested identities, repository-context state, and approval boundary into one reconstructable transition | Necessary lineage binding; not a second planner or Durable Work artifact |
| G31-04 | `PLATFORM_IMPLEMENTATION_TURN_PROPOSAL_PREVIEW_ARTIFACT_V1` | The existing approval request lacked the complete source-backed, user-presentable projection and explicit unresolved-scope statement | Necessary presentation projection; no new semantic decision |
| G31-04 | `PLATFORM_IMPLEMENTATION_TURN_APPROVAL_CONSUMPTION_ARTIFACT_V1` | A textual `/approve` did not itself prove which four immutable proposal identities were consumed | Necessary approval-continuity evidence; not execution authorization |
| G31-05 | `APPROVED_DURABLE_WORK_WORKER_PAYLOAD_BINDING_ARTIFACT_V1` | Existing PPP, implementation-request, and Worker-request Replays had no common approved-work lineage root or field-source map | Necessary composition binding; the native artifact families remain unchanged |
| G31-06 | `CANONICAL_REPOSITORY_SCOPE_GROUNDING_ARTIFACT_V1` | The unresolved Worker request could not carry cognition snapshot identity, exact target/symbol evidence, mutation layers, freshness, and complete upstream lineage without changing its responsibility | Necessary evidence binding, as accepted by G31-07 |
| G31-08 | `GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1` | The pending execution summary could carry scope but not the complete G31 grounding lineage, failed observation state, or proof that no human confirmation/authorization existed | Necessary review binding; not a new authorization request or decision |
| G31-09 | `GROUNDED_EXECUTION_AUTHORIZATION_HUMAN_DECISION_RESULT_ARTIFACT_V1` | Existing confirmation represented approval only and did not represent explicit rejection, session consumption, or complete G31-08 lineage | Necessary two-decision result binding; not a second approval system |
| G31-10 | **None** | Existing execution-ready and execution-authorization artifact families were sufficient after a bounded projection | Strongest reuse result; no parallel canonical family |

Each introduced family has one owner, one validator, one reconstructable
lineage role, and a distinct upstream/downstream edge. Nested artifact copies
are immutable evidence snapshots, not replacement authorities.

## 6. G31-04 symbol classification

File: `aigol/runtime/platform_implementation_turn_durable_work_binding.py`.
Current spans are exact inclusive source spans.

| Symbol(s) | Span | Responsibility | Classification |
|---|---:|---|---|
| `PLATFORM_IMPLEMENTATION_TURN_DURABLE_WORK_BINDING_VERSION`; three artifact-family constants; three status constants | 35–54 | Version, artifact, and status vocabulary for the one transition | `ESSENTIAL_BINDING` |
| `BOUNDARY_FLAGS` | 56–70 | Explicit stop and non-authority assertions | `ESSENTIAL_VALIDATION` |
| `compose_implementation_turn_durable_work_binding` | 73–207 | Coordinate existing coverage, plan, Durable Work, preview, and persistence | `ESSENTIAL_BINDING` |
| `validate_implementation_turn_durable_work_binding` | 210–294 | Validate complete nested identity continuity | `ESSENTIAL_VALIDATION` |
| `validate_implementation_turn_proposal_preview` | 297–319 | Validate the preview artifact and hash | `ESSENTIAL_VALIDATION` |
| `consume_approved_implementation_turn_binding` | 322–384 | Bind exact pending approval identities to canonical continuation | `ESSENTIAL_BINDING` |
| `validate_implementation_turn_approval_consumption` | 387–414 | Validate approval-consumption identity and boundaries | `ESSENTIAL_VALIDATION` |
| `reconstruct_implementation_turn_durable_work_binding`; `reconstruct_implementation_turn_approval_consumption` | 417–430 | Reconstruct ordered wrappers and nested artifacts | `ESSENTIAL_REPLAY` |
| `_proposal_preview`; `_repository_context` | 433–522 | Project source-backed proposal and repository context | `ESSENTIAL_PROJECTION` |
| `_bounded_project_capability_gap_evidence` | 525–539 | Require prior bounded gap evidence before projection | `ESSENTIAL_VALIDATION` |
| `_project_capability_gap_coverage_projection`; `_project_required_extension_gap` | 542–666 | Adapt an already-decided gap into the existing coverage contract | `ESSENTIAL_PROJECTION` |
| `_failure_reason` | 669–678 | Project a truthful fail-closed explanation | `ESSENTIAL_PRESENTATION` |
| `_validate_preview_lineage` | 681–696 | Compare preview source identities | `ESSENTIAL_VALIDATION` |
| `_validate_hash_bound_snapshot` | 699–709 | Validate a hash-bound snapshot with local hash logic | `DUPLICATE_HELPER_OBSERVATION` |
| `_snapshot_hash` | 712–714 | Hash an object excluding its hash field | `JUSTIFIED_LOCAL_HELPER` |
| `_persist_binding`; `_persist_consumption`; `_validate_wrapper` | 717–745 | Persist and validate transition-specific ordered wrappers | `ESSENTIAL_REPLAY` |
| `_require_string` | 748–751 | Local non-empty string boundary | `DUPLICATE_HELPER_OBSERVATION` |
| `__all__` | 754–769 | Declare the intended public transition surface | `JUSTIFIED_LOCAL_HELPER` |

Modified existing symbols are also necessary: Project Services
`prepare_unified_human_interface_project_context` is `ESSENTIAL_BINDING` and
`_conversation_approval_summary` is `ESSENTIAL_PRESENTATION`;
`run_human_interface_runtime_entry` is `ESSENTIAL_PROJECTION`; AiCLI
`run_reference_uhi_session` and `run_reference_uhi_submit_session` are
`ESSENTIAL_BINDING`, while `_render_summary` is `ESSENTIAL_PRESENTATION`.

## 7. G31-05 symbol classification

File: `aigol/runtime/approved_durable_work_worker_payload_binding.py`.

| Symbol(s) | Span | Responsibility | Classification |
|---|---:|---|---|
| version, artifact, PPP source/certification, and two status constants | 36–49 | Define the one composition binding vocabulary | `ESSENTIAL_BINDING` |
| `REPLAY_STEPS` | 51–54 | Define ordered composition wrappers | `ESSENTIAL_REPLAY` |
| `FALSE_BOUNDARIES` | 56–74 | Assert no authorization, execution, Worker, Provider, mutation, or HI authority | `ESSENTIAL_VALIDATION` |
| `bind_approved_durable_work_to_worker_payload` | 77–199 | Coordinate G31-04 validation and existing PPP/request bridges | `ESSENTIAL_BINDING` |
| `validate_approved_durable_work_worker_payload_binding` | 202–339 | Validate native artifacts, scope, field lineage, and boundaries | `ESSENTIAL_VALIDATION` |
| `reconstruct_approved_durable_work_worker_payload_binding` | 342–392 | Reconstruct native and G31 wrapper Replays | `ESSENTIAL_REPLAY` |
| `render_approved_durable_work_worker_payload_binding` | 395–422 | Render canonical payload and stop state | `ESSENTIAL_PRESENTATION` |
| `_implementation_scope`; `_field_lineage`; `_source` | 425–509 | Project approved fields and their exact sources | `ESSENTIAL_PROJECTION` |
| `_ppp_task_package`; `_implementation_request_approval` | 512–628 | Adapt approved work into existing PPP and non-executing approval families | `ESSENTIAL_PROJECTION` |
| `_validate_ppp_task_package`; `_validate_approval_continuity`; `_repository_scope_unresolved` | 631–688 | Validate package, approval identity, and unresolved scope | `ESSENTIAL_VALIDATION` |
| `_validate_hash` | 691–699 | Locally verify an artifact hash | `DUPLICATE_HELPER_OBSERVATION` |
| `_ensure_replay_available` | 702–705 | Preflight a two-file append-only Replay | `DUPLICATE_HELPER_OBSERVATION` |
| `_persist_step`; `_validate_wrapper` | 708–724 | Create and validate artifact-specific ordered wrappers | `ESSENTIAL_REPLAY` |
| `_require_string` | 727–730 | Local non-empty string boundary | `DUPLICATE_HELPER_OBSERVATION` |

New operational helpers `_approved_durable_work_worker_payload_binding_active`
and `_interactive_approved_durable_work_worker_payload_turn_summary` are
respectively `ESSENTIAL_VALIDATION` and `ESSENTIAL_PRESENTATION`. Existing
symbols changed in `governed_implementation_request_runtime.py` are
`_validate_ppp_candidate` (`ESSENTIAL_VALIDATION`) and
`_implementation_request_artifact`, `_failed_implementation_request_artifact`,
and `_scope` (`ESSENTIAL_PROJECTION`). Existing Worker-bridge symbols
`_validate_implementation_request` are `ESSENTIAL_VALIDATION`, while
`_worker_request_artifact` and `_failed_worker_request_artifact` are
`ESSENTIAL_PROJECTION`. Operational composition is `ESSENTIAL_BINDING`; Human
Interface transport is `ESSENTIAL_PROJECTION`; terminal summary/render changes
are `ESSENTIAL_PRESENTATION`.

## 8. G31-06 symbol classification and G31-07 continuity

File: `aigol/runtime/approved_durable_work_repository_scope_grounding.py`.
This table preserves the substance of the accepted G31-07 audit while using
the G31-R01 classification vocabulary.

| Symbol(s) | Span | Responsibility | Classification |
|---|---:|---|---|
| version, artifact, and two status constants | 29–38 | Define one grounding transition | `ESSENTIAL_BINDING` |
| `REPLAY_STEPS` | 39–42 | Define ordered grounding wrappers | `ESSENTIAL_REPLAY` |
| `FALSE_BOUNDARIES` | 44–61 | Assert the pre-authorization stop | `ESSENTIAL_VALIDATION` |
| `ground_approved_durable_work_repository_scope` | 64–176 | Bind one exact capability-audit match and project the Worker request | `ESSENTIAL_BINDING` |
| `validate_approved_durable_work_repository_scope_grounding` | 179–295 | Validate upstream identities, targets, freshness, projection, and boundaries | `ESSENTIAL_VALIDATION` |
| `reconstruct_approved_durable_work_repository_scope_grounding` | 298–326 | Reconstruct ordered and nested Replay | `ESSENTIAL_REPLAY` |
| `render_approved_durable_work_repository_scope_grounding` | 329–350 | Render scope, evidence, ambiguity, and stop state | `ESSENTIAL_PRESENTATION` |
| `_grounding_artifact` | 353–441 | Materialize the immutable cognition and lineage evidence object | `ESSENTIAL_BINDING` |
| `_required_capability_key`; `_target_evidence` | 444–469 | Adapt only already-decided capability and path evidence | `ESSENTIAL_PROJECTION` |
| `_observe_target` | 472–532 | Observe content hash, symbols, location, and existing layer for selected paths | `ESSENTIAL_BINDING` |
| `_validate_target_evidence`; `_repository_cognition_snapshot_hash`; `_validate_projection_continuity` | 535–636 | Validate freshness, snapshot identity, and unchanged Worker fields | `ESSENTIAL_VALIDATION` |
| `_workspace_root`; `_existing_workspace_root` | 639–650 | Enforce current workspace and Git preconditions | `ESSENTIAL_VALIDATION` |
| `_relative_path` | 653–658 | Normalize a repository-relative path locally | `DUPLICATE_HELPER_OBSERVATION` |
| `_verify_hash` | 661–665 | Reimplement public artifact-hash verification | `DUPLICATE_HELPER_OBSERVATION` |
| `_ensure_replay_available` | 668–671 | Preflight a two-file Replay | `DUPLICATE_HELPER_OBSERVATION` |
| `_persist_step`; `_validate_wrapper` | 674–690 | Persist and validate transition-specific ordering | `ESSENTIAL_REPLAY` |
| `_require_string` | 693–696 | Local non-empty string boundary | `DUPLICATE_HELPER_OBSERVATION` |

The existing Worker bridge additions are independently justified:
`project_worker_request_repository_scope` is `ESSENTIAL_PROJECTION`,
`validate_worker_request_artifact` is `ESSENTIAL_VALIDATION`, and
`_unique_relative_paths` is `DUPLICATE_HELPER_OBSERVATION`. The operational
grounding summary, Human Interface transport, and AiCLI render changes are
`ESSENTIAL_PRESENTATION`; `run_interactive_conversation` is
`ESSENTIAL_BINDING`.

G31-07 correctly found no duplicated Repository Cognition capability. The
local AST pass enriches only paths already selected by `detect_capabilities`;
no public symbol-rich immutable Repository Cognition artifact existed. Its
accepted observations—local hash verification and relative-path
normalization—remain visible and unrepaired.

## 9. G31-08 symbol classification

File: `aigol/runtime/grounded_worker_request_execution_authorization_binding.py`.

| Symbol(s) | Span | Responsibility | Classification |
|---|---:|---|---|
| version, artifact, and two status constants | 37–48 | Define one authorization-review binding | `ESSENTIAL_BINDING` |
| `REPLAY_STEPS` | 49–52 | Define ordered review wrappers | `ESSENTIAL_REPLAY` |
| `FALSE_BOUNDARIES` | 54–76 | Assert no confirmation, authorization, or Worker stage | `ESSENTIAL_VALIDATION` |
| `bind_grounded_worker_request_to_execution_authorization_review` | 79–142 | Coordinate grounding validation and existing pending summary creation | `ESSENTIAL_BINDING` |
| `validate_grounded_worker_request_execution_authorization_review` | 145–223 | Recompute exact scope and validate all boundaries | `ESSENTIAL_VALIDATION` |
| `reconstruct_grounded_worker_request_execution_authorization_review` | 226–274 | Reconstruct nested G31-06 and ordered G31-08 Replay | `ESSENTIAL_REPLAY` |
| `render_grounded_worker_request_execution_authorization_review` | 277–300 | Render distinct review checkpoint | `ESSENTIAL_PRESENTATION` |
| `_exact_authorization_scope`; `_pending_execution_summary` | 303–415 | Project exact grounding evidence into the existing summary contract | `ESSENTIAL_PROJECTION` |
| `_review_binding_artifact`; `_failed_review_binding_artifact` | 418–507 | Materialize positive or fail-closed transition evidence | `ESSENTIAL_BINDING` |
| `_upstream_identities` | 510–544 | Project unchanged upstream hashes | `ESSENTIAL_PROJECTION` |
| `_ensure_replay_available` | 547–552 | Preflight a two-file Replay | `DUPLICATE_HELPER_OBSERVATION` |
| `_persist_step` | 555–567 | Persist artifact-specific ordered wrappers using public transport | `ESSENTIAL_REPLAY` |
| `_required_text` | 570–573 | Local non-empty string boundary | `DUPLICATE_HELPER_OBSERVATION` |
| `_failure_reason` | 576–579 | Produce a bounded fail-closed explanation | `ESSENTIAL_PRESENTATION` |

The operational summary and AiCLI renderer are `ESSENTIAL_PRESENTATION`;
`run_interactive_conversation` is `ESSENTIAL_BINDING`; lifecycle-state and
next-action projections plus Human Interface transport are
`ESSENTIAL_PROJECTION`. G31-08 uses public `verify_replay_hash` and does not
copy the G31-06 `_verify_hash`, `_relative_path`, or `_unique_relative_paths`
helpers.

## 10. G31-09 symbol classification

File: `aigol/runtime/grounded_execution_authorization_human_decision_binding.py`.

| Symbol(s) | Span | Responsibility | Classification |
|---|---:|---|---|
| runtime version, result family, three statuses | 25–29 | Define one distinct decision-result transition | `ESSENTIAL_BINDING` |
| `REPLAY_STEPS` | 30–33 | Define ordered decision wrappers | `ESSENTIAL_REPLAY` |
| `FALSE_BOUNDARIES` | 35–52 | Assert decision is not authorization or execution | `ESSENTIAL_VALIDATION` |
| `bind_distinct_human_execution_decision` | 53–133 | Bind contextual approve/reject to exact G31-08 review/session | `ESSENTIAL_BINDING` |
| `validate_distinct_human_execution_decision` | 134–211 | Validate two-decision identity, rejection, confirmation, and boundaries | `ESSENTIAL_VALIDATION` |
| `reconstruct_distinct_human_execution_decision` | 212–237 | Reconstruct nested review and ordered decision Replay | `ESSENTIAL_REPLAY` |
| `render_distinct_human_execution_decision` | 238–255 | Render first-versus-second decision and stop state | `ESSENTIAL_PRESENTATION` |
| `_accepted_result`; `_failed_result` | 256–332 | Materialize exact approved, rejected, or failed decision evidence | `ESSENTIAL_BINDING` |
| `_reject_prior_decision` | 333–346 | Enforce one terminal decision per review/session | `ESSENTIAL_VALIDATION` |
| `_ensure_replay_available` | 349–352 | Preflight the two-file Replay | `DUPLICATE_HELPER_OBSERVATION` |
| `_persist` | 355–359 | Persist transition-specific ordered wrappers using public transport | `ESSENTIAL_REPLAY` |
| `_text` | 362–365 | Local non-empty string boundary | `DUPLICATE_HELPER_OBSERVATION` |

AiCLI `_record_contextual_execution_decision` and the contextual state changes
in `run_reference_uhi_session` are `ESSENTIAL_BINDING`; `_reference_runtime_status`
is `ESSENTIAL_PROJECTION`; `_render_help` is `ESSENTIAL_PRESENTATION`.
Operational summary and Human Interface changes are respectively
`ESSENTIAL_PRESENTATION` and `ESSENTIAL_PROJECTION`.

The strict two-decision model is preserved: G31-04 approval authorizes only
continuation; G31-09 records a separate execution decision. Approval creates
the existing human-confirmation evidence but no authorization artifact.
Rejection creates no confirmation and terminally blocks authorization.

## 11. G31-10 symbol classification

File: `aigol/runtime/confirmed_grounded_execution_authorization_binding.py`.

| Symbol(s) | Span | Responsibility | Classification |
|---|---:|---|---|
| `RUNTIME_VERSION` | 31 | Identify the bounded compatibility projection | `ESSENTIAL_BINDING` |
| `REPLAY_STEPS` | 32–37 | Name existing projected artifacts in required order | `ESSENTIAL_REPLAY` |
| `FORBIDDEN_OPERATIONS`; `STOP_BOUNDARIES` | 38–54 | Enforce no Worker or mutation stage | `ESSENTIAL_VALIDATION` |
| `authorize_confirmed_grounded_execution_decision` | 57–233 | Validate G31-09, project existing ready families, call existing authorization | `ESSENTIAL_BINDING` |
| `reconstruct_confirmed_grounded_execution_ready_replay` | 236–300 | Validate projected existing artifacts and complete nested lineage | `ESSENTIAL_REPLAY` |

Existing execution-authorization changes are narrow:
`_load_execution_ready_lineage` and
`reconstruct_execution_authorization_replay` are `ESSENTIAL_VALIDATION`;
`_authorization_request` and `_authorization_artifact` are
`ESSENTIAL_PROJECTION`. AiCLI `run_reference_uhi_session` and
`_record_contextual_execution_decision` changes are `ESSENTIAL_BINDING` plus
`ESSENTIAL_PRESENTATION` of already-owned evidence.

G31-10 introduces no canonical artifact family, private helper, approval,
policy, or authorization owner. It uses public serialization, hash,
validation, and Replay contracts.

## 12. Cross-generation helper and idiom audit

| Idiom | Exact G31 locations | Existing public equivalent | Classification | Disposition |
|---|---|---|---|---|
| artifact hash verification | G31-04 `_validate_hash_bound_snapshot`; G31-05 `_validate_hash`; G31-06 `_verify_hash` | `verify_replay_hash(..., hash_field="artifact_hash")` | `EXISTING_PUBLIC_FUNCTION_UNDERUSED` and local `DUPLICATE_HELPER_OBSERVATION` | Defer consolidation; do not copy into G31-11B |
| repository-relative path normalization | G31-06 `_relative_path`; Worker bridge `_unique_relative_paths` | Several scope-specific validators, but no one universally compatible path API | `DUPLICATE_HELPER_OBSERVATION` | Preserve accepted behavior; future shared contract requires a separate bounded audit |
| required non-empty string guard | G31-04/05/06 `_require_string`; G31-08 `_required_text`; G31-09 `_text` | No public generic FailClosed string validator | `DUPLICATE_HELPER_OBSERVATION` | Small local repetition; no architectural repair required |
| two-file Replay preflight | G31-05/06/08/09 `_ensure_replay_available` | `write_json_immutable` protects one file, not a pair | `DUPLICATE_HELPER_OBSERVATION` | Candidate for later transport utility only with atomicity semantics preserved |
| ordered wrapper construction | G31-04 persist helpers; G31-05/06/08 `_persist_step`; G31-09 `_persist` | Public hashing and immutable write primitives, no generic typed ordered-wrapper contract | `JUSTIFIED_LOCAL_HELPER` / `ESSENTIAL_REPLAY` | Artifact-specific filenames, steps, and order remain local |
| wrapper validation | G31-04/05/06 `_validate_wrapper`; later modules use public hash verifier plus local order checks | Public hash verification does not own artifact-specific ordering | `ESSENTIAL_REPLAY` with bounded repeated shape | No subsystem duplication; do not generalize during Worker selection |
| explicit false-boundary maps | all six modules | No single map is valid for every lifecycle stage | `ESSENTIAL_VALIDATION` | Keep explicit; merging could erase stage-specific truth |
| presentation mapping across Platform Core, runtime entry, and AiCLI | each operational milestone | Existing layered presentation ownership | `ESSENTIAL_PRESENTATION` | Necessary layer projection, not duplicated semantics |

No second canonicalizer, serializer, immutable writer, Replay store, repository
index, planner, selector, approval engine, authorization policy, Worker
registry, Worker assignment runtime, Provider runtime, or mutation runtime was
created. The consolidation observations are implementation idioms only.

## 13. Reuse, authority, and stop-boundary assessment

The audited chain reuses these existing public owners:

- Project Objective, Platform Knowledge, capability coverage, development
  planning, and Durable Governed Work for G31-04;
- PPP, governed implementation request, and Worker-request families for
  G31-05;
- `detect_capabilities`, existing mutation-layer classification, and
  Worker-request scope projection for G31-06;
- existing execution summary and human-confirmation contracts for G31-08 and
  G31-09;
- existing execution-ready and execution-authorization families and
  `authorize_execution_ready` for G31-10;
- existing Worker registry, deterministic selection, selection Replay, and
  certification for the next G31-11B edge.

At every accepted stage AiCLI transports commands and renders canonical
fields. It does not classify the goal, compose the plan, select repository
targets, approve, authorize, select a Worker, dispatch, invoke, or mutate.

The stop states remain truthful:

```text
G31-04  proposal approval consumed; execution authorization false
G31-05  Worker payload composed; repository scope unresolved
G31-06  repository scope grounded; authorization false
G31-08  authorization review pending; human execution decision absent
G31-09  distinct human decision recorded; authorization artifact absent
G31-10  execution authorized; Worker selection absent
```

Proposal approval never becomes execution authorization. No G31-04 through
G31-10 path selects, assigns, dispatches, or invokes a Worker; invokes a
Provider; executes a command; or mutates the repository.

## 14. Validation and governance evidence

Focused validation was run after reconstructing the commit and symbol maps:

| Validation group | Result |
|---|---:|
| G31-04, G31-05, G31-06, G31-08, G31-09, G31-10 accepted tests | 149 passed, 0 skipped, 0 failed |
| execution summary, human confirmation, and execution authorization | 30 passed, 0 skipped, 0 failed |
| Worker registry/runtime, ERR, unified selection, selection certification, and assignment compatibility | 71 passed, 0 skipped, 0 failed |
| reference Human Interface, runtime entry, and AiCLI continuity | 42 passed, 0 skipped, 0 failed |
| Replay-focused repository tests | 245 passed, 0 skipped, 0 failed |
| Governance tests | 96 passed, 0 skipped, 0 failed |

These focused counts overlap and must not be added as a repository-suite
total. The evidence is internally consistent with the accepted reports and
G31-11A, so the full repository suite was not run, as required by the audit
scope.

The read-only governance conformance engine reports:

- status: `PARTIALLY_CONFORMANT`;
- checks passed: 18;
- checks failed: 2;
- critical violations: 0;
- deterministic: true;
- fail-closed: true;
- read-only: true.

The two known findings remain unchanged: missing expected/installed root
pre-commit hooks, and the system pre-commit hook missing
`promotion_gate_v02` and `check_layer_freeze`. G31-R01 neither hides nor
repairs them. They do not prove duplication in the audited G31 transitions.

## 15. Retrospective conclusion and deferred consolidation

The six bindings are larger than simple field mappings because each edge
preserves immutable identities, validates nested source artifacts, records
ordered Replay, rejects substitution, projects truthful presentation, and
states the next authority boundary explicitly. Removing those responsibilities
would reduce lines by weakening the certified lifecycle.

The audit does not find a redundant canonical artifact, parallel owner, or
architectural duplicate. It does find bounded consolidation opportunities:

1. adopt public `verify_replay_hash` wherever a future touched module still
   performs equivalent local artifact-hash verification;
2. consider one tested multi-file Replay preflight/wrapper utility only in a
   separate transport-owned change that preserves append-only and ordering
   behavior;
3. consider a public repository-relative path contract only after reconciling
   the different workspace, artifact, and mutation consumers;
4. avoid introducing another local required-string guard in G31-11B.

These observations do not justify reopening accepted generations or delaying
the bounded Worker-selection projection. Consolidating them inside G31-11B
would broaden that unit and increase regression risk. Therefore:

`G31_BINDINGS_ACCEPTED_WITH_CONSOLIDATION_OBSERVATIONS`

`READY_FOR_G31_11B_WITH_DEFERRED_CONSOLIDATION`

Exactly one next blocker remains:

`G31_10_AUTHORIZATION_EXISTING_WORKER_SELECTION_BOUNDED_PROJECTION_ABSENT`

The evidence does not change the G31-11A planning estimates: no-copy/paste
conversational governed development remains **97%**, and overall project
progress remains **86%**. These are evidence-scoped planning indicators, not
certification or production-readiness claims. Deferred helper consolidation
does not add a required lifecycle stage and therefore does not change either
denominator.

## 16. Corrected bounded G31-11B prompt

```text
# Generation 31-11B — G31-10 Authorization to Existing Certified Worker Selection Binding

Treat Generation 30, committed G31-02 through G31-10, G31-11A, and G31-R01 as
immutable accepted baselines.

G31-11A verdict:

EXISTING_CERTIFIED_WORKER_SELECTION_REUSABLE_BOUNDED_PROJECTION_REQUIRED

G31-R01 verdicts:

G31_BINDINGS_ACCEPTED_WITH_CONSOLIDATION_OBSERVATIONS
READY_FOR_G31_11B_WITH_DEFERRED_CONSOLIDATION

First true blocker:

G31_10_AUTHORIZATION_EXISTING_WORKER_SELECTION_BOUNDED_PROJECTION_ABSENT

## Objective

Implement exactly one reuse binding:

valid G31-10 execution authorization
  -> exact existing native-development Worker selection input
  -> select_unified_resource
  -> existing RESOURCE_SELECTION_ARTIFACT_V1 and Replay
  -> stop before Worker assignment

Do not create or redesign a Worker registry, selector, eligibility policy,
Worker identity, authorization system, assignment runtime, or Replay subsystem.

## Required reuse

Reuse:

- reconstruct_execution_authorization_replay;
- reconstruct_confirmed_grounded_execution_ready_replay;
- the exact G31-10 authorization request, decision, artifact, result, scope,
  packet, and nested G31 lineage;
- default_resource_registry;
- select_unified_resource;
- reconstruct_unified_resource_selection_replay;
- existing WORKER_ROLE, IMPLEMENTATION_ASSISTANCE, and NATIVE_DEVELOPMENT
  vocabulary;
- existing Human Conversation Experience and presentation contracts;
- public replay_hash, verify_replay_hash, serialization, immutable write,
  validation, and Replay contracts.

Do not copy any G31-R01 consolidation observation: no local artifact-hash
verifier, required-string helper, path normalizer, Replay preflight, wrapper
validator, or new false-boundary abstraction. Deferred consolidation is not
part of G31-11B.

## Required behavior

Validate the exact authorization and project only:

- workflow_type: NATIVE_DEVELOPMENT;
- required_capability: IMPLEMENTATION_ASSISTANCE;
- requested_role_type: WORKER_ROLE;
- domain_id: NATIVE_DEVELOPMENT;
- worker_authorization_required: true;
- context_reference: exact execution-authorization identity;
- context_hash: exact execution-authorization artifact hash.

Select exactly one existing eligible resource or preserve the selector's
existing fail-closed no-match or ambiguity result. Bind selection Replay to the
complete G31 authorization lineage.

Required stop state:

worker_selected = true only on successful existing selection
worker_assigned = false
worker_dispatched = false
provider_invoked = false
worker_invoked = false
command_executed = false
repository_mutated = false

Do not call assign_worker_from_invocation_request, dispatch, Provider or Worker
invocation, command execution, or repository mutation.

## Fail-closed requirements

Reject failed, revoked, expired, replayed, substituted, broadened,
cross-session, or Replay-invalid authorization; changed summary or confirmation;
changed grounded scope, role, Project Objective, Repository Cognition evidence,
or G31 identity; unsupported capability/domain projection; changed registry or
selection context; and reordered or substituted selection Replay.

Invalid evidence must not partially select or assign a Worker.

## Minimal-change gate

Use no new canonical artifact family and preferably no new production file.
Maximum production additions: 200 lines. Reuse existing public validation and
Replay contracts. Stop and report if the existing selector cannot represent
the transition within this bound.

## Validation

Add focused G31-11B tests for exact authorization consumption, positive existing
selection, no-match, ambiguity, tampering, Replay, context lineage, authority
boundaries, and no assignment. Run G31-10, unified selection, ERR, Worker
registry/certification, authorization, Replay, Human Interface/AiCLI,
Governance, py_compile, and git diff --check. Run the full suite once only after
focused evidence passes.

Perform a real PTY-backed ./aicli validation in a disposable repository using
only an ordinary request and contextual approvals. Demonstrate existing Worker
selection, truthful stop before assignment, fail-closed tampering, nested
Replay reconstruction, and no dispatch, invocation, command, or mutation.
Remove the disposable repository afterward.

## Documentation

Add:

docs/governance/G31_11B_G31_10_AUTHORIZATION_EXISTING_CERTIFIED_WORKER_SELECTION_BINDING.md

Report exact files, size, symbols, reused contracts, PTY and Replay evidence,
validation/governance counts, authority boundaries, progress, one next blocker
or readiness verdict, git status, and commit commands. Do not commit.
```

No commit was created by this audit.
