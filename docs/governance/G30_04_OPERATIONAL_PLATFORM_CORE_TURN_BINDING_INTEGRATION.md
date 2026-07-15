# G30-04 Operational Platform Core Turn Binding Integration

Status: implemented and bounded.

## Purpose

G30-04 binds Human Interface turns to existing Platform Core owners without
creating a classifier, selector, router, clarification subsystem, registry, or
execution authority. It closes the operational boundary identified by G30-03.

Generation 29 remains unchanged and constitutionally certified.

## Canonical turn envelope

Each AiCLI submission produces one immutable
`PLATFORM_CORE_OPERATIONAL_TURN_BINDING_ARTIFACT_V1`. The envelope records:

- session and user-turn identity;
- the existing Platform Query Router response and hash for new turns;
- selected service and query class;
- the bounded binding destination;
- clarification owner, semantic slot, and origin for replies;
- downstream G29 route reference and hash where applicable;
- explicit Human Interface, Worker, Provider, and mutation boundary flags.

The envelope is owned and validated by Platform Core. AiCLI transports and
renders it but does not inspect it to make semantic decisions.

## Informational routing

New turns first invoke the existing Platform Query Router. Pure informational
turns bind directly to the router-selected read-only service and existing
Canonical Platform Presentation.

Governed action evidence, an explicit governed work type, explicit canonical
artifact transport, or the existing governed-development route binds the turn
to the existing Project Services workflow. This preserves implementation
summary and approval behavior as well as governed read-only G29 routing.

The integration does not duplicate Query Router scoring or classification.

## Clarification ownership and semantic-slot continuity

When G29 returns a clarification, Platform Core creates an immutable
`PLATFORM_CORE_OPERATIONAL_CLARIFICATION_ENVELOPE_V1` containing:

- `clarification_owner`;
- `clarification_runtime_identity`;
- canonical `semantic_slot`;
- originating Project Objective artifact and hash;
- G29 route, selection, and clarification references and hashes;
- work-type boundary metadata;
- session identity and parent-envelope lineage.

AiCLI copies this envelope opaquely into the pending clarification state.
Project Services validates it before accepting a reply. A reply is returned to
the originating G29 route using the original Project Objective; Project
Objective inference is not restarted. Canonical slot metadata takes precedence
over question-text inference.

Generic Platform Core clarification continues to use its existing lifecycle.

The binding also preserves the existing Project Services handling for vague
development or reuse-oriented statements. It uses existing clarification
signals and Query Router evidence; it does not add a competing intent
classifier.

## Replay

Operational-turn Replay reconstructs:

```text
user turn
  -> existing Query Router classification
  -> selected operational binding
```

and:

```text
G29 clarification
  -> opaque Human Interface projection
  -> user reply
  -> owner-specific G29 continuation
```

Reconstruction validates artifact hashes, session identity, owner identity,
semantic-slot identity, origin-turn lineage, G29 route reconstruction, and
continuation-route hashes. Owner substitution, slot substitution, stale reply
lineage, cross-session use, and route tampering fail closed.

## Authority boundaries

- Platform Query Router remains classification authority.
- Project Services owns operational binding and workspace continuity.
- G29-02 remains semantic-selection and clarification-semantics owner.
- G29-06 remains runtime-route owner.
- AiCLI remains presentation and opaque transport only.
- Human approval remains required for implementation.
- No Worker or Provider is invoked by turn binding.
- No repository mutation, governance mutation, or Replay mutation authority is
  introduced.

## Scope boundary

G30-04 is an integration of certified responsibilities. It does not make
natural-language clarification answers into canonical input artifacts. When
G29 requires an explicit compatible canonical artifact, that requirement
continues to fail closed until the artifact is supplied through G29-08 ingress.

## Validation and certification evidence

Deterministic validation completed on 2026-07-15:

- focused G30-04 routing, continuation, tamper, and authority tests: 8 passed;
- Project Services, Query Router, G28, G29, Human Interface Replay, and G30-04
  regression selection: 94 passed;
- governance conformance tests: 5 passed;
- full repository suite: 6,141 passed and 4 skipped;
- `py_compile` and `git diff --check`: passed.

The read-only governance conformance engine remains
`PARTIALLY_CONFORMANT`: 18 checks pass, two pre-existing hook-conformance
checks fail, and there are no critical violations. G30-04 does not conceal or
modify that known hook drift.

## Reusable integration pattern

Future operational bindings should reuse this sequence:

1. invoke the existing Platform Query Router for a new user turn;
2. persist its immutable response and hash in the Platform Core turn envelope;
3. bind informational work to the selected read-only service or governed work
   to existing Project Services;
4. when an existing owner asks for clarification, preserve owner, semantic
   slot, origin, runtime identity, work type, and artifact lineage opaquely;
5. validate the envelope before returning the reply to that owner;
6. reconstruct both the initial route and continuation route from Replay.

This is an integration contract, not a new lifecycle or semantic authority.
