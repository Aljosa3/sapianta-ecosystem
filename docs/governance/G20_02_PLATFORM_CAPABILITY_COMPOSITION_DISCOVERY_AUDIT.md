# G20-02 Platform Capability Composition Discovery Audit

Status: AUDIT COMPLETE

Date: 2026-07-11

Scope: `AUDIT_ONLY` architectural review of whether Platform Core can
deterministically discover reusable capabilities and certified compositions
before implementation. This audit does not modify runtime behavior, tests,
Human Interfaces, certification semantics, replay semantics, provider or worker
behavior, or existing governance artifacts other than this report.

## Executive Summary

Platform Core already contains most of the deterministic information required
for Platform Capability Composition Discovery.

Existing services can already answer separate parts of the discovery problem:

| Question | Existing deterministic source |
| --- | --- |
| What capability exists? | Candidate Capability Discovery, Platform Knowledge Runtime, Capability Certification Registry |
| Who owns and implements it? | Capability Certification Registry and Platform Knowledge Runtime |
| Is it certified? | Capability Certification Registry and certification evidence references |
| Which service can answer a query? | Unified Platform Query Router route descriptors |
| Should existing work be reused? | Project Knowledge Reuse |
| Which certified composition proves the reuse pattern? | Generation Certification Composition Service and its Generation Evidence Profile |
| What governance or replay evidence supports it? | Governance reports, Replay Observation, Replay Certification, workspace replay metadata |

No genuinely new capability registry, knowledge system, certification engine,
replay system, semantic subsystem, provider runtime, worker runtime, or Human
Interface authority is required.

The remaining gap is narrower: Platform Core has no canonical service that
joins these existing results into one deterministic **capability composition
discovery artifact**. Current services select one candidate capability, one
certification record, or one query route. They do not produce a general
many-to-many coverage model containing:

- the requested problem facets;
- all matching certified Platform capabilities;
- existing routable services;
- known certified composition dependencies;
- evidence-backed reuse coverage;
- residual unimplemented requirements;
- the smallest admissible canonical composition.

The missing functionality is therefore a bounded Platform Core composition
service, not a new subsystem.

Final verdict:

`PLATFORM_CAPABILITY_COMPOSITION_DISCOVERY_REUSE_WITH_MINIMAL_CANONICAL_COMPOSITION_BINDING`

## Architectural Findings

### 1. Deterministic capability metadata already exists

The Platform Capability Certification Registry records deterministic,
hash-bound metadata for certified Platform capabilities:

- canonical capability identifier;
- capability, architectural, and implementation owner;
- certification status and scope;
- certification milestone and version;
- certification evidence references;
- verification type;
- supersession state;
- certification record hash.

This is sufficient to establish that a registered capability exists, where it
is implemented, who owns it, whether it is certified, and whether it remains
current. The registry remains metadata only and correctly does not grant
runtime authority.

### 2. Natural-language candidate discovery already exists

Platform Core Project Services exposes deterministic Candidate Capability
Discovery. It evaluates a bounded capability catalog, workspace knowledge,
certified artifacts, active objectives, keyword evidence, and ambiguity. It
returns a replay-visible, hash-bound artifact containing candidate scores,
selected goal target, reuse basis, and a capability-resolution decision.

This surface is useful but intentionally development-oriented. Its catalog is
small and uses project goal identifiers such as `replay`, `certification`, and
`human_interface`. Those identifiers are not a complete canonical mapping to
the uppercase capability identities held by the certification registry.

### 3. Platform Knowledge already composes discovery and certification

The Platform Knowledge Runtime already reuses:

- Candidate Capability Discovery;
- Project Knowledge Reuse;
- Capability Certification Registry;
- governance evidence references;
- PCCL reference-owner metadata;
- workspace and replay metadata.

It provides deterministic answers for capability existence, owner,
implementation owner, certification state, evidence, recommended service, and
reuse recommendation.

Its current contract resolves one best certification record for a free-form
query. It does not return a complete ranked set of capabilities or calculate
coverage across multiple problem facets.

### 4. Routing metadata already identifies reusable services

The Unified Platform Query Router exposes deterministic service descriptors
containing:

- service identifier;
- service and implementation owner;
- supported query classes;
- required inputs;
- response artifact type;
- service version;
- adapter identity;
- routing terms;
- descriptor hash.

The current descriptors make Platform Knowledge, Root Cause Trace, Governed
Development, and Generation Certification routable without moving selection
authority into Human Interfaces.

The descriptor collection is a routability catalog, not a composition graph.
It does not state which capabilities a service consumes, which capabilities it
composes, what problem facets it satisfies, or which remaining gaps require a
new binding.

### 5. G20-01 establishes a certified composition precedent

The Generation Certification Composition Service proves the target
architecture:

- a canonical evidence profile declares required capabilities and evidence;
- existing certification, knowledge, governance, runtime, replay observation,
  and replay certification evidence is composed;
- completeness, hashes, lineage, certification, and supersession are checked;
- a bounded result artifact is returned;
- router and presentation layers are reused;
- no duplicate certification subsystem is created.

This is strong evidence that Capability Composition Discovery should follow
the same pattern. G20-01 is one certified composition instance, not yet a
general registry or discovery model for all Platform compositions.

## Existing Reusable Platform Capabilities

| Capability | Existing responsibility | Discovery contribution | Reuse readiness |
| --- | --- | --- | --- |
| Platform Capability Certification Registry | Canonical certification and ownership metadata | Exact capability identity, implementation owner, certification, evidence, supersession | High |
| Candidate Capability Discovery | Deterministic natural-language and workspace candidate inference | Candidate problem families, scores, goal targets, ambiguity | High, with identifier coverage limitation |
| Project Knowledge Reuse | Classifies already satisfied, extending, modifying, certified-related, or new work | Reuse recommendation, duplicate-work evidence, known milestones and history | High |
| Platform Knowledge Runtime | Composes registry, discovery, knowledge reuse, governance, PCCL, and workspace evidence | Existing capability and service answer | High |
| Unified Platform Query Router | Selects one responsible Platform service | Routable service descriptors and required inputs | High |
| Canonical Platform Presentation Layer | Normalizes existing Platform responses | Reusable result presentation shape | High |
| Generation Certification Composition Service | Composes certified capability and evidence requirements | Certified example of explicit composition dependencies and residual evidence gaps | High as precedent and composition evidence |
| Replay Observation Layer | Normalizes deterministic runtime and certification observations | Evidence continuity and observed status | High when replay evidence is required |
| Replay Certification | Certifies validated execution replay | Certified execution-result evidence reference | High within its existing narrow contract |
| PCCL reference metadata | Binds reference types to authoritative Platform owners | Ownership-preserving references to discovery, knowledge, certification, governance, and replay | High as metadata carrier |
| Governance reports | Authoritative architectural and certification evidence | Rationale, scope, limitations, milestones | High |
| Workspace replay metadata | Known targets, certified artifacts, implementation history, prior decisions | Project-specific reuse and continuity | High when workspace state exists |

## Capability Discovery Analysis

### What Platform Core can answer now

Without Providers, Workers, or Human Interface authority, Platform Core can
already answer deterministically:

1. Whether an exact registered capability exists.
2. Whether that capability is certified, verified, superseded, or deprecated.
3. Which component owns and implements it.
4. Which governance evidence supports its certification.
5. Whether a free-form request matches a bounded project capability family.
6. Whether workspace evidence shows the work as already satisfied, extending,
   modifying, or new.
7. Which registered Platform service should answer supported query classes.
8. Whether Generation Certification is an existing certified composition.

These operations are deterministic, read-only, hash-visible, and Platform
Core-owned.

### What Platform Core cannot answer canonically yet

Before every implementation, no existing single contract can reliably answer:

1. Which distinct functional facets are present in the requested work.
2. Which complete set of certified capabilities covers those facets.
3. Which existing services must be composed together rather than selecting
   only one service.
4. Which certified compositions already combine those capabilities.
5. Which dependencies and evidence requirements belong to each composition.
6. Which request facets remain uncovered after reuse.
7. Whether the residual gap is service logic, route binding, presentation
   binding, evidence profile, or genuinely new capability semantics.
8. What the smallest deterministic canonical composition would be.

The absence of this unified answer means the information is available but must
still be manually assembled during architecture audits.

## Composition Analysis

Platform Capability Composition Discovery can be built entirely by composing
existing Platform Core services.

Recommended source precedence:

1. Capability Certification Registry for canonical capability identity,
   ownership, certification, evidence, and supersession.
2. Platform Knowledge Runtime for capability matching, knowledge sources, and
   reuse recommendations.
3. Candidate Capability Discovery and Project Knowledge Reuse for request and
   workspace-specific matching.
4. Query Router descriptors for routable services, required inputs, response
   artifact types, and service versions.
5. Existing composition evidence profiles, beginning with Generation
   Certification, for explicit dependency examples.
6. Governance reports for composition rationale and limitations.
7. Replay Observation and Replay Certification for evidence-bound runtime
   continuity only.
8. PCCL metadata for owner-preserving reference binding.

The composition must not infer runtime truth from certification metadata alone.
It should distinguish:

- capability identity from service routability;
- certification metadata from authoritative certification artifacts;
- project reuse from complete functional satisfaction;
- known compositions from merely co-occurring capabilities;
- missing evidence from missing implementation;
- missing binding from genuinely missing semantics.

## Gap Analysis

### Existing Platform Core capabilities

These are already implemented and should not be duplicated:

- capability discovery;
- certification lookup and supersession checks;
- project knowledge reuse;
- service routing metadata;
- canonical presentation;
- generation evidence profiles;
- replay observation and replay certification;
- governance and workspace evidence resolution.

### Reusable Platform compositions

Existing composition patterns include:

- Platform Knowledge composition over registry, Project Services, governance,
  PCCL, and workspace metadata;
- Unified Query Router composition over knowledge, causality, certification,
  and development service routes;
- Canonical Presentation composition over heterogeneous service artifacts;
- Governed Read-Only Work Binding over routing and presentation;
- Generation Certification composition over capability, governance, runtime,
  replay observation, and replay certification evidence.

### Genuinely missing capability

The precise missing capability is:

`CANONICAL_MULTI_CAPABILITY_COMPOSITION_COVERAGE_AND_RESIDUAL_GAP_RESOLUTION`

It must join multiple existing discovery surfaces into one deterministic
artifact that records:

- normalized request facets;
- matched canonical capability identifiers;
- certified and supersession status;
- candidate routable services;
- known certified composition matches;
- capability-to-facet coverage;
- required composition dependencies;
- missing required evidence;
- uncovered facets;
- residual gap classification;
- minimal recommended canonical composition;
- source hashes, confidence, ambiguity, and limitations.

This capability does not need new semantic authority. It needs deterministic
composition and explicit cross-surface bindings.

### Deterministic first stopping point

The first deterministic stopping point is the transition from single-candidate
selection to multi-capability coverage.

`discover_candidate_capabilities(...)` selects one highest-scoring candidate.
Platform Knowledge then resolves one best certification record. The Query
Router selects one service route. None proceeds to a canonical many-to-many
coverage and residual-gap artifact.

The identifier boundary reinforces this stop:

- Project Services uses a small lower-case goal-oriented `CAPABILITY_CATALOG`;
- the Certification Registry uses canonical uppercase certified capability
  identifiers;
- Query Router descriptors use service identifiers and query classes;
- Generation Evidence Profiles list explicit dependencies for one generation;
- no canonical binding maps all four surfaces into one composition model.

## Minimal Canonical Composition Recommendation

If implemented in a future milestone, Platform Capability Composition
Discovery should be another bounded, read-only Platform Core composition
service.

It should not become a broad new runtime subsystem. Its only responsibilities
should be:

1. Accept a request and optional workspace/evidence context.
2. Reuse Candidate Capability Discovery and Platform Knowledge.
3. enumerate matching certification records rather than selecting only one.
4. Join candidates to Query Router service descriptors.
5. Resolve known composition profiles and certification evidence.
6. Compute deterministic facet coverage and remaining gaps.
7. Classify the residual gap using a bounded vocabulary such as:
   - `NO_GAP_EXISTING_CAPABILITY_SUFFICIENT`;
   - `MINIMAL_ROUTE_BINDING_REQUIRED`;
   - `MINIMAL_PRESENTATION_BINDING_REQUIRED`;
   - `MINIMAL_EVIDENCE_PROFILE_REQUIRED`;
   - `MINIMAL_COMPOSITION_SERVICE_REQUIRED`;
   - `GENUINELY_NEW_CAPABILITY_REQUIRED`;
   - `DISCOVERY_AMBIGUOUS_FAILED_CLOSED`.
8. Return one hash-bound, replay-visible discovery artifact.

Recommended conceptual result:

```text
human or Platform request
-> Candidate Capability Discovery
-> Platform Knowledge and Certification Registry
-> Query Router service descriptors
-> known composition profiles and governance evidence
-> deterministic capability-to-facet coverage
-> residual gap classification
-> minimal canonical composition recommendation
-> Canonical Platform Presentation
```

This is comparable in architectural size to the Generation 19 Platform
Knowledge and Query Router bindings and to the G20-01 Generation Certification
composition service.

## Architectural Boundaries

A future composition discovery service must preserve:

- Platform Core ownership of discovery and composition analysis;
- Certification Registry authority over certification metadata;
- governance reports as authoritative certification evidence;
- Replay Observation and Replay Certification ownership of replay evidence;
- Query Router ownership of service selection;
- Canonical Presentation ownership of normalized presentation;
- Human Interfaces as thin render-only adapters;
- provider and worker non-invocation;
- read-only repository and replay behavior;
- fail-closed ambiguity, missing-evidence, and identifier handling;
- explicit limitation visibility;
- no automatic implementation authorization or mutation.

It must not:

- create a duplicate capability or certification registry;
- treat keyword matching as proof of capability satisfaction;
- infer a certified composition merely because capabilities coexist;
- broaden Replay Certification beyond validated execution results;
- move architecture decisions into `aicli`;
- invoke Providers or Workers for discovery;
- automatically authorize implementation;
- reframe missing or partial evidence as complete coverage.

## Implementation Recommendation

Implementation readiness is high for a small composition binding because all
required source services already exist.

A future implementation should add only:

- one canonical composition-discovery artifact contract;
- one deterministic identifier/cross-surface binding;
- one coverage and residual-gap composition function;
- one Query Router descriptor and adapter;
- one Canonical Presentation normalization adapter;
- focused fail-closed regressions;
- implementation-scope certification metadata after validation.

No new Platform subsystem is recommended.

This audit does not implement that recommendation.

## Final Verdict

`PLATFORM_CAPABILITY_COMPOSITION_DISCOVERY_REUSE_WITH_MINIMAL_CANONICAL_COMPOSITION_BINDING`

Platform Core already contains the deterministic capability, certification,
service, governance, runtime, replay, and composition metadata needed for
discovery. The missing functionality is one bounded composition that converts
those distributed sources into multi-capability coverage, certified
composition matches, residual gaps, and the smallest canonical reuse plan.
