# Continuation D2 Inspection Binding Contract V1

Authority: STEP78CM exact binding contract, STEP78CN implementation authorization, and STEP78CO exact internal-owner function correction.
Status: minimum binding implemented under corrected CO function scope; release proof belongs to the retained CN G48 report. Not certified. Scope: typed Human-originated CWM to inspection inside the existing Objective Commitment gate.

## Activation and transport

Canonical Human Entry may provide optional `continuation_d2_input` only when the existing G66 capture reports `canonical_typed_semantic_composition.control == SEMANTIC_TURN`, there is no Objective Commitment handoff, and the flow requires the Objective Commitment gate. Its only field is `conversation_state`, copied from the existing owner result. The existing entry public signature is unchanged.

Project Services independently verifies an asserted input. Absent optional input retains legacy behavior. Present missing, malformed or extra fields fail closed. Asserted input outside an admitted typed semantic gate context fails closed. Natural-text-only input, non-admitted replies, confirmation/commitment, other selected flows and legacy calls remain outside activation.

## Placement and authority

`prepare_unified_human_interface_project_context` retains existing precedence, flow, clarification and immutable-predecessor validation. It forwards asserted input only to `_objective_commitment_gate_project_context`.

Inside the gate, after existing clarification validation and before result hashing/persistence:

1. Validate snapshot, request/turn lineage and owner-store currentness.
2. Invoke existing `discover_candidate_capabilities` with `structured_requirement_state`.
3. Invoke existing `project_knowledge_context_from_workspace` with that discovery and `general_project_goal`.
4. Attach provenance metadata to the existing knowledge projection.
5. Hash the existing enclosing context, validate the resulting projection and recheck currentness, then use existing immutable persistence.

Structured mode does not compute or reuse a cached legacy contextual-task mapping. Legacy mode retains the original mapping path.

No router invocation, selection, rescoring or selected-flow replacement is introduced. Objective readiness, clarification, candidate confirmation and Commitment meaning remain unchanged. No Objective inference, admission, Governance, reuse proof, planning or execution result is supplied by inspection.

## Identity and revision rules

- Original request: existing precedence `request_identity`/`request_hash`, matching the flow binding and immutable Human Intent predecessor.
- Current turn: existing source-turn identity/digest, recomputed from current text using the existing source-turn owner and proposal's expected pre-transition revision; matches proposal, commit and flow.
- Continuation: existing `OWNER_BOUND_CLARIFICATION_CONTINUATION` reference/hash, exact session/conversation/owner and expected pre-transition revision. A changed current turn requires this predecessor.
- Pre-transition revision: proposal `expected_cwm_revision` and `expected_semantic_revision`, cross-checked with commit source revisions.
- Post-transition/consumed revision: final validated owner state, exactly matching flow and readiness evidence. The immediate proposal commit target is only a lower bound; G60/G66 assertion/reduction may advance further.
- Consumed snapshot: existing conversation/workspace/session identities, final global/semantic revisions, intrinsic checksum and complete-state replay hash.

Do not equate original request and current-turn hashes. Do not derive consumed revision as pre-transition revision plus one. No second request identity is created.

## Integrity and currentness

Use the existing closed CWM validator with expected workspace and existing production conversation session. Require ACTIVE and unexpired at the enclosing turn's canonical `created_at`. Cross-check flow `cwm_revision`/`cwm_state_hash`, proposal/commit/validation hashes and admitted dispositions, and existing readiness report identities/revisions/checksum/state digest/evaluation time.

Read, never recover, the existing store with `load_conversation_working_memory_state_v2`:

- root: `runtime_root / production_conversation_cwm`;
- workspace: existing expected workspace;
- session: existing `session_id + :production-conversation-v1`;
- observation: enclosing turn `created_at`.

The loaded state must exactly equal the validated supplied snapshot. Check before discovery and again immediately before context persistence. Drift, missing state, expiration or substitution rejects. No refresh, recovery, cleanup, new lock/lease or new store. These are point-in-time observations, not perpetual freshness guarantees.

## Result and validation

Existing result path:
`context.knowledge_reuse.candidate_capability_discovery.structured_relevance`.

Only sibling metadata is added at `context.knowledge_reuse.continuation_d2_binding`:

- original request identity/hash;
- source-turn identity/digest;
- continuation predecessor references/hashes;
- pre-transition global/semantic revisions;
- post-transition and semantic revisions;
- snapshot checksum/replay hash;
- observed time and flow-binding hash;
- D2 relevance hash;
- inspection_only=true, authority_effect=NONE, c4_status=UNBOUND;
- canonical deterministic binding_hash.

Metadata is reconstructed and compared exactly, closing the schema. The enclosing context hash covers the full result. D1 immutable candidates, parent admissions and D2 closed artifact remain unchanged.

`validate_continuation_d2_inspection_context(context)` checks historical integrity using existing immutable owner references, source bindings, D2 recomputation, exact knowledge projection, gate projection, authority-negative fields and complete context hash. It does not load or refresh the CWM store. Historical integrity is not a currentness claim; existing D2 evidence revalidation still applies.

`validate_continuation_d2_inspection_context(context, runtime_root=...)` additionally checks owner-store currentness. Validation during production persistence always uses this live mode. Rehashed metadata, authority, clarification or knowledge promotions reject.

## Failure semantics

| Input | Result |
|---|---|
| No asserted structured input | Existing legacy behavior |
| Asserted missing/malformed/unsupported input or activation context | FAIL CLOSED |
| Checksum/digest/identity/lineage mismatch | FAIL CLOSED |
| Stale, substituted, absent or expired current owner state | FAIL CLOSED |
| Valid insufficient semantic state | QUERY_INSUFFICIENT |
| Partial query-eligible state | D2 inspection with unresolved evidence retained |
| Unsupported relation | UNKNOWN / UNKNOWN_RELEVANCE; never capability absence |

No broken asserted binding silently downgrades to legacy mode.

## Acceptance and mutation budget

B1 automatic owner snapshot; B2 deterministic same request/snapshot/evidence/observation; B3 semantic revision changes binding; B4 checksum/digest tamper rejection; B5 request/conversation/session substitution rejection; B6 query insufficiency; B7 partial evidence; B8 legacy preservation; B9 authority promotion rejection; B10 independent certificate remains C4 UNBOUND; B11 unchanged G20/G63/G47 regressions; B12 existing store/discovery/identity.

C1 changed CWM without rerouting; C2 final post-transition consumption; C3 original/current identities distinct; C4 no pre+1 assumption; C5 store drift/substitution/expiration rejection; C6 existing result attachment; C7 identical gate authority/clarification/readiness fields; C8 same selection; C9 rehashed lineage/snapshot/result rejection; C10 deterministic reevaluation without re-admitting a turn.

Additional cases: unsupported schema/context, missing asserted state, malformed predecessor, state advance during projection, and confirmation/commitment preservation.

CO authorizes only the existing handoff block of `_run_human_interface_runtime_entry_owner_execution_v1` and Project Services `prepare_unified_human_interface_project_context`, `_objective_commitment_gate_project_context`, `_bind_continuation_d2_inspection`, `validate_continuation_d2_inspection_context`. Existing router, Platform Knowledge, CWM and semantic owners, registries and regression test files remain unchanged.

The other authorized paths are `tests/test_continuation_d2_inspection_binding_v1.py`, this contract, and `STEP78CN_CONTINUATION_SAFE_D2_BINDING_IMPLEMENTATION_CLOSURE_G48.md`.

## Limitations

No independent certification, generalized natural-language semantic admission, mandatory workflow discovery, operational scope algebra, D3–D6, F0 continuation or E05 execution. Existing inspection-only authority and C4 UNBOUND remain. Automatic typed input delivery establishes neither F0 coverage nor certified reuse.

## Corrected owner-function locator

The producer-to-Project-Services handoff is in `human_interface_runtime_entry_service.py::_run_human_interface_runtime_entry_owner_execution_v1`. STEP78CO explicitly corrects CM's attribution to the public wrapper. Only the existing internal handoff block is authorized; the public wrapper, other internal branches, and all binding semantics remain unchanged. No additional file or authority path is introduced.
