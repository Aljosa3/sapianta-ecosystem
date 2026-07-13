# G28-02 — Certified Capability Invocation Binding

Status: IMPLEMENTED AND DETERMINISTICALLY VERIFIED

Date: 2026-07-13

## Purpose

G28-02 implements one bounded Platform Core transition:

`validated Platform Knowledge discovery -> allowlisted certified capability invocation`

Platform Knowledge remains a read-only discovery service. The new binding
validates its response, resolves current certification evidence, selects one
static adapter, validates capability-specific inputs, and delegates to the
existing canonical capability owner.

## Runtime

- `aigol/runtime/certified_capability_invocation_binding_runtime.py`
- result artifact: `CERTIFIED_CAPABILITY_INVOCATION_RESULT_ARTIFACT_V1`
- completed status: `CERTIFIED_CAPABILITY_INVOCATION_COMPLETED`
- registry capability: `CERTIFIED_CAPABILITY_INVOCATION_BINDING`

The public entry point is `invoke_certified_capability(...)`.

## Initial Adapter Allowlist

Exactly three read-only Repository Cognition adapters are supported:

| Capability | Existing canonical entry point | Accepted input |
| --- | --- | --- |
| `PLATFORM_CHANGE_NORMALIZATION` | `normalize_platform_change(...)` | `IMPLEMENTATION_MANIFEST_ARTIFACT_V1` or `GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1` |
| `PLATFORM_CHANGE_IMPACT_ANALYSIS` | `analyze_platform_change_impact(...)` | `NORMALIZED_CHANGE_ARTIFACT_V1` |
| `PLATFORM_VALIDATION_PLANNING` | `plan_platform_validation(...)` | `PLATFORM_CHANGE_IMPACT_ARTIFACT_V1` |

The adapter mapping is static and immutable. Certification registry
`implementation_owner` metadata is verified as lineage evidence but is never
imported or executed. A certified capability without an explicit adapter fails
closed.

## Input and Output Binding

The binding requires:

- a hash-valid `PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1`;
- its explicit Replay-visible reference;
- the exact discovered capability identifier;
- a deterministic invocation and session identifier;
- the complete capability-specific input mapping;
- actor, timestamp, and binding Replay directory.

Discovery capability identity, current certification status, supersession,
certification record hash, and implementation owner are rebound to the
certification registry. Input artifact identity, canonical reference,
artifact hash, semantic hash, and prerequisites are verified before the
canonical capability is called.

The capability output is accepted only when its existing validator confirms
the expected artifact type, artifact hash, semantic hash, and successful
non-failed-closed status.

## Replay

Successful invocation records six immutable ordered steps:

1. Platform Knowledge discovery source;
2. certified capability resolution;
3. allowlisted adapter selection;
4. validated capability inputs;
5. capability invocation result;
6. returned binding result.

The selected capability writes its own canonical Replay below the deterministic
`capability_runtime` subdirectory. Binding reconstruction validates wrapper and
artifact hashes, discovery identity, current certification evidence, adapter
metadata, input evidence, output identity, and all cross-step lineage.

Failed invocations preserve the failed result and returned evidence without
claiming capability execution.

## Governance and Authority Boundary

The binding does not:

- treat discovery as authorization;
- grant Human Interface authority;
- dynamically import an implementation owner;
- execute arbitrary Python;
- invoke a Worker or Provider;
- authorize execution, dispatch, or mutation;
- mutate the repository;
- certify results;
- change existing Repository Cognition semantics.

Capabilities requiring approval, Governance authorization, Worker execution,
Provider invocation, or mutation have no G28-02 adapter and therefore fail
closed as unsupported.

## Human Interface Boundary

No AiCLI or other Human Interface code is changed. Human Interfaces remain
responsible only for request transport and later presentation. Capability
resolution and delegation remain Platform Core responsibilities.

## Validation

Focused tests cover successful invocation through all three adapters,
discovery and capability mismatch, uncertified and superseded capability
rejection, missing adapter, input identity/reference/hash failures, unexpected
output rejection, Replay reconstruction and tamper detection, registry
registration, and the absence of Worker, Provider, mutation, Human Interface
authority, and dynamic-import surfaces.

Repository-wide conformance remains subject to the existing visible hook-drift
findings; G28-02 does not reinterpret partial conformance as full conformance.

## Known Limitation

G28-02 does not translate natural-language requests into capability input
artifacts. Callers must supply the existing canonical, hash-bound input
artifact and its exact reference and semantic hash. This preserves the
separation between discovery, evidence construction, and invocation.
