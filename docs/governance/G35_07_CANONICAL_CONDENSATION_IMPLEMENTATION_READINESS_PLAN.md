# G35-07 Canonical Condensation Implementation Readiness Plan

Status: IMPLEMENTATION BLUEPRINT — NO RUNTIME IMPLEMENTATION
Version: 1.0.0
Authority: Platform Core constitutional development planning
Source specification: G35-05 Canonical Governed Development Condensation Contract
Source audit: G35-06 Canonical Condensation Integration Readiness Audit

## 1. Purpose

This plan defines the smallest deterministic implementation and certification
sequence for introducing Canonical Governed Development Condensation into a
future certified Platform Core revision. It is planning evidence only. It does
not authorize a mutation, change runtime behavior, or certify an implementation.

The implementation objective is:

```text
completed governed-development objective
→ non-authoritative condensation proposal
→ deterministic validation
→ exact human review and approval
→ approved bounded synthesis projection
→ unchanged G31 preflight
→ unchanged governed CODEX lifecycle
```

The following existing guarantees remain fixed:

- `CODEX_SYNTHESIS_PREFIX == "runtime validation: "`;
- the final input maximum remains 240 Unicode code points;
- existing preflight remains final admission authority;
- original human request remains immutable primary intent evidence;
- no condensation approval is execution authorization;
- Worker selection, assignment, dispatch, invocation, and process activation
  retain their current owners; and
- `DIRECT_EXACT_REQUEST_V1` remains available for compatible short requests.

## 2. Architectural Decision

Canonical Governed Development Condensation is a **new certified Platform
capability**. Its integration requires a **versioned G31 synthesis-input
binding**, but does not revise the existing G31 preflight algorithm.

PCBV31 remains an immutable historical baseline. Any runtime containing the
new binding must be certified as a new Platform Core revision. Reclassifying
the work as configuration, silently passing a different string to G31, or
changing only AiCLI presentation is prohibited.

## 3. Exact Insertion Point

The integration point is the current transition from the completed
conversation approval summary to the early synthesis preflight:

```text
approval_summary["canonical_runtime_prompt"]
→ run_human_interface_runtime_entry(...g31_synthesis_preflight_prompt=...)
→ preflight_codex_worker_synthesis(...)
```

The new stage is inserted after `summary_admissible` and construction of the
completed Project Objective/implementation-turn evidence, but before the first
call to G31 preflight and before the existing implementation approval.

The condensation decision is a new semantic-review decision. Existing
implementation, grounded-execution, and CODEX-activation decisions remain
separate and are not renumbered or reinterpreted.

## 4. Planned Runtime Change Surface

### 4.1 New Platform Core modules

| Planned module | Responsibility | Change class | Replay | Hash impact | Authorization impact |
| --- | --- | --- | --- | --- | --- |
| `aigol/runtime/canonical_governed_development_condensation_runtime.py` | Construct `CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION_ARTIFACT_V1` from authenticated original request, clarification, completed objective, and workspace/session evidence. V1 uses deterministic rules only. | Additive | Produces proposal for Replay owner; does not persist independently | New deterministic artifact ID/hash | None; all authority flags false |
| `aigol/runtime/canonical_governed_development_condensation_validation_runtime.py` | Validate schema, source lineage, requirement mapping, ambiguity, Unicode counts, proposal method, and canonical hash. | Additive | Produces immutable validation result | New validation ID/hash and ordered failure-code commitment | None; PASS permits review only |
| `aigol/runtime/canonical_governed_development_condensation_human_decision_runtime.py` | Build review envelope and bind exact APPROVE/REJECT decision to source, proposal, validation, and projected-request hashes. | Additive | Produces review and decision records | New review/decision hashes | Adds semantic approval only; explicitly not execution authorization |
| `aigol/runtime/canonical_governed_development_condensation_replay.py` | Persist and reconstruct ordered proposal, validation, review/decision, and bounded-projection evidence under the existing Replay owner. | Additive | New four-stage Replay family | New wrapper/replay hashes | None; reconstruction cannot approve or authorize |

These four modules are separate because proposal production, deterministic
validation, Human Authority, and Replay ownership are constitutionally distinct.
No LLM proposal producer is included in the first implementation revision.

### 4.2 Existing parent-runtime modules that require modification

| Module | Why it changes | Change class | Replay change | Hash impact | Authorization change |
| --- | --- | --- | --- | --- | --- |
| `aigol/cli/aicli.py` | Insert condensation review before the current early preflight; render source/proposal differences; collect exact approval/rejection; persist the selected input mode in pending state. | Versioned orchestration | Exposes new Replay references; does not own Replay | AiCLI session/transcript state changes only on condensation path | No authority; transports Human Authority decision |
| `aigol/runtime/human_interface_runtime_entry_service.py` | Accept and validate the approved condensation bundle, preserve it across G31 application transitions, and pass the approved projection to preflight and the Core runner. | Versioned common-entry binding | Carries new Replay references in application state | G31 aggregate state hash/identity changes on V2 path | No new authority; rejects missing/substituted approval |
| `aigol/cli/aigol_cli.py` | Carry the approved condensation decision from common entry into the existing grounded execution-authorization review call. | Versioned Core orchestration | Adds source Replay reference to turn aggregation | Turn summary/aggregate hashes change on V2 path | No decision authority; transport only |
| `aigol/runtime/grounded_worker_request_execution_authorization_binding.py` | Introduce a V2 review/scope that explicitly binds input mode, original-request hash, condensation/validation/approval hashes, and bounded-projection hash. | Versioned artifact family | Existing two-step Replay gains V2 artifact content, not a new owner | Review, scope, summary, and wrapper hashes change | Authorization scope becomes condensation-aware but is not broadened |
| `aigol/runtime/grounded_execution_authorization_human_decision_binding.py` | Validate and repeat the new V2 scope commitments in the distinct grounded-execution decision. | Versioned artifact family | Existing decision Replay records V2 commitments | Decision, confirmation, and Replay hashes change | Existing human decision scope remains unchanged; continuity checks increase |
| `aigol/runtime/codex_worker_activation_binding_runtime.py` | Select `DIRECT_EXACT_REQUEST_V1` or `APPROVED_CONDENSATION_V1`; reconstruct condensation Replay; form the V2 Worker contract; bind proposal/approval/projection through activation review, third approval, handoff, receipt, and reconstruction. | Versioned G31 input binding | Existing three-step activation Replay records V2 lineage | Preflight, contract, review, approval, prompt, handoff, receipt, and Replay hashes change on condensation path | No new activation authority; existing third approval binds the exact V2 handoff |
| `aigol/runtime/codex_task_outcome_human_review_runtime.py` | Present original contextual request separately from the approved condensed Worker task and verify both lineages during output review. | Versioned review compatibility | Existing task-outcome Replay carries V2 source commitments | Review packet, criteria, decision, and Replay hashes change | Result acceptance authority remains separate and unchanged |
| `aigol/runtime/platform_capability_certification_registry.py` | Register the new capability and its eventual certification evidence without upgrading incomplete evidence. | Additive registry entry | Registry evidence references only | Registry artifact hash changes when regenerated | None |

### 4.3 Existing nested `sapianta_system` modules that require modification

| Module | Why it changes | Change class | Replay change | Hash impact | Authorization change |
| --- | --- | --- | --- | --- | --- |
| `runtime/codex_synthesis/governed_codex_task_request.py` | Define V2 Worker execution contract and task request fields for input mode, original source hash, condensation hash, approval hash, and projection hash. | Versioned with V1 reader retained | Request becomes new Replay input | Request and contract identities change only for V2 | None |
| `runtime/codex_synthesis/governed_codex_task_classifier.py` | Classify V2 from validated semantic commitments or an explicit approved task class instead of re-inferring solely from compact text; preserve legacy lexical classification for V1. | Versioned classifier | Classification remains synthesis evidence | Response identity changes for V2 | None; classifier cannot authorize |
| `runtime/codex_synthesis/governed_codex_task_response.py` | Fail closed unless V2 natural language ends with the exact approved task and all condensation commitments agree; retain the existing 240 check. | Versioned validation | Synthesis response evidence contains V2 validation | Response/replay identity and prompt hash change for V2 | None |
| `runtime/codex_synthesis/governed_codex_prompt_synthesizer.py` | Render the approved condensed task as primary task data while displaying immutable source/condensation identifiers without promoting them to instructions. | Versioned prompt contract | Prompt remains synthesis evidence | Structured prompt hash changes for V2 | None; CODEX remains Worker only |
| `runtime/codex_synthesis/governed_codex_prompt_validator.py` | Require V2 task/source sections and reject missing, duplicated, or instruction-positioned condensation metadata while retaining the 2,400-character prompt bound. | Versioned validation | Prompt validation remains synthesis evidence | Validation and response identities change for V2 | None |
| `runtime/codex_synthesis/governed_codex_evidence.py` | Expose source, mode, condensation, approval, and projection commitments. | Additive V2 evidence | V2 synthesis evidence expands | Evidence/replay hash changes for V2 | None |
| `runtime/codex_synthesis/governed_codex_replay.py` | Include V2 source and projection commitments explicitly in replay identity rather than relying only on nested incidental hashing. | Versioned identity seed | Yes, V2 identity schema | New V2 replay identity | None |
| `runtime/codex_synthesis/__init__.py` | Export V2 request/contract constructors while preserving V1 exports. | Additive | None | None directly | None |
| `runtime/codex_handoff/governed_codex_handoff_request.py` | Bind original request separately from approved synthesis input and its condensation decision. | Versioned request | V2 handoff Replay input | Request identity changes for V2 | None |
| `runtime/codex_handoff/governed_codex_handoff_response.py` | Carry V2 binding fields into package seed and fail closed on missing continuity. | Versioned response | V2 handoff identity content | Package/replay/export hashes change | None |
| `runtime/codex_handoff/governed_codex_handoff_package.py` | Define `GOVERNED_CODEX_HANDOFF_PACKAGE_V2` containing original-source and approved-condensation commitments. | Versioned; V1 retained | Package becomes downstream Replay evidence | Package hash changes for V2 | Package still declares no downstream authority |
| `runtime/codex_handoff/governed_codex_handoff_validator.py` | Verify V2 package/source/projection/approval continuity and reject mixed V1/V2 fields. | Versioned fail-closed validation | Validation evidence changes | Validation and package-dependent hashes change | Prevents unapproved projection from reaching the execution gate |
| `runtime/codex_handoff/governed_codex_handoff_evidence.py` | Expose both original contextual request and exact approved Worker task. | Additive V2 evidence | V2 evidence expands | Evidence hash changes | None |
| `runtime/codex_handoff/governed_codex_handoff_replay.py` | Bind V2 condensation lineage into handoff replay/export identity. | Versioned identity seed | Yes | New V2 Replay/export identity | None |
| `runtime/codex_handoff/__init__.py` | Export versioned V2 constructors/validators while retaining V1 compatibility. | Additive | None | None directly | None |
| `runtime/execution_gate/governed_execution_authorization_chain.py` | Add a `CONDENSATION_APPROVAL_VERIFIED` chain step for V2 packages before explicit activation approval and token issuance. | Versioned chain | Existing authorization evidence records one additional V2 step | Authorization replay/receipt identities change for V2 | No new authority; exposes prior semantic approval |

### 4.4 Modules intentionally not modified

The following are mandatory regression surfaces but should not receive
production changes unless tests prove an undocumented incompatibility:

- `aigol/runtime/platform_project_objective_inference.py` — remains source of
  completed objective evidence;
- `aigol/runtime/platform_implementation_turn_durable_work_binding.py` — remains
  immutable source/first-approval lineage; condensation is a separate later
  approval;
- repository grounding, Worker payload, selection, assignment, dispatch,
  invocation, candidate bridge, and governed execution modules — continue to
  bind the V2 authorization-scope hash transitively;
- `aigol/runtime/execution_authorization_runtime.py` and
  `confirmed_grounded_execution_authorization_binding.py` — already copy and
  hash the complete authorization scope;
- execution-gate authority-token, authorization-validator, receipt, and Replay
  modules — already bind the complete validated handoff package and prompt hash;
- execution-consumer and CODEX execution-adapter modules — already validate or
  consume the handoff/prompt hashes and retain the original request in evidence;
- result capture and semantic validation bindings — operate on authentic output
  and existing activation hashes, not on task condensation semantics.

Any proposed change to one of these modules requires a recorded failed
compatibility test demonstrating why transitive hash binding is insufficient.

## 5. Governance and Certification Artifact Surface

These non-runtime artifacts must be created or versioned during an authorized
implementation generation:

| Artifact | Required action |
| --- | --- |
| G35-05 specification | Retain unchanged as the normative contract. Any semantic change requires a new specification version. |
| Capability registry/matrices | Add `CANONICAL_GOVERNED_DEVELOPMENT_CONDENSATION`; do not upgrade `GOVERNED_CODEX_TASK_SYNTHESIS` merely because the new capability exists. |
| Condensation executable contract/schema | Define exact field sets, canonical serialization, failure codes, and supported V1 proposal method. |
| G31 input-binding contract V2 | Define direct and condensation modes and prohibit mixed-mode artifacts. |
| Replay manifest/evidence | Register the new four-stage Replay family and its reconstructors. |
| Human-decision certification evidence | Prove source/proposal difference visibility, exact approval binding, rejection, and one-artifact scope. |
| Compatibility report | Prove unchanged V1 short-request outputs, hashes, Replay order, and approval counts. |
| Platform capability certification | Certify the new capability independently before G31 activation binding is enabled. |
| G31 integration certification | Certify the complete approved-condensation-to-preflight-to-handoff chain. |
| Platform Core baseline declaration | Record the new baseline only after full regression and constitutional certification. PCBV31 history remains unchanged. |

No historical artifact, replay record, capability entry, or certification may
be edited in place. New versions refer to prior identities and preserve their
original hashes.

## 6. Deterministic Implementation Sequence

Each step must leave the repository importable, the legacy V1 path runnable,
and all completed checkpoints green before the next step begins.

### Step 0 — Baseline and fixture freeze

- Record PCBV31 source revision and the current known partial-conformance
  findings.
- Create immutable golden fixtures for short requests at final lengths 20, 21,
  239, and 240 and rejected fixtures at 241 and above.
- Capture V1 task-request, synthesis, handoff, authority-token, activation,
  task-outcome, and Replay identities for compatibility comparison.

Checkpoint: existing focused G31 tests, governance tests, deterministic Replay
tests, and `git diff --check`. No new capability code exists yet.

### Step 1 — Add canonical artifact model and deterministic proposal producer

- Add the artifact constructor and canonical serializer.
- Implement only `DETERMINISTIC_RULES` for V1.
- Keep the module unreachable from Human Interface and G31 orchestration.

Checkpoint: unit tests for canonical identity, Unicode handling, stable ordering,
duplicate/missing requirements, no authority flags, and unchanged imports.

### Step 2 — Add deterministic validator

- Add every G35-05 failure code and exact schema/lineage/requirement-map checks.
- Prove that PASS permits review only and cannot construct an approval or G31
  request.

Checkpoint: validator unit and negative tests, canonical-hash tests, mutation
substitution tests, and governance boundary tests.

### Step 3 — Add Replay family and reconstruction

- Add ordered proposal, validation, review/decision, and projection wrappers.
- Initially exercise Replay using fixtures only; do not connect AiCLI.
- Reject partial, reordered, duplicate, cross-session, and mixed-source Replay.

Checkpoint: Replay round-trip, corruption, ordering, historical-read, and
cross-session tests; governance tests for unchanged Replay ownership.

### Step 4 — Add human review and decision artifact

- Build the exact source-versus-proposal review envelope.
- Bind APPROVE/REJECT to source bundle, proposal, validation, and projected
  request hashes.
- Keep the decision API unreachable from normal G31 routing.

Checkpoint: unit tests for exact approval, rejection, stale source, changed
proposal, changed validation, changed projection, actor/time validation, and
approval non-authority.

### Step 5 — Add dormant nested V2 synthesis and handoff contracts

- Add V2 request, Worker contract, evidence, Replay identity, and handoff
  package support in `sapianta_system`.
- Retain V1 constructors and validators unchanged.
- Require an explicit V2 input-mode discriminator; mixed or missing version
  fields fail closed.
- Do not route production requests to V2.

Checkpoint: nested unit tests; V1 golden compatibility; V2 task substitution,
source/approval/projection substitution, 240-bound, prompt, handoff, execution
gate, consumer, and adapter tests. Run the nested affected-suite regression.

### Step 6 — Add dormant parent V2 authorization binding

- Add optional approved-condensation input to Core orchestration.
- Add V2 authorization review/scope and V2 grounded human decision support.
- Propagate the new scope unchanged through existing authorization, selection,
  assignment, dispatch, invocation, candidate, and governed-execution paths.
- Keep V1 as the only selected production mode.

Checkpoint: G31-08 through governed-execution focused tests; scope-hash and
decision Replay tests; negative tests proving condensation approval cannot
authorize execution or Worker selection. Run governance tests.

### Step 7 — Add common-entry condensation review state

- Introduce a distinct pending action for condensation review.
- Add deterministic input-mode selection without enabling V2 activation.
- Persist approved condensation Replay reference/hash in common-entry state.
- Prove Human Interfaces only render and transport the decision.

Checkpoint: common-entry and AiCLI unit tests; multi-line/clarification tests;
cancel/reject/resume/session-isolation tests; interface-neutrality tests; Replay
tests for proposal through approved projection. Run governance tests.

### Step 8 — Bind approved projection to G31 activation

- Update G31 preflight binding to accept one typed source: direct V1 input or
  approved V2 projection.
- Reconstruct condensation Replay during review, activation, and Replay
  reconstruction.
- Build V2 Worker contract and handoff and bind them through the existing third
  approval and execution gate.
- Leave the 20/240 contract and preflight implementation unchanged.

Checkpoint: G31 preflight, activation, handoff, authorization, receipt, Replay,
prompt-fidelity, and substitution tests. Run all G31-17B through G31-21B
regressions and the affected nested suite.

### Step 9 — Align task-outcome review

- Present original contextual request, approved condensed task, exact Worker
  prompt, and Worker output as distinct fields.
- Evaluate output against the approved Worker task while retaining the original
  request for human context and source-fidelity review.

Checkpoint: task-outcome review/decision, exact-byte, unified-diff, rejection,
rework, Replay, and no-mutation tests. Run the complete G31 focused lifecycle.

### Step 10 — Enable explicit coexistence

- Enable `DIRECT_EXACT_REQUEST_V1` for all currently compatible short requests.
- Enable `APPROVED_CONDENSATION_V1` only after a direct-input length
  determination proves V1 cannot enter preflight and a fully approved V2
  artifact exists.
- Prohibit fallback between modes after approval or preflight failure.

Checkpoint: dual-mode decision table, legacy golden hashes, long-request
success/failure, mixed-mode rejection, no-retry/no-fallback, cross-session, and
full end-to-end Replay tests.

### Step 11 — Certification candidate freeze

- Freeze implementation and evidence manifests.
- Run static validation, all affected tests, governance conformance, complete
  repository regression, and deterministic replay twice from clean temporary
  destinations.
- Record limitations and known partial conformance without upgrading them.

Checkpoint: constitutional certification review. No production baseline is
declared before this step passes.

## 7. Certification Checkpoint Matrix

| Validation class | Required checkpoints |
| --- | --- |
| Unit tests | After every implementation step; a failed unit checkpoint blocks continuation. |
| Replay tests | Steps 3, 4, 6, 7, 8, 9, 10, and final Step 11. |
| Governance tests | Baseline Step 0; ownership/authority Steps 2, 3, 4, 6, 7, 8; final Step 11. |
| Nested synthesis/handoff tests | Steps 5, 8, 10, and final Step 11. |
| G31 focused lifecycle | Steps 6, 8, 9, 10, and final Step 11. |
| Repository regression | Once after dormant contracts are integrated at Step 8; again after coexistence Step 10; final clean run at Step 11. |
| Constitutional certification | Only after Step 11 produces complete deterministic evidence and no unresolved regression. |

A repository regression must not be launched concurrently with another full
regression. Focused suites may run independently, but every result must name
its exact scope to avoid duplicate repository-wide validation.

## 8. Risk Assessment

| Risk class | Highest risk | Constitutional consequence | Required control |
| --- | --- | --- | --- |
| Replay | Approved projection and preflight input reconstruct to different text or identities while each record is individually hash-valid. | Replay could prove two internally valid but different tasks. | One canonical projection hash must be repeated and recomputed in decision, preflight, activation review, handoff, receipt, and reconstruction; reject mixed sessions/modes. |
| Authorization | Condensation approval is mistaken for implementation, grounded-execution, or CODEX-activation approval. | A semantic representation decision could acquire execution authority. | Separate artifact type, approval scope, pending action, authority flags, and Replay step; existing approvals remain mandatory. |
| Compatibility | Adding optional V2 fields changes V1 canonical serialization or replay identities for short requests. | PCBV31 historical reconstruction and golden evidence could drift. | Separate V1/V2 constructors and identity seeds; no defaulted V2 fields in V1 objects; byte-for-byte golden fixtures. |
| Worker | CODEX receives the original request while approval covers the condensed task, or task-outcome review evaluates a different task than CODEX received. | Worker prompt fidelity and human result review become invalid. | V2 Worker contract makes approved body the sole `authorized_task`; original remains separately labeled contextual evidence; exact prompt and criteria hashes must agree. |
| Semantic fidelity | A compact body passes structural validation after weakening a material prohibition. | Human could approve misleading condensation and execution scope could broaden. | Complete requirement map, deterministic prohibition/permission comparisons, visible difference report, and exact human approval; unresolved cases fail closed. |
| Operational rollout | A failed V2 attempt silently falls back to V1, retries condensation, or chooses another proposal. | Unapproved task substitution or hidden continuation. | One mode decision per source bundle; terminal failure for that artifact; every new proposal requires a new identity and approval. |

The highest overall risk is **cross-boundary Replay identity divergence**,
because it can mask both authorization and Worker-task substitution while local
hash checks still pass. End-to-end reconstruction is therefore the primary
certification gate.

## 9. Migration Strategy

### 9.1 `DIRECT_EXACT_REQUEST_V1`

During coexistence, V1 remains the default for requests whose exact canonical
input already satisfies G31:

```text
len("runtime validation: " + original_request) <= 240
```

V1 behavior, artifact shapes, approval count, prompt, handoff, hash seeds,
Replay ordering, and Worker lifecycle remain unchanged. The migration must not
inject `null` V2 fields or a new wrapper around V1 artifacts, because either
would change historical compatibility hashes.

### 9.2 `APPROVED_CONDENSATION_V1`

`APPROVED_CONDENSATION_V1` names version 1 of the condensation
artifact/capability mode. It is carried by version 2 of the G31 synthesis-input
binding because the historical G31 V1 binding supports direct exact input only.
These version axes are independent and MUST NOT be collapsed into one version
number.

G31 V2 eligibility requires all of:

1. exact direct input is over 240 code points;
2. source clarification and Project Objective are complete;
3. canonical condensation proposal exists;
4. deterministic validation is PASS;
5. Human Authority approved the exact review envelope;
6. projection and Replay reconstruction succeed; and
7. the projected final input is at most 240 code points.

Failure of any condition is terminal for that artifact. V2 cannot fall back to
direct input, truncate, retry, select a different proposal, or invoke CODEX.

### 9.3 Coexistence period

The first certified revision must support both modes. The coexistence period
has no time-based automatic expiry. It ends only through a later explicit
constitutional decision supported by compatibility evidence.

Metrics may report mode counts and failure classes as passive observability,
but must not influence routing, approval, authorization, or certification.

Historical V1 Replay is reconstructed only by V1 readers. New V2 readers may
read both versions but must never reinterpret V1 as an implicit condensation.

### 9.4 Rollback and failure containment

Before the final baseline declaration, V2 can remain dormant while V1 stays
operational. After V2 certification, a deployment rollback may select the last
certified runtime version, but no Replay record may be deleted, rewritten, or
down-converted. A V2 artifact produced by a later runtime remains V2 evidence
even if that runtime is no longer active.

## 10. Final Certification Sequence

The certification candidate must complete this order without mutation between
steps:

1. static import/compile and `git diff --check`;
2. new condensation model/validator/decision unit tests;
3. condensation Replay reconstruction and corruption suite;
4. nested synthesis, handoff, execution-gate, consumer, and adapter suites;
5. G31 authorization, selection, assignment, dispatch, invocation, activation,
   capture, validation, task-outcome, and mutation-boundary suites;
6. direct-mode golden compatibility suite;
7. approved-condensation end-to-end positive and negative suite;
8. governance conformance tests and governance engine, preserving known hook
   drift as visible partial conformance if still present;
9. one complete repository regression;
10. clean-destination deterministic Replay reproduction;
11. constitutional authority/ownership audit;
12. capability certification for Canonical Governed Development Condensation;
13. G31 V2 integration certification; and
14. new Platform Core baseline certification and release-evidence freeze.

No certification can be inferred from unit or repository test success alone.
The new capability is constitutionally available only after both its independent
certification and the G31 integration certification pass.

## 11. Acceptance Gates

Implementation readiness requires all of the following to be demonstrably true:

- every V1 golden artifact and replay identity is unchanged;
- every V2 artifact has an explicit version and input mode;
- original request and approved Worker task remain distinct and reconstructable;
- all material requirements are mapped and displayed to the human;
- no approval artifact acquires broader scope;
- G31 preflight remains byte-for-byte unchanged in its prefix/bound logic;
- no Worker stage changes owner or identity;
- no Provider, retry, fallback, hidden continuation, or mutation is added;
- corrupted, ambiguous, incomplete, unapproved, mixed-mode, cross-session, and
  over-bound inputs fail before Worker process activation;
- Replay proves the exact approved body equals the submitted preflight body;
- task-outcome review evaluates the exact Worker task; and
- complete regression and constitutional certification pass.

## 12. Implementation-Readiness Verdict

`CANONICAL_CONDENSATION_IMPLEMENTATION_SEQUENCE_READY_FOR_SEPARATE_AUTHORIZATION`

The repository contains the source evidence, Replay primitives, approval
mechanisms, G31 preflight, handoff, execution gate, and Worker lifecycle needed
to implement the capability through a bounded Platform Core revision. It does
not contain the condensation capability or its lineage socket today.

This plan authorizes nothing. A separate generation must explicitly authorize
Step 0 and the bounded implementation surface before any runtime, test,
configuration, registry, or certification artifact is changed.
