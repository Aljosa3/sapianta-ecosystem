# AIGOL_OCS_CONTEXT_ASSEMBLY_MODEL_V1

## Status

Contract model.

## Purpose

OCS context assembly deterministically gathers, normalizes, hashes, and exposes
the context needed for bounded cognition output.

Context assembly is not execution and not authorization.

## Assembly Inputs

Context assembly may consume accepted inputs from:

- conversation memory;
- replay-derived evidence;
- domain registry and domain artifacts;
- approval evidence;
- provider policy and proposal artifacts;
- worker lifecycle artifacts;
- governance limitation and gap artifacts.

Every accepted input must have:

- source category;
- artifact path or stable artifact id;
- artifact type where available;
- source hash where available;
- read rationale;
- authority classification;
- known limitation notes.

## Normalization Rules

Context assembly must normalize inputs by:

- using stable source categories;
- sorting accepted references deterministically;
- preserving artifact paths and ids rather than copying unrestricted content;
- summarizing only from replay-visible or governance-visible material;
- retaining known gaps and limitation statements;
- marking rejected or unavailable sources explicitly;
- computing a context hash from normalized references and selected summaries.

## Proposed Artifact Shape

A future runtime artifact should use this contract shape:

```text
OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1
```

Required fields:

- `artifact_type`;
- `contract_version`;
- `context_id`;
- `source_request_reference`;
- `source_chain_id`;
- `input_categories`;
- `accepted_inputs`;
- `rejected_inputs`;
- `context_sections`;
- `normalization_policy`;
- `known_gaps`;
- `context_hash`;
- `authority_flags`;
- `replay_visibility`;
- `created_at`;
- `terminal_status`.

`authority_flags` must explicitly state:

- `authorizes_execution: false`;
- `authorizes_dispatch: false`;
- `authorizes_worker_invocation: false`;
- `authorizes_provider_invocation: false`;
- `authorizes_governance_mutation: false`;
- `authorizes_replay_mutation: false`.

## Context Sections

Canonical sections:

- `conversation_context`;
- `replay_context`;
- `domain_context`;
- `approval_context`;
- `provider_context`;
- `worker_context`;
- `governance_context`;
- `known_gap_context`;
- `operator_clarification_context`.

Empty sections must be recorded as empty with rationale, not silently omitted.

## Replay Visibility

The assembled context must be replay-visible through:

- explicit source references;
- deterministic source hashes where available;
- context hash;
- rejected source list;
- normalization policy;
- known gap preservation.

Replay reconstruction must be able to prove what OCS saw and what OCS did not
see without requiring hidden provider state or hidden memory.

## Fail-Closed Conditions

Context assembly must fail closed when:

- mandatory source class cannot be resolved;
- source hash is missing where required;
- source hash mismatch occurs;
- source category is not allowed by the input model;
- required known-gap context would be dropped;
- forbidden authority appears in context;
- context cannot be reconstructed deterministically.
