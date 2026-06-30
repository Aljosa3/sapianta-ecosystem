# G3-04 Phase 6 ACLI Command UHCL Consumption Migration V1

Status: STAGED ACLI COMMAND MIGRATION IMPLEMENTED

Final verdict: G3_04_PHASE_6_READY

## 1. Executive Summary

This phase begins the ACLI command migration from legacy ACLI-owned
communication paths to certified UHCL consumption.

The first migrated command surface is the canonical ACLI operator
rendering-and-confirmation path. This surface is the shared command-facing
communication wrapper used by ACLI conversational development flows to render
operator state and classify terminal input.

The migration preserves legacy fields and replay compatibility while adding
UHCL source artifact consumption, ACLI UHCL adapter rendering, and canonical
UHCL response-class capture.

Primary conclusion:

- ACLI operator response rendering now consumes UHCL typed communication
  sections before terminal presentation.
- ACLI operator confirmation classification now consumes the UHCL shared
  confirmation model before terminal input capture.
- ACLI still records legacy compatibility fields for existing callers.
- Unknown legacy confirmation input remains a compatibility wrapper and fails
  closed for canonical UHCL response capture.
- No provider, worker, governance, replay, approval, authorization, execution,
  deployment, or repository mutation authority is introduced.

## 2. Files Changed

Runtime:

- `aigol/runtime/acli_operator_rendering_and_confirmation.py`

Tests:

- `tests/test_acli_operator_rendering_and_confirmation_v1.py`

Documentation:

- `docs/governance/G3_04_PHASE_6_ACLI_COMMAND_UHCL_CONSUMPTION_MIGRATION_V1.md`

## 3. Commands Migrated

### 3.1 ACLI Operator Response Rendering

Migrated function:

- `render_operator_response(...)`

Migration behavior:

1. Existing ACLI conversation artifact is validated.
2. Existing deterministic ACLI summary is preserved for compatibility.
3. A UHCL typed explanation section is created from the conversation and CSA
   evidence.
4. The ACLI UHCL adapter renders that UHCL artifact as terminal presentation.
5. Legacy ACLI rendering artifact records `uhcl_consumption` evidence with
   source artifact hash, render artifact hash, replay references, and
   presentation-only flags.

ACLI role after migration:

- terminal presentation adapter;
- compatibility wrapper;
- render evidence recorder.

ACLI does not generate reusable explanation meaning.

### 3.2 ACLI Operator Confirmation Classification

Migrated function:

- `classify_operator_confirmation(...)`

Migration behavior:

1. Existing ACLI conversation artifact is validated.
2. Existing legacy confirmation classification is preserved for compatibility.
3. A UHCL shared confirmation model is created from conversation and CSA
   evidence.
4. The ACLI UHCL adapter renders the confirmation artifact.
5. Supported terminal input is captured as a canonical UHCL response class:
   `CONFIRMATION`, `CLARIFICATION`, `MODIFICATION`, `REJECTION`, or
   `CONTINUATION`.
6. Legacy `unknown` input remains compatibility-only and records
   `COMPATIBILITY_UNKNOWN_INPUT_FAILED_CLOSED` instead of inventing a UHCL
   response class.

ACLI role after migration:

- terminal input capture;
- mapping raw input to canonical UHCL response classes where supported;
- compatibility preservation for legacy unknown input.

ACLI does not own confirmation semantics.

## 4. Remaining Compatibility Wrappers

The following ACLI communication surfaces remain compatibility wrappers after
this phase:

- `aigol/runtime/acli_human_friendly_explanation_runtime.py`;
- `aigol/runtime/acli_llm_assisted_explanation_runtime.py`;
- `aigol/runtime/acli_proposal_approval_bridge.py`;
- `aigol/runtime/acli_authorization_bridge.py`;
- command-specific renderers that have not yet been wired to UHCL artifacts.

They remain valid only as transitional wrappers. They must not be treated as
canonical owners of reusable communication meaning.

## 5. Migration Evidence

Every migrated operator rendering artifact now records:

- `uhcl_command_migration_version`;
- command surface;
- ACLI role;
- legacy wrapper retention;
- UHCL source artifact type;
- UHCL source artifact hash;
- UHCL source replay reference;
- UHCL render artifact hash;
- UHCL render replay reference;
- no semantic translation by ACLI;
- no explanation generation by ACLI;
- no confirmation logic by ACLI;
- no provider or worker orchestration;
- no governance performed by ACLI;
- no replay ownership by ACLI.

Every migrated confirmation artifact additionally records:

- canonical UHCL response class when supported;
- canonical UHCL response class set;
- UHCL response artifact hash when captured;
- UHCL response replay reference when captured;
- compatibility fail-closed status for unknown input.

## 6. Replay Impact

Replay remains append-only and compatibility-preserving.

Legacy ACLI top-level replay artifacts are unchanged in shape for existing
callers, but they now include UHCL consumption evidence. UHCL source artifacts,
ACLI UHCL render artifacts, and UHCL response artifacts are stored in
subdirectories under the ACLI replay directory so top-level legacy replay order
remains stable.

Replay reconstruction now reports:

- migrated UHCL consumption status;
- UHCL source artifact hashes;
- legacy render and classification counts;
- existing non-authority flags.

## 7. Governance Impact

Governance impact is bounded and positive.

This phase strengthens the permanent architecture invariant:

```text
UBTR/UHCL owns reusable communication meaning.
ACLI owns terminal presentation only.
```

The migrated path explicitly records that ACLI does not perform semantic
translation, explanation generation, confirmation logic, provider orchestration,
worker orchestration, governance, replay ownership, approval, authorization,
execution, deployment, or repository mutation.

Approval and authorization remain existing Platform Core authorities. Human
confirmation remains evidence only.

## 8. Rollback Impact

Rollback is low risk.

The migration is additive inside the existing ACLI operator rendering and
confirmation compatibility wrapper. Legacy fields remain present. If a downstream
caller cannot yet consume the UHCL migration evidence, it can continue reading
the existing legacy fields.

Rollback consists of removing the UHCL consumption calls and the new
`uhcl_consumption` fields from:

- `aigol/runtime/acli_operator_rendering_and_confirmation.py`;
- `tests/test_acli_operator_rendering_and_confirmation_v1.py`;
- this governance document.

No replay mutation, governance mutation, provider invocation, worker execution,
approval revocation, authorization revocation, deployment rollback, or repository
state migration is required.

## 9. Remaining Migration Work

Remaining ACLI migration batches:

1. migrate ACLI human-friendly explanation wrappers to direct UHCL progressive
   explanation consumption;
2. migrate ACLI LLM-assisted explanation compatibility output to UHCL evidence
   consumption where it remains admissible;
3. migrate proposal and approval command output to UHCL typed sections and shared
   confirmation artifacts;
4. migrate authorization command output to UHCL recovery and evidence-bound
   sections;
5. migrate Provider, Worker, and Product summary commands to UHCL binding
   artifacts;
6. capture command-level old-vs-new parity snapshots before retiring each
   compatibility wrapper.

## 10. Validation Summary

Required validation for this phase:

- `git diff --check`;
- `python -m py_compile aigol/runtime/acli_operator_rendering_and_confirmation.py aigol/runtime/acli_uhcl_adapter_rendering.py`;
- targeted ACLI migration tests;
- full pytest;
- generated `.runtime` cleanup after validation.

## 11. Final Determination

The canonical ACLI operator response rendering and confirmation classification
command surface now consumes UHCL artifacts while preserving compatibility,
replay, and governance boundaries.

This is a staged migration, not final retirement of every legacy ACLI
communication wrapper.

Final verdict: G3_04_PHASE_6_READY
