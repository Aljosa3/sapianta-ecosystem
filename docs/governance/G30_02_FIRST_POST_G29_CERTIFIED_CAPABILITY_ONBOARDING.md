# G30-02 First Post-G29 Certified Capability Onboarding

Status: implemented bounded capability onboarding.

## Purpose

G30-02 demonstrates that the certified Generation 29 semantic capability
runtime is reusable. It onboards the existing
`PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME`, a deterministic read-only
Platform Core capability outside the platform-change normalization, impact,
and validation-planning chain.

The milestone extends certified metadata and canonical input handling. It does
not add a lifecycle, router, registry, selection algorithm, execution authority,
Provider path, Worker path, or repository-mutation path.

## Selected capability

The selected capability was originally implemented and certified by G20-03.
It deterministically composes existing capability registry, Platform Knowledge,
query-route, generation-certification, Governance, and optional Replay evidence
to report capability coverage and residual gaps.

Its existing implementation remains owned by
`aigol.runtime.platform_capability_composition_coverage`. G30-02 adds its
Generation 29 onboarding evidence to the existing certification record rather
than creating a duplicate capability identity.

## Canonical input contract

`PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1` is the immutable
canonical input family for this binding. It contains:

- an immutable `request_id`;
- the bounded coverage query and its hash;
- creation time;
- a canonical artifact hash;
- explicit read-only, Replay, Human Interface, Provider, Worker, repository,
  Governance, and Replay-mutation boundary declarations.

The validator rejects type, version, status, query-hash, artifact-hash, and
boundary drift. G29-08 additionally validates the enclosing Replay wrapper,
opaque reference, immutable identity, and source stability before exposing the
artifact to semantic selection.

## Onboarding steps

The reusable extension contract exercised by this milestone is:

1. reuse one existing certified capability identity;
2. bind new onboarding documentation into its certification evidence;
3. define one immutable canonical request artifact and validator;
4. add one static allowlisted G28 adapter using the existing canonical entry
   point;
5. add one G29 semantic descriptor without changing scoring or clarification;
6. admit the request family through the existing G29-08 validator dispatch;
7. project the request into the exact G28 capability-input fields in G29-06;
8. validate the existing capability output through its native validator;
9. reuse the existing Canonical Presentation adapter;
10. reconstruct the unchanged nested ingress, selection, lifecycle, G28, and
    presentation Replay chain.

## Runtime composition

Natural-language and artifact evidence enter as separate bounded inputs and
converge only inside Platform Core:

```text
Natural-language request ----> Project Objective ----> G29-02 selection
                                                        |
Opaque wrapper reference ----> G29-08 validation -------+
                                                        |
                                                        v
                                             exact-one artifact binding
                                                        |
                                                        v
                                              Platform Knowledge
                                                        |
                                                        v
                                                    G29-04
                                                        |
                                                        v
                                   unchanged G28 allowlisted invocation
                                                        |
                                                        v
                                      Canonical Platform Presentation
```

The capability result remains read-only. Coverage may be complete, partial, or
failed closed. Partial coverage is a valid deterministic result and is rendered
as missing-evidence presentation rather than execution authority.

## Replay continuity

The ingress Replay records the opaque request, validated canonical request
snapshot, Project Context link, and downstream G29-06 route hash. G29-06
reconstructs G29-02 selection and Platform Knowledge lineage, then delegates to
the G29-04 reconstructor. G29-04 reconstructs the unchanged six-step G28 Replay
and validates the Canonical Presentation hash.

Reconstruction therefore verifies the complete chain from the supplied wrapper
through the existing capability output. Hash, identity, ordering, selection,
input, certification, output, or presentation drift fails closed.

## Ownership boundaries

- Platform Core owns canonical validation and deterministic semantic selection.
- The existing G20-03 runtime owns capability-composition analysis.
- G28 owns allowlisted capability invocation and input/output validation.
- G29-04 owns lifecycle composition.
- Canonical Presentation owns result normalization only.
- Human Interface transports opaque references and renders Platform Core output.
- Human Interface gains no validation, selection, invocation, or Replay authority.
- No Provider or Worker is selected or invoked.
- No repository, Governance, or Replay mutation is authorized.

## Certification evidence

The existing `PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME` certification
record now references this onboarding evidence in addition to its G20-03
implementation evidence. Focused tests prove:

- immutable request validation and tamper rejection;
- direct G28 adapter invocation and reconstruction;
- natural-language Project Objective and semantic selection;
- explicit canonical artifact ingress;
- Platform Knowledge identity continuity;
- G29-04 and G28 traversal;
- Canonical Presentation compatibility;
- nested ingress and route Replay reconstruction;
- absence of Human Interface, Provider, Worker, and mutation authority.

## Reusable onboarding pattern

Future deterministic read-only capabilities should reuse this bounded pattern:

```text
existing certified implementation
  + canonical immutable input contract
  + existing certification record evidence
  + static G28 allowlisted adapter
  + G29 semantic descriptor
  + ingress validator dispatch
  + G29-06 input projection
  + native output validation
  + existing presentation adapter
  + nested Replay reconstruction tests
```

A future onboarding must not introduce a dynamic registry, heuristic artifact
discovery, Human Interface semantics, or a parallel lifecycle merely to avoid
these explicit certification steps.

## Remaining boundary

This milestone proves reuse for a fourth deterministic read-only Platform Core
capability. Provider-assisted cognition and Worker execution remain separate
governed integrations requiring their existing authorization, identity,
credential, approval, and Replay contracts.
