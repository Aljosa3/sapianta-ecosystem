# G20-01 Generation Certification Composition Service

Status: implemented and certified at implementation scope.

Final verdict: `GENERATION_CERTIFICATION_COMPOSITION_SERVICE_IMPLEMENTED`.

## Objective

Generation Certification is now bound as a Platform Core composition service.
The implementation reuses existing certification and replay capabilities and
does not introduce a new certification engine, registry, replay system,
router, presentation layer, or Human Interface authority.

## Implemented Surface

- `aigol/runtime/generation_certification_composition.py`
  - defines `GENERATION_EVIDENCE_PROFILE_V1`;
  - composes capability registry, Platform Knowledge, governance, runtime, and
    replay evidence;
  - applies deterministic completeness and supersession rules;
  - produces `GENERATION_CERTIFICATION_RESULT_V1`;
  - fails closed on invalid profiles, hash disagreement, uncertified or
    superseded capabilities, invalid evidence types, and incomplete lineage.
- `aigol/runtime/platform_query_router.py`
  - registers `GENERATION_CERTIFICATION` as a canonical query class;
  - routes generation certification requests to the composition service.
- `aigol/runtime/platform_presentation_layer.py`
  - normalizes `GENERATION_CERTIFICATION_RESULT_V1` through the existing
    canonical presentation model.
- `aigol/runtime/platform_capability_certification_registry.py`
  - records implementation-scope certification metadata for the composition
    service.
- `tests/test_g20_01_generation_certification_composition.py`
  - covers ready, incomplete, fail-closed, durable-certified, router,
    presentation, read-only binding, and registry behavior.

## Canonical Evidence Profile

The canonical Generation 19 profile declares:

- required capabilities;
- required certification records;
- required governance artifacts;
- required runtime evidence;
- required replay evidence;
- deterministic acceptance policy;
- known observations;
- supersession policy;
- optional durable certification evidence.

The profile is hash-bound. Mutation without recomputing the profile hash fails
closed. Declared governance hashes are checked against repository bytes.
Embedded runtime and replay artifacts are checked for artifact type, hash, and
lineage continuity.

## Result States

- `GENERATION_CERTIFICATION_READY`: all required evidence is complete, but no
  durable generation certification evidence was supplied.
- `GENERATION_CERTIFICATION_INCOMPLETE`: required evidence is absent.
- `GENERATION_CERTIFICATION_FAILED_CLOSED`: evidence is contradictory,
  invalid, uncertified, superseded, hash-inconsistent, or lineage-incomplete.
- `GENERATION_CERTIFIED`: all evidence is complete and valid durable,
  replay-visible certification evidence has already been recorded.

The composition service is read-only. It never claims that it recorded durable
evidence. `GENERATION_CERTIFIED` is emitted only when a hash-valid durable
record with `recorded = true` and `replay_visible = true` is supplied.

## Reused Platform Core Capabilities

- Capability Certification Registry;
- Platform Knowledge Runtime;
- Replay Observation Layer artifact contract;
- Replay Certification artifact contract;
- PCCL certification ownership metadata;
- Unified Platform Query Router;
- Canonical Platform Presentation Layer;
- Governed Read-Only Runtime Binding;
- governance and runtime evidence.

Replay Certification retains its existing narrow authority over validated
execution results. Generation Certification references that evidence when the
generation profile requires it; it does not broaden or replace Replay
Certification semantics.

## Ownership and Boundary Preservation

- Platform Core owns evidence composition and the deterministic verdict.
- Human Interfaces remain render-only thin adapters.
- No provider or worker is invoked.
- No repository, governance, source replay, or runtime implementation is
  mutated.
- Existing implementation approval and runtime binding remain unchanged.
- Missing or contradictory certification evidence remains visible.

## Validation

Required validation covers focused Generation Certification, Query Router,
Presentation Layer, Replay Certification, governance conformance, full tests,
Python compilation, and whitespace checks. Final results are recorded in the
implementation handoff.

## Final Verdict

`GENERATION_CERTIFICATION_ACHIEVED_THROUGH_PLATFORM_CORE_COMPOSITION`
