# G30-06 In-Session Opaque Artifact Attachment and Continuation

Status: implemented and bounded.

## Purpose

G30-06 removes the final G30-05 terminal UX limitation. A user can now attach
one opaque canonical artifact reference to the current Generation 29
clarification without closing or restarting the AiCLI process.

No Platform Core, G29, G28, Replay, Governance, Query Router, or presentation
responsibility changed.

## Attachment command

The reference Human Interface accepts:

```text
/attach <opaque-canonical-artifact-reference>
```

AiCLI accepts this command only while it holds an active Platform Core
clarification. It does not open the path, inspect a wrapper, classify an
artifact type, select a capability, interpret a semantic slot, or authorize an
invocation. It transports the exact opaque reference with a fixed
continuation message to existing Project Services.

Platform Core validates the active clarification envelope and passes the
reference through existing G29-08 ingress.

## Operational lifecycle

```text
user request
  -> AiCLI
  -> Platform Core
  -> G29 clarification
  -> /attach opaque-reference
  -> existing clarification owner/session validation
  -> G29-08 explicit canonical artifact ingress
  -> G29-06 canonical input binding
  -> Platform Knowledge
  -> G29-04 invocation lifecycle
  -> unchanged G28 certified invocation
  -> Canonical Platform Presentation
  -> Replay reconstruction
```

The attachment is a continuation of the active operational turn. It is not a
new route or lifecycle stage.

## Clarification continuity

The completion preserves:

- G29 clarification owner;
- `input_artifact_family` semantic slot;
- runtime identity;
- session identity;
- originating Project Objective and hash;
- originating route and clarification hashes;
- parent operational turn reference;
- governed work type and mutation boundary.

Project Objective inference is not restarted. The continuation is identical to
the certified G30-05 resumed-session path after the reference reaches Platform
Core.

## Replay continuity

The operational completion turn now records:

- that an in-session opaque attachment was bound;
- G29-08 Replay reference;
- ingress resolution hash and status;
- originating clarification-envelope hash;
- continuation G29-06 route reference and hash.

Reconstruction delegates to existing ingress and route reconstruction. It
verifies the attachment session, ingress resolution hash, ingress status, and
downstream route hash before accepting the operational turn.

This detects attachment substitution, session mismatch, stale clarification
lineage, route tampering, and clarification-owner substitution.

## Fail-closed behavior

AiCLI rejects attachment transport when there is no active clarification,
after cancellation, or after completion. A second attachment after successful
completion is rejected because the clarification is no longer active.

Platform Core and G29-08 fail closed for missing, tampered, unsupported, or
otherwise invalid references. No Provider, Worker, capability invocation, or
repository mutation is reached on ingress failure.

Stale, cross-session, owner-substituted, or Replay-tampered continuations are
rejected by existing Platform Core and Replay validation.

## Human Interface neutrality

AiCLI remains limited to:

- recognizing the transport command;
- checking that a locally pending Platform Core clarification exists;
- forwarding the opaque reference;
- rendering the returned Platform Core result.

All semantic and validation authority remains downstream. The attachment
command does not grant AiCLI artifact discovery, artifact validation,
capability selection, invocation, or execution authority.

## Terminal workflow

A normal interactive session uses:

```text
aicli> Analyze Platform Capability Composition Coverage.
Audit only.
/send

Clarification required before governed execution.

aicli> /attach /allowed/root/000_composition_coverage_request_recorded.json

presentation_status: PRESENTATION_READY
provider_invoked: False
worker_invoked: False
repository_mutated: False
```

The clarification and attachment occur within one AiCLI process and one
session identity.

## Validation evidence

Deterministic validation completed on 2026-07-15:

- focused G30-06 positive, negative, neutrality, and Replay tests: 11 passed;
- all implemented Generation 30 regression tests: 26 passed;
- G29 and G28 regression tests: 73 passed;
- selected Human Interface, Replay, and Governance tests: 35 passed;
- full repository suite: 6,155 passed and 4 skipped;
- `py_compile` and `git diff --check`: passed.

The read-only governance conformance engine remains
`PARTIALLY_CONFORMANT`: 18 checks pass, two pre-existing hook-conformance
checks fail, and there are no critical violations. G30-06 does not alter or
conceal that known hook drift.

## Remaining limitations

- One active clarification accepts one opaque attachment command.
- The referenced canonical artifact must already exist inside a G29-08 allowed
  root as an immutable Replay wrapper.
- AiCLI intentionally provides no artifact browsing or discovery.
- A failed ingress closes with a governed fail-closed result; it does not
  silently replace or repair the supplied artifact.

These are constitutional constraints rather than missing semantic runtime
capabilities.
