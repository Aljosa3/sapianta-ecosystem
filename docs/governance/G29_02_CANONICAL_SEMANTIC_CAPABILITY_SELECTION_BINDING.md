# G29-02 — Canonical Semantic Capability Selection Binding

Status: IMPLEMENTED AND DETERMINISTICALLY VERIFIED

Date: 2026-07-13

## Purpose

G29-02 implements one bounded Platform Core transition:

`validated Project Objective -> one G28-eligible capability or one clarification`

The binding performs semantic selection only. It does not invoke the selected
capability, authorize execution, or change the behavior of Project Objective,
Platform Knowledge, the Capability Certification Registry, or the Generation
28 invocation boundary.

## Runtime and Artifact

- runtime: `aigol/runtime/semantic_capability_selection_runtime.py`
- canonical artifact: `SEMANTIC_CAPABILITY_SELECTION_ARTIFACT_V1`
- capability: `CANONICAL_SEMANTIC_CAPABILITY_SELECTION_BINDING`
- successful status: `CAPABILITY_SELECTED`
- ambiguity status: `CAPABILITY_CLARIFICATION_REQUIRED`
- unavailable status: `NO_ADMISSIBLE_CAPABILITY`
- invalid-evidence status: `FAILED_CLOSED`

The public entry point is `select_semantic_capability(...)`.

## Inputs

The binding requires:

- a hash-valid and sufficient Project Objective artifact;
- its explicit reference and artifact hash;
- an immutable certification registry snapshot and fingerprint;
- immutable G28 adapter metadata and fingerprint;
- an ordered set of available canonical input artifact types;
- deterministic selection and session identifiers;
- an explicit Replay destination.

Candidate-discovery evidence is optional because older valid Project Objective
artifacts may not expose a separate discovery reference. When supplied, its
identity, hash, boundary flags, and candidate lineage are validated.

## Bounded Semantic Descriptors

Immutable semantic descriptors are colocated with the existing G28 adapter
metadata in
`aigol/runtime/certified_capability_invocation_binding_runtime.py`.

Initial scope is exactly:

- `PLATFORM_CHANGE_NORMALIZATION`;
- `PLATFORM_CHANGE_IMPACT_ANALYSIS`;
- `PLATFORM_VALIDATION_PLANNING`.

Each descriptor records objective terms, supported actions, supported subjects,
expected outcomes, excluded meanings, supported work types, required semantic
slots, clarification labels, accepted input artifact types, and required G28
input fields. Each descriptor is independently hashed.

The selection runtime does not add another registry and does not inspect or
dynamically import `implementation_owner`.

## Candidate Eligibility

A candidate is admissible only when all of these are true:

1. its certification record is present and hash-valid;
2. its certification status is `CERTIFIED` or `VERIFIED`;
3. it is not superseded;
4. exact G28 adapter metadata is present and hash-valid;
5. its requested work type is supported;
6. no excluded meaning matches;
7. required action, subject, and input-family semantics are resolved;
8. an accepted canonical input artifact type is available.

Certification and adapter discovery are eligibility evidence, not execution
authorization.

## Deterministic Scoring

The explicit scoring model uses fixed weights for:

- exact capability identifier match;
- objective-term match;
- supported-action match;
- supported-subject match;
- expected-outcome match;
- accepted canonical input artifact availability.

Candidate construction iterates by canonical identifier and final ordering is
stable by descending score followed by identifier. Identifier ordering is for
evidence presentation only. It is never used to resolve a semantic tie.

A capability is selected only when exactly one admissible candidate has the
unique highest score. Every candidate retains positive match evidence,
exclusion evidence, required slots, unresolved slots, certification lineage,
adapter lineage, and descriptor lineage.

## Clarification

No supported candidate, a highest-score tie, or unresolved action, subject, or
input-artifact semantics produces a deterministic Platform Core clarification.

The clarification artifact:

- is Platform Core owned;
- asks exactly one highest-value question;
- is hash-bound and Replay-visible;
- records the missing semantic slot and candidate identifiers;
- uses no LLM or probabilistic routing;
- grants no authority to a Human Interface.

Human Interfaces may render the question and collect a response. They may not
rank or select capabilities.

## Replay

A complete selection records six immutable ordered steps:

1. Project Objective source;
2. invocation-eligible candidate set;
3. semantic scoring evidence;
4. selection or ambiguity classification;
5. canonical selection artifact;
6. returned selection result.

Reconstruction verifies wrapper ordering and hashes, objective lineage,
candidate-discovery lineage, registry and adapter fingerprints, descriptor
integrity, reproducible scores, ordered candidates, selected identifier,
clarification linkage, returned-result linkage, and the absence of capability,
Worker, Provider, or mutation execution.

## Generation 28 Handoff

On `CAPABILITY_SELECTED`, the artifact exposes:

- the exact selected capability identifier;
- accepted canonical input artifact types;
- required canonical input fields;
- `ready_for_g28_invocation: true`.

The artifact does not call Generation 28. A later Platform Core caller must
provide the selected identifier and complete canonical input artifacts to the
unchanged G28 binding.

Selection is not authorization.

## Constitutional Boundaries

The G29-02 runtime:

- invokes no capability;
- invokes no Worker or Provider;
- performs no repository mutation;
- performs no dynamic import or arbitrary dispatch;
- creates no new certification registry;
- gives no authority to AiCLI or another Human Interface;
- does not modify Platform Knowledge semantics;
- does not alter Governance, Replay, or Certification authority;
- does not claim full repository conformance while known hook drift remains.

## Validation

Focused validation covers unique selection for all three adapters,
certification and supersession filtering, missing-adapter filtering, invalid
objective and fingerprint rejection, no-candidate behavior, equal-score
ambiguity, missing semantic slots, deterministic clarification, stable ordering,
reproducible scoring, artifact validation, Replay reconstruction, tamper
rejection, registration, and all non-execution boundaries.

