# AIGOL_MINIMAL_CONSTITUTIONAL_MEMORY_V1

## Purpose

Formalize the **constitutional memory** that AiGOL already operates on:
an append-only replay-evidence substrate where every governed cognition
operation, every gate decision, every authorization, every routing
event, every isolation outcome, and every governed return is preserved
as immutable, hash-linked, replay-reconstructable evidence.

This document is **descriptive and constitutive** — it freezes the
memory model that is already implemented. It introduces no new memory
feature, no adaptive memory layer, and no autonomous memory mutation.

## Append-Only Evidence Memory

The minimal constitutional memory is the set of replay-visible evidence
artifacts emitted by the minimal runtime loop. Each artifact is:

- **immutable** — `dataclass(frozen=True)` with construction-time hash
  validation;
- **append-only** — lineage reconstructors reject duplicates,
  non-monotonic orderings, and mutated entries;
- **hash-linked** — every artifact carries a `sha256:`-prefixed
  `evidence_hash`, and every cross-stage reference is by hash
  (`raw_response_evidence_hash`, `extraction_evidence_hash`,
  `proposal_evidence_hash`, `connector_evidence_hash`,
  `usage_validation_evidence_hash`, `activation_evidence_hash`,
  `operator_usage_evidence_hash`, `governed_return_summary` /
  `governed_return_hash`, `cli_evidence_hash`,
  `session_lineage_hash`);
- **canonical** — emitted through canonical JSON serialization
  ([aigol/runtime/transport/serialization.py](../aigol/runtime/transport/serialization.py))
  with sorted keys, compact separators, ASCII-only encoding.

Constitutional memory is **not** a key-value store, not a vector store,
not a database, not a cache, not an embedding index. It is the
evidence chain itself.

## Replay Lineage as Memory Substrate

The lineage reconstructors are the read surface of constitutional
memory:

- `reconstruct_raw_provider_response_lineage`
- `reconstruct_bounded_extraction_lineage`
- `reconstruct_external_llm_proposal_lineage`
- `reconstruct_live_openai_runtime_lineage`
- `reconstruct_real_openai_api_invocation_lineage`
- `reconstruct_translation_lineage`
- `reconstruct_cognition_review_lineage`
- `reconstruct_authorization_lineage`
- `reconstruct_routing_lineage`
- `reconstruct_session_lineage`
- `reconstruct_minimal_governed_execution_lineage`
- `reconstruct_production_isolation_lineage`
- `reconstruct_governed_return_lineage`
- `reconstruct_live_runtime_usage_validation_lineage`
- `reconstruct_real_runtime_activation_lineage`
- `reconstruct_first_real_operator_usage_lineage`
- `reconstruct_runtime_operator_cli_lineage`
- `reconstruct_operator_interaction_loop_lineage`
- `reconstruct_live_cognition_rejection_analysis_lineage`

Each reconstructor:

- accepts a list / tuple of evidence dicts or instances;
- validates that no `*_id` repeats;
- validates that `created_at` is monotonically non-decreasing;
- emits a lineage view with a `lineage_hash`;
- carries `append_only_valid = True`, `lineage_valid = True`,
  `governance_authority_separated = True`.

## Governed Recall

Memory recall is **only** by deterministic lineage reconstruction over
a supplied set of evidence artifacts. There is no probabilistic recall,
no fuzzy recall, no embedding-similarity recall, no learned retrieval.

The rejection analyzer
([aigol/runtime/live_cognition_rejection_analysis.py](../aigol/runtime/live_cognition_rejection_analysis.py))
is the canonical recall surface: given one usage record, it deterministically
re-projects the entire replay-visible decision chain into a single
analysis artifact with its own `evidence_hash`.

## Semantic Continuity

Semantic continuity is preserved across operations because:

- every gate decision references its predecessors by hash;
- bounded proposals carry their `proposal_id`, `proposal_type`,
  `requested_capabilities`, `proposed_contract_reference`, and
  `created_at` verbatim into the contract candidate
  (`translated_contract_candidate.source_proposal_id`, etc.);
- the contract, authorization, routing, execution, isolation, and
  governed return artifacts all carry the `contract_id`,
  `session_id`, `execution_id` linking the loop end-to-end;
- replay reconstruction over the same evidence list always produces
  the same lineage hash, deterministically.

## Authority-Separated Memory Writes

Memory writes are **only** the emission of evidence artifacts by the
defined governance gates. No stage may write memory on behalf of any
other stage. There is no shared mutable memory cell, no global
mutable state, no monkey-patched runtime.

`governance_authority_separated = True` on every evidence artifact
is the formal type-level assertion that the emitter has not
overreached.

## No Adaptive Autonomous Memory Mutation

- No background process modifies memory.
- No stage rewrites prior evidence.
- No learning loop updates memory parameters.
- No probabilistic model updates memory statistics.
- No adaptive policy mutates memory shape.
- No autonomous compaction, eviction, summarization, or rewriting.

The only operation on memory is **append** of a freshly constructed
immutable evidence artifact. Reading memory is **reconstruction** of
a deterministic lineage view from those append-only artifacts.

## Boundary

This document freezes constitutional memory in its current shape.
Memory is the replay-evidence chain. Recall is deterministic
reconstruction. Authority is separated by construction.
The only future memory primitive that may be added is one explicitly
required by an observed operational failure that cannot be diagnosed
or recovered via the existing replay-evidence substrate.
