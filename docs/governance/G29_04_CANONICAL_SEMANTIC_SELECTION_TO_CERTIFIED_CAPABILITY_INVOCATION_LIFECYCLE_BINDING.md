# G29-04 — Canonical Semantic Selection to Certified Capability Invocation Lifecycle Binding

## Responsibility Boundary

G29-04 implements one bounded Platform Core composition:

`validated G29 selection -> explicit Platform Knowledge -> concrete canonical inputs -> unchanged G28 invocation -> canonical presentation`

It does not select capabilities, create capability inputs, certify capabilities,
authorize execution, or replace G28 invocation validation. G29-02 remains the
selection authority and G28-02 remains the sole certified capability invocation
authority.

## Input Contract

The lifecycle requires:

- deterministic invocation and session identifiers;
- a hash-valid `SEMANTIC_CAPABILITY_SELECTION_ARTIFACT_V1`;
- a hash-valid explicit Platform Knowledge response and reference;
- concrete canonical capability inputs using exactly the G29-declared G28 field schema;
- an invoking Platform Core actor and timestamp;
- an explicit Replay destination.

The lifecycle does not create concrete capability inputs from natural language,
Project Objective prose, semantic descriptors, or a capability identifier.

## Validation Sequence

The binding validates the G29 artifact with the existing G29 validator. Only
`CAPABILITY_SELECTED` with one exact admissible candidate,
`invocation_eligible: true`, `clarification_required: false`, and
`ready_for_g28_invocation: true` may continue.

The explicit Platform Knowledge response must identify the same capability.
Concrete inputs must contain exactly the declared fields and an accepted
canonical artifact family. G28 then independently revalidates discovery,
current certification, supersession, the allowlisted adapter, artifact identity,
references, canonical hashes, and semantic hashes.

Clarification, no-candidate, malformed, tampered, and mismatched states fail
closed before G28. G28 failures remain G28 failures and are projected without
being reinterpreted.

## Replay Lineage

The lifecycle records five immutable composition steps:

1. validated semantic-selection handoff;
2. complete G28 invocation request;
3. validated G28 result;
4. canonical presentation;
5. returned lifecycle result.

The composition Replay links G29 selection identity and hash, explicit Platform
Knowledge identity and hash, per-field concrete input hashes, the G28 request
hash, G28 result hash, and presentation hash. Reconstruction verifies ordering,
wrapper and artifact hashes, capability-identifier continuity, request and
result lineage, concrete input evidence, the internal G28 Replay, and final
presentation linkage. It does not duplicate or replace G29 or G28 internal
Replay semantics.

## Presentation Behavior

The existing Canonical Platform Presentation Layer accepts a validated
`CERTIFIED_CAPABILITY_INVOCATION_RESULT_ARTIFACT_V1`. Successful results expose
the selected capability, invocation status, output artifact identity, and
Replay reference. Valid G28 failed-closed results produce a canonical
failed-closed presentation. Malformed results are rejected.

Human Interfaces render this canonical presentation only. They do not rank,
select, bind, invoke, or interpret capabilities.

## Authority Exclusions

The lifecycle:

- grants no Human Interface authority;
- treats neither selection nor discovery as authorization;
- invokes no Worker or Provider;
- authorizes no Worker, Provider, or repository mutation;
- uses no dynamic imports or arbitrary dispatch;
- creates no registry or certification decision;
- does not modify G29 selection or G28 invocation semantics.

Certified read-only Platform capability invocation remains distinct from Worker
execution authorization.

## Runtime Reachability Limitation

G29-04 establishes a callable and certified Platform Core lifecycle boundary.
It does not automatically route natural-language AiCLI requests into capability
invocation because the current router does not necessarily possess the required
concrete canonical input artifacts. Operational AiCLI reachability remains a
separate, explicitly governed validation and integration question.

Repository-wide governance conformance remains subject to the two pre-existing
hook-drift findings. G29-04 does not reinterpret partial conformance as full
conformance.
