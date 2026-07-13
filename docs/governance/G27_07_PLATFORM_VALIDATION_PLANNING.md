# G27-07 — Platform Validation Planning

Status: IMPLEMENTED AND DETERMINISTICALLY VERIFIED

Date: 2026-07-13

## Purpose

G27-07 implements one bounded Platform Core capability:

`PLATFORM_CHANGE_IMPACT_ARTIFACT_V1 -> PLATFORM_VALIDATION_PLAN_ARTIFACT_V1`

It deterministically projects affected capabilities, constitutional layers,
Governance surfaces, Replay surfaces, and Certification surfaces into ordered
validation requirements. It plans validation only. It does not construct a
validation candidate, execute a command, invoke a Worker or Provider, authorize
execution or mutation, or certify a result.

## Runtime and Canonical Artifact

Runtime:

- `aigol/runtime/platform_validation_planning_runtime.py`

Canonical artifact:

- `PLATFORM_VALIDATION_PLAN_ARTIFACT_V1`

Operations:

- `plan_platform_validation(...)`;
- `validate_platform_validation_plan_artifact(...)`;
- `reconstruct_platform_validation_plan_replay(...)`.

Registry capability:

- `PLATFORM_VALIDATION_PLANNING`.

## Ingress and Binding

The only accepted semantic input is a validated, non-failed
`PLATFORM_CHANGE_IMPACT_ARTIFACT_V1`. The runtime verifies the impact artifact,
its deterministic hash, its artifact hash, the impact analysis reference, and
the supplied source hash. Each affected capability is rebound to the current
Platform Capability Certification Registry record hash. Stale or altered
ownership metadata fails closed.

## Deterministic Requirement Mapping

Requirements are produced in this fixed category order:

1. affected capability regression verification;
2. constitutional layer verification;
3. Governance surface conformance;
4. Replay surface integrity;
5. Certification evidence continuity.

Within a category, source identifiers are sorted. Every requirement has a
deterministic index, identifier, owner, mapping evidence, and hash. L0 through
L4 use explicit validation semantics; an unsupported layer fails closed.

Inherited optional unresolved mappings are preserved and receive the planning
disposition `PRESERVED_OPTIONAL_SOURCE_MAPPING`. Required capability, layer, or
surface mappings are never represented as optional: absence, ambiguity, stale
registry binding, or unsupported values fail closed.

## Allowlist Boundary

The runtime reads the existing Validation Allowlist but does not change it.
An existing command identifier is referenced only when the command's declared
repository Python target set exactly equals the affected path set. Partial,
subset, inferred, natural-language, or synthesized command mappings are
prohibited.

G27-07 introduces no command identifiers. For impacts without an existing exact
mapping, `allowlisted_command_references` is empty and the semantic requirements
remain explicit for a later, separately governed candidate-construction stage.
No argv is embedded in the plan.

## Replay Contract

One plan artifact is persisted in the `platform_validation_plan_recorded`
wrapper. Replay reconstruction verifies wrapper ordering and hash, artifact and
requirement hashes, deterministic plan hash, counts, status consistency,
allowlist references, and non-authority flags.

The deterministic plan hash excludes the plan identifier, creation timestamp,
and replay location. Identical validated impact and registry/allowlist state
therefore produce the same plan hash.

## Constitutional Boundary

This capability is read-only and non-authoritative. It does not:

- construct single-command or suite validation candidates;
- select or synthesize command argv;
- expand the Validation Allowlist;
- execute validation;
- invoke Workers or Providers;
- authorize execution, dispatch, or repository mutation;
- mutate Governance or Replay state;
- certify results.

The Validation Candidate Runtime and Validation Suite Candidate Runtime remain
downstream and are reused only as architectural boundaries; neither is called
by G27-07.

## Verification

Focused tests cover ordered mapping across all five input families,
determinism, source reference/hash binding, registry rebinding, unresolved
mapping preservation, strict artifact ingress, authority denial, replay
reconstruction, tamper detection, and capability registration.

## Known Limitations

- The existing production allowlist has one narrowly scoped G8 compile command.
  Most Platform Change Impact artifacts therefore correctly produce no command
  reference.
- The plan expresses deterministic validation obligations, not executable test
  selection. Candidate construction remains a later milestone.
- Optional unresolved hashes inherited from Change Normalization remain visible
  and are not silently promoted to resolved evidence.
