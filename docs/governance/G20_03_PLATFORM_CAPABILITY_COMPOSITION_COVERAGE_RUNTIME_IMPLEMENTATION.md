# G20-03 Platform Capability Composition Coverage Runtime

Status: implemented and certified at implementation scope.

Final verdict:

`PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ACHIEVED_THROUGH_MINIMAL_PLATFORM_CORE_COMPOSITION`

## Objective

G20-03 implements the minimal canonical composition identified by the G20-02
audit. The runtime deterministically discovers reusable Platform capabilities,
computes request-facet coverage, identifies certified reusable compositions,
records uncovered residual gaps, and recommends the smallest required Platform
extension.

The implementation is a bounded read-only composition service. It is not a
new Platform subsystem.

## Reused Capabilities

The runtime composes existing:

- Candidate Capability Discovery;
- Platform Knowledge Runtime;
- Platform Capability Certification Registry;
- Unified Platform Query Router route descriptors;
- Generation Certification Evidence Profile;
- governance certification evidence;
- optional replay evidence.

The Canonical Platform Presentation Layer normalizes the result, and the
Unified Platform Query Router exposes the service through the canonical
`CAPABILITY_COMPOSITION_DISCOVERY` query class.

## Canonical Artifact

The runtime produces:

`PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1`

The artifact includes:

- deterministic request facets and matched terms;
- discovered certified reusable capabilities;
- capability-to-facet coverage;
- routability metadata and descriptor hashes;
- certified reusable compositions and dependencies;
- governance evidence references and content hashes;
- optional replay evidence hash and lineage validation;
- uncovered residual gaps;
- minimal required Platform extension;
- source precedence and reused service declarations;
- final artifact hash and explicit boundary flags.

## Deterministic Outcomes

Coverage status is one of:

- `CAPABILITY_COMPOSITION_COVERAGE_COMPLETE`;
- `CAPABILITY_COMPOSITION_COVERAGE_PARTIAL`;
- `CAPABILITY_COMPOSITION_COVERAGE_FAILED_CLOSED`.

The minimal extension classification distinguishes:

- an existing certified capability;
- an existing certified composition;
- a minimal composition service requirement;
- a genuinely uncovered capability facet;
- ambiguous discovery that fails closed.

The runtime does not treat keyword matching alone as certification. Coverage
requires a non-superseded certified registry record. Known composition matches
require implementation-scope certification metadata and explicit dependency
bindings.

## Architectural Boundaries

The implementation preserves:

- Platform Core ownership;
- read-only behavior;
- deterministic hashes and fail-closed ambiguity;
- registry and governance evidence authority;
- existing router and presentation ownership;
- existing Generation and Replay Certification contracts;
- Human Interfaces as thin adapters;
- provider and worker non-invocation;
- repository, governance, and replay non-mutation.

No capability registry, certification engine, knowledge runtime, router,
presentation layer, replay subsystem, provider runtime, worker runtime, or
Human Interface logic was duplicated.

## Implemented Surface

- `aigol/runtime/platform_capability_composition_coverage.py`
- `aigol/runtime/platform_query_router.py`
- `aigol/runtime/platform_presentation_layer.py`
- `aigol/runtime/platform_capability_certification_registry.py`
- `tests/test_g20_03_platform_capability_composition_coverage.py`
- `tests/test_g19_04_platform_query_router.py`

The existing `aigol/cli/aicli.py` remains unchanged.

## Validation

Validation includes focused composition, router, presentation, read-only
binding, Generation Certification, and registry regressions; governance
conformance; the full test suite; Python compilation; and `git diff --check`.
Final results are recorded in the implementation handoff.

## Final Verdict

`PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ACHIEVED_THROUGH_MINIMAL_PLATFORM_CORE_COMPOSITION`
