# G3-04 Phase 8 Platform Communication Wrapper Retirement V1

Status: WRAPPER RETIREMENT PLAN COMPLETE

Final verdict: PLATFORM_WRAPPER_RETIREMENT_REQUIRED

## 1. Executive Summary

The Platform Communication Consolidation Audit confirmed that UHCL is the
canonical reusable communication layer and that ACLI must remain an interface
adapter only.

This phase classifies the remaining communication wrappers and defines the
retirement plan required to complete Platform Core communication consolidation.
It does not remove runtime code. It establishes which wrappers must be migrated
to UHCL, which may remain adapter-specific, which should be deprecated, and
which can become removable after parity evidence is captured.

Primary conclusion:

- UHCL is ready to receive all remaining reusable communication paths.
- The remaining wrappers are not all ready for immediate deletion.
- Retirement requires staged migration, command-level parity snapshots, and
  rollback-safe compatibility windows.
- No new communication semantics should be introduced outside UHCL.

## 2. Scope And Non-Goals

Reviewed wrapper families:

- `acli_human_friendly_explanation_runtime.py`;
- `acli_llm_assisted_explanation_runtime.py`;
- `acli_proposal_approval_bridge.py`;
- `acli_authorization_bridge.py`;
- remaining operator rendering compatibility fields;
- Provider summary wrappers;
- Worker summary wrappers;
- Product 1 summary wrappers;
- Governance to Human wording wrappers;
- Replay summary wording wrappers.

This phase does not:

- change runtime behavior;
- delete wrapper code;
- invoke providers;
- execute workers;
- create approval or authorization;
- mutate replay;
- mutate governance;
- introduce interface-specific communication semantics.

## 3. Wrapper Inventory

| Wrapper / surface | Current role | Decision | Retirement condition |
| --- | --- | --- | --- |
| `acli_human_friendly_explanation_runtime.py` | Legacy reusable ACLI explanation wording | migrate to UHCL, then deprecate | UHCL progressive explanation artifacts produce equivalent output for all current callers. |
| `acli_llm_assisted_explanation_runtime.py` | Legacy advisory explanation path with LLM/provider boundary concerns | migrate to UHCL evidence consumption, then retain only if needed as compatibility | Advisory explanation must become source evidence for UHCL, not a parallel communication owner. |
| `acli_proposal_approval_bridge.py` | Proposal and approval communication plus bridge evidence | migrate communication to UHCL; retain bridge authority/evidence boundaries | Proposal/approval rendering consumes UHCL typed sections and shared confirmation while approval authority remains external. |
| `acli_authorization_bridge.py` | Authorization communication plus bridge evidence | migrate communication to UHCL; retain authorization evidence boundaries | Authorization rendering consumes UHCL evidence-bound sections and recovery guidance while authorization authority remains external. |
| `acli_operator_rendering_and_confirmation.py` | Phase 6 migrated UHCL consumer with legacy fields | retain as adapter-specific compatibility wrapper | Legacy reusable confirmation fields are retired after callers consume canonical UHCL response classes. |
| `acli_uhcl_adapter_rendering.py` | UHCL terminal adapter | retain as adapter-specific | Permanent ACLI presentation surface; not a wrapper to remove. |
| Provider proposal and diagnostic summaries | Provider-facing human summaries and proposal text | migrate to UHCL Provider bindings | Provider cognition/provenance summaries consume UHCL binding artifacts. |
| Provider-assisted conversation/classification | Legacy compatibility communication and classification | deprecate or retain compatibility-only | Must not define canonical meaning; retire after UBTR/UHCL and OCS paths cover callers. |
| Worker lifecycle and execution summaries | Worker-facing human summaries | migrate to UHCL Worker bindings | Worker execution/lifecycle summaries consume UHCL binding artifacts. |
| Product 1 workflow summaries | Product-facing workflow communication | migrate to UHCL Product 1 workflow bindings | Product 1 interfaces consume UHCL Product 1 workflow summary artifacts. |
| Product 1 decision packet summaries | Decision packet human summaries | migrate to UHCL Product 1 decision packet bindings | Decision packet communication consumes UHCL binding artifacts. |
| Product 1 audit packet summaries | Audit packet human summaries | migrate to UHCL Product 1 audit packet bindings | Audit packet communication consumes UHCL binding artifacts. |
| Governance to Human translation runtime | Historical governance wording surface | migrate wording to UHCL, retain source evidence if needed | Governance remains authority/source evidence; human wording comes from UHCL. |
| Replay summary command | Operator-facing replay summary rendering | migrate human wording to UHCL transparency/explanation sections | Replay reconstruction remains authoritative; human replay summaries consume UHCL. |

## 4. Migration Decisions

### 4.1 Retain As Adapter-Specific

Retain:

- `acli_uhcl_adapter_rendering.py`;
- ACLI terminal card formatting;
- ACLI raw input capture;
- ACLI communication level selection;
- ACLI command transport and terminal ergonomics.

These are presentation responsibilities, not reusable communication semantics.

### 4.2 Migrate To UHCL

Migrate:

- human-friendly explanation wording;
- LLM-assisted/advisory explanation output;
- proposal communication;
- approval communication;
- authorization communication;
- provider summaries;
- worker summaries;
- Product 1 summaries;
- governance human-facing wording;
- replay human-facing summaries.

Migration target:

- UHCL typed communication sections;
- UHCL progressive explanation derivation;
- UHCL shared confirmation model;
- UHCL source evidence binding;
- UHCL Provider/Worker/Product communication bindings;
- UHCL recovery guidance.

### 4.3 Deprecate

Deprecate after UHCL parity snapshots:

- ACLI-owned reusable explanation generation;
- ACLI-owned reusable confirmation wording/classification fields;
- ACLI-owned proposal, approval, and authorization wording;
- provider-assisted communication surfaces that bypass UHCL;
- governance or replay wording that duplicates UHCL sections.

### 4.4 Remove

Remove only after all of the following are true:

1. equivalent UHCL artifacts are created for each wrapper output family;
2. old-vs-new deterministic parity snapshots pass;
3. downstream callers consume UHCL artifacts or adapter render artifacts;
4. rollback window is complete;
5. no authority-bearing behavior depends on the wrapper;
6. governance evidence records the retirement decision.

## 5. Retirement Candidates

Immediate retirement candidates: none.

Candidate after migration:

- reusable explanation prose in `acli_human_friendly_explanation_runtime.py`;
- reusable advisory explanation prose in `acli_llm_assisted_explanation_runtime.py`;
- legacy confirmation class fields in `acli_operator_rendering_and_confirmation.py`;
- proposal/approval wording in `acli_proposal_approval_bridge.py`;
- authorization wording in `acli_authorization_bridge.py`;
- replay `rendered_summary` wording when UHCL transparency/explanation rendering
  covers replay summary output;
- governance-to-human wording when UHCL governance explanation sections cover
  current callers.

Not retirement candidates:

- approval authority;
- authorization authority;
- governance conformance;
- replay reconstruction;
- CSA artifacts;
- OCS cognition artifacts;
- Provider evidence artifacts;
- Worker evidence artifacts;
- Product 1 workflow, decision packet, and audit packet evidence;
- ACLI terminal rendering and input capture.

## 6. Compatibility Strategy

Compatibility must be staged and fail-closed.

For each wrapper:

1. add UHCL artifact creation or UHCL artifact consumption beside the legacy
   output;
2. record source evidence hash, UHCL artifact hash, render artifact hash, and
   rollback reference;
3. preserve legacy fields for callers during the compatibility window;
4. capture parity snapshots for representative command outputs;
5. switch callers to UHCL artifacts or adapter render artifacts;
6. mark legacy fields deprecated;
7. remove legacy communication wording only after parity certification.

Compatibility wrappers must remain explicit. No wrapper may silently continue as
the owner of reusable communication meaning.

## 7. Replay Impact

Replay impact is additive during migration.

Each migrated wrapper should record:

- source evidence reference;
- source evidence hash;
- UHCL artifact reference;
- UHCL artifact hash;
- adapter render artifact reference where applicable;
- adapter render artifact hash where applicable;
- legacy wrapper reference;
- legacy wrapper hash;
- parity snapshot hash;
- rollback reference.

Replay reconstruction authority remains in Replay. UHCL provides human-facing
communication artifacts and does not replace replay reconstruction.

## 8. Governance Impact

Governance impact is bounded.

This retirement plan preserves:

- UBTR/UHCL communication ownership;
- governance authority separation;
- approval authority separation;
- authorization authority separation;
- provider and worker execution boundaries;
- replay continuity;
- compatibility rollback;
- explicit known-gap visibility.

This plan forbids:

- ACLI-owned reusable communication semantics;
- provider-owned human communication semantics;
- worker-owned human communication semantics;
- Product 1-owned platform communication semantics;
- replay-breaking wrapper deletion;
- approval or authorization creation through communication rendering.

## 9. Certification Impact

Certification requires wrapper-by-wrapper evidence.

Certification criteria:

- no new communication semantics outside UHCL;
- all migrated wrappers consume UHCL artifacts or produce source evidence for
  UHCL;
- all adapter output remains presentation-only;
- all parity snapshots pass;
- all rollback references are recorded;
- approval and authorization remain external authorities;
- provider and worker layers remain source evidence producers;
- Product 1 remains a platform consumer, not communication owner.

Until these criteria are met for every wrapper family, wrapper retirement is not
complete.

## 10. Rollback Strategy

Rollback must remain simple and evidence-preserving.

Rollback pattern:

1. keep legacy wrapper output during the migration window;
2. record UHCL output separately from legacy wrapper output;
3. switch callers through a bounded migration flag or explicit command wiring;
4. if parity fails, revert the caller to the legacy wrapper while preserving UHCL
   artifacts for analysis;
5. do not mutate existing replay evidence;
6. do not remove wrapper code until rollback window closes.

Rollback must not revoke approval, revoke authorization, invoke providers,
execute workers, mutate governance, mutate replay, deploy, or mutate repository
state.

## 11. Next Implementation Batch

Recommended next batch:

`G3_04_PHASE_8A_ACLI_EXPLANATION_WRAPPER_UHCL_MIGRATION_V1`

Scope:

- migrate `acli_human_friendly_explanation_runtime.py` to UHCL progressive
  explanation artifacts;
- migrate admissible `acli_llm_assisted_explanation_runtime.py` output to UHCL
  evidence consumption;
- preserve provider/LLM non-authority notices;
- capture old-vs-new explanation parity snapshots;
- keep ACLI rendering adapter-specific;
- do not remove wrapper code until parity is certified.

Follow-on batches:

1. `G3_04_PHASE_8B_PROPOSAL_APPROVAL_AUTHORIZATION_UHCL_MIGRATION_V1`;
2. `G3_04_PHASE_8C_PROVIDER_WORKER_PRODUCT_SUMMARY_UHCL_MIGRATION_V1`;
3. `G3_04_PHASE_8D_GOVERNANCE_REPLAY_SUMMARY_UHCL_MIGRATION_V1`;
4. `G3_04_PHASE_8E_COMPATIBILITY_WRAPPER_RETIREMENT_CERTIFICATION_V1`.

## 12. Final Determination

The wrapper inventory is complete and the retirement path is defined. The
remaining wrappers are not ready for immediate removal because parity snapshots
and command-level UHCL migration have not yet been completed for every wrapper
family.

Final verdict: PLATFORM_WRAPPER_RETIREMENT_REQUIRED
