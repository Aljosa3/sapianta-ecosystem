# UBTR Orchestration Architecture Specification V1

Status: Generation 2 architecture specification.

This artifact defines the complete Universal Bidirectional Translation Runtime
orchestration architecture for AiGOL Generation 2.

It does not implement runtime code.
It does not redesign Governance.
It does not redesign OCS.
It does not redesign Replay.

## 1. Purpose

Platform Core Generation 1 certified UBTR as the canonical semantic authority,
with compatibility layers still present in several consumers.

Generation 2 requires UBTR to become not only the canonical semantic authority,
but also the orchestrator of the complete semantic cognition lifecycle:

```text
Human Input
  |
  v
UBTR Orchestration
  |
  +-- Deterministic semantic interpretation
  |
  +-- Ambiguity and confidence evaluation
  |
  +-- Escalation decision
  |
  +-- OCS-governed provider cognition when needed
  |
  +-- Multi-provider comparison when needed
  |
  v
Canonical Semantic Artifact
  |
  v
Replay Evidence
  |
  v
Human-Readable Projection
```

The objective is one canonical semantic pipeline while preserving the existing
constitutional boundaries:

- UBTR owns semantic orchestration.
- OCS governs cognition provider invocation.
- Providers remain non-authoritative.
- Replay records every semantic decision.
- Human authority remains final.

## 2. Architecture Position

UBTR sits above ACLI and below the human-facing interaction layer.

UBTR does not replace HIRR, OCS, PPP, workers, replay, approval, or governance.
Instead, UBTR produces the canonical semantic artifact that downstream consumers
use instead of independently interpreting human language.

```text
Human
  |
  v
Universal Bidirectional Translation Runtime
  |
  v
Canonical Semantic Artifact
  |
  +--> HIRR / workflow resolution
  +--> ACLI operator presentation
  +--> OCS cognition workflow, when escalation is required
  +--> PPP and worker projections
  +--> Replay and hardening evidence
```

## 3. End-To-End Orchestration Diagram

```text
Human Natural Language
  |
  v
[1] Human input normalization
  |
  v
[2] Deterministic semantic interpretation
  |
  v
[3] Ambiguity detection
  |
  v
[4] Confidence evaluation
  |
  v
[5] Escalation decision
  |
  +-----------------------------+
  |                             |
  v                             v
Deterministic only        Provider escalation required
  |                             |
  |                             v
  |                      [6] OCS cognition request
  |                             |
  |                             v
  |                      [7] Lowest-cost capable provider
  |                             |
  |                             v
  |                      [8] Capability escalation, if needed
  |                             |
  |                             v
  |                      [9] Multi-provider comparison, if needed
  |                             |
  |                             v
  |                      [10] Consensus integration
  |                             |
  +-------------+---------------+
                |
                v
        [11] Canonical Semantic Artifact generation
                |
                v
        [12] Replay translation evidence
                |
                v
        [13] Human-readable projection
```

## 4. Orchestration Stage Responsibilities

| Stage | UBTR Responsibility | OCS Responsibility | Provider Responsibility | Replay Responsibility | Human Authority Boundary |
| --- | --- | --- | --- | --- | --- |
| 1. Human input normalization | Normalize language, preserve original prompt, create translation request identity. | None unless escalation is later requested. | None. | Record original prompt reference and normalization artifact. | Human remains source of request. |
| 2. Deterministic semantic interpretation | Apply deterministic semantic rules and produce initial semantic payload. | None. | None. | Record deterministic translation evidence. | No execution or approval occurs. |
| 3. Ambiguity detection | Identify ambiguity flags, missing entities, conflicting intent, multilingual uncertainty, and unsafe uncertainty. | None. | None. | Record ambiguity flags and inputs. | Human may later clarify ambiguity. |
| 4. Confidence evaluation | Assign deterministic confidence and fidelity status. | None. | None. | Record confidence and scoring basis. | Human confidence is not inferred as approval. |
| 5. Escalation decision | Decide deterministic-only or provider escalation using policy thresholds. | Validate whether requested cognition escalation is admissible. | None. | Record escalation decision, reason, and rejected alternatives. | Human can decline or request clarification; no provider result becomes authority. |
| 6. OCS cognition request | Create bounded semantic cognition request for OCS. | Govern provider workflow, enforce provider eligibility, fail closed if unavailable. | None until invoked by OCS. | Record OCS request and governance decision. | Human remains authority over downstream approval. |
| 7. Lowest-cost capable provider | Specify semantic task requirements and fidelity constraints. | Select the lowest-cost eligible capable provider. | Produce cognition artifact only. | Record provider selected, request, response, cost tier, and status. | Provider output is advisory. |
| 8. Capability escalation | Determine whether provider output is insufficient. | Govern escalation to higher capability provider. | Produce additional cognition artifact. | Record escalation reason and provider lineage. | Escalation does not authorize action. |
| 9. Multi-provider comparison | Request comparison when semantic ambiguity remains material. | Govern multi-provider cognition and comparison workflow. | Produce independent cognition artifacts. | Record all provider artifacts and comparison inputs. | Disagreement requires governed handling or human review. |
| 10. Consensus integration | Integrate agreement, disagreement, confidence, and uncertainty into semantic synthesis. | Ensure comparison evidence is valid and non-authoritative. | No authority; providers do not vote execution into existence. | Record comparison outcome and consensus rationale. | Human review remains available where ambiguity persists. |
| 11. Canonical Semantic Artifact generation | Produce the single canonical semantic artifact consumed by Platform Core. | No semantic authority; may attach governance admissibility evidence. | None. | Record artifact hash, schema version, lineage, and source artifacts. | Artifact informs governance; it does not approve or execute. |
| 12. Replay translation evidence | Emit replay-visible semantic decision evidence. | Provide OCS governance evidence for cognition steps. | Provider artifacts remain replay evidence. | Persist full semantic lineage and reconstruction material. | Replay is source of truth for what happened. |
| 13. Human-readable projection | Produce deterministic human-readable projection from canonical artifact. | None unless projection includes governed cognition summary. | Optional provider-assisted explanation remains non-authoritative. | Record projection and explanation source. | Human decides whether to approve, reject, clarify, or stop. |

## 5. Responsibility Matrix

| Responsibility | UBTR | OCS | Provider | Replay | Human |
| --- | --- | --- | --- | --- | --- |
| Semantic translation ownership | Owns | Does not own | Does not own | Records | Reviews |
| Provider cognition governance | Requests when needed | Owns | Participates | Records | May review |
| Provider selection | Specifies need and constraints | Owns selection and admissibility | None | Records | None |
| Cost-aware escalation | Requests based on semantic need | Governs provider tier escalation | Responds | Records | None |
| Multi-provider comparison | Requests when needed | Owns governed comparison execution | Produces artifacts | Records | Reviews material ambiguity |
| Canonical semantic artifact | Owns generation | Supplies governance evidence | Supplies non-authoritative input | Records artifact and lineage | Consumes projection |
| Workflow authority | Supplies semantic input | Does not approve execution | None | Records | Human approval remains required |
| Execution authority | None | None | None | Records only | Human approval plus governed worker path |
| Human explanation | Produces projection | May supply cognition summary | Optional advisory wording | Records source | Reads and decides |

## 6. Cognition Escalation Pipeline

UBTR must attempt deterministic semantic interpretation first.

Provider escalation is permitted only when deterministic interpretation is
insufficient under explicit replay-visible criteria.

### 6.1 Deterministic-Only Path

UBTR remains deterministic-only when:

- confidence meets the required threshold;
- ambiguity is absent or immaterial;
- required entities are present;
- fidelity checks pass;
- the request maps to a known semantic contract;
- no operator asks for improved explanation or broader cognition.

Result:

```text
Deterministic Translation
  |
  v
Canonical Semantic Artifact
```

### 6.2 Escalation Triggers

UBTR may request OCS cognition when one or more conditions are true:

- ambiguity exceeds threshold;
- confidence falls below threshold;
- required entity extraction is incomplete;
- multilingual normalization is uncertain;
- deterministic semantic fidelity fails;
- translation completeness is insufficient;
- operator explicitly requests improved explanation, comparison, summary, or proposal-only cognition;
- downstream consumer requires semantic projection that deterministic rules cannot safely provide.

Each trigger must be recorded as an escalation reason.

### 6.3 Provider Tiering

OCS governs provider selection using the bounded cognition request produced by
UBTR.

Provider tiering order:

1. No provider, deterministic only.
2. Lowest-cost capable provider.
3. Higher-capability provider if the lower tier is insufficient.
4. Multiple providers when independent comparison is required.
5. Governed comparison and consensus integration.

UBTR never allows a provider to replace the canonical semantic artifact.
Provider output is input evidence only.

### 6.4 Multi-Provider Comparison

Multi-provider comparison is required only when:

- provider outputs conflict on material semantic meaning;
- confidence remains below threshold after single-provider escalation;
- the request is high impact and requires independent cognition evidence;
- multilingual or domain ambiguity remains unresolved;
- replay evidence needs explicit agreement or disagreement analysis.

Comparison output must preserve:

- agreement analysis;
- disagreement analysis;
- confidence synthesis;
- unresolved ambiguity;
- provider provenance;
- cost and capability tier.

UBTR integrates comparison evidence into the canonical semantic artifact.
OCS governs the comparison workflow.
Replay records the full chain.

## 7. Canonical Semantic Artifact Generation

The final output of UBTR orchestration is one Canonical Semantic Artifact.

The artifact must include, at minimum:

- semantic identity;
- workflow identity, if known;
- conversation identity;
- replay identity;
- translation lineage;
- confidence representation;
- ambiguity representation;
- clarification state;
- approval state;
- execution intent;
- provider projection;
- worker projection;
- human-readable projection;
- technical projection;
- authority flags;
- deterministic artifact hash.

UBTR generates this artifact from:

- original human input;
- deterministic translation output;
- ambiguity and confidence evaluation;
- provider cognition artifacts, if any;
- provider comparison artifacts, if any;
- OCS governance evidence, if any;
- replay lineage references.

The artifact is canonical semantic evidence.
It is not approval.
It is not execution authorization.
It is not a worker request.

## 8. Replay Evidence Flow

Replay must record every semantic decision required to reconstruct the
orchestration chain.

Required replay evidence:

- original operator input reference;
- normalized input;
- deterministic translation artifact;
- ambiguity flags;
- confidence score and threshold;
- escalation decision;
- escalation reason;
- OCS cognition request, if any;
- provider eligibility and selection;
- provider request and response;
- provider tier and cost metadata;
- provider comparison inputs and outputs;
- consensus integration result;
- canonical semantic artifact;
- human-readable projection;
- fallback path, if any;
- fail-closed reason, if any.

Replay must be sufficient to answer:

- why deterministic translation was accepted or rejected;
- why provider escalation occurred or did not occur;
- which provider was selected and why;
- whether provider output was accepted as evidence;
- how the canonical semantic artifact was produced;
- what the human saw before any approval decision.

## 9. Authority Boundaries

UBTR authority:

- canonical semantic orchestration;
- canonical semantic artifact generation;
- ambiguity and confidence evaluation;
- semantic replay evidence generation;
- human-readable semantic projection.

OCS authority:

- governed cognition workflow invocation;
- provider admissibility;
- provider selection;
- provider escalation governance;
- multi-provider comparison governance;
- fail-closed cognition handling.

Provider authority:

- none.

Providers may only produce cognition artifacts.
Provider output is never workflow authority, approval authority, execution
authority, replay authority, or governance authority.

Replay authority:

- source of truth for evidence lineage;
- deterministic reconstruction of semantic decisions;
- immutable record of provider involvement and projections.

Human authority:

- final approval, rejection, clarification, modification, or stop decision;
- no semantic artifact or provider output may bypass the human approval boundary.

## 10. Failure Handling

UBTR orchestration must fail closed when:

- normalized input cannot be represented safely;
- deterministic translation is malformed;
- ambiguity is material and cannot be resolved;
- confidence is below threshold and escalation is unavailable;
- OCS rejects provider cognition;
- provider output violates authority boundaries;
- provider output fails fidelity checks;
- comparison results conflict without resolvable consensus;
- canonical semantic artifact cannot be generated deterministically;
- replay evidence cannot be persisted.

Fail-closed output must include:

- failure stage;
- reason;
- available replay reference;
- whether human clarification is possible;
- confirmation that no approval, worker execution, or repository mutation occurred.

## 11. Implementation Roadmap

This specification does not implement code.

Recommended implementation sequence:

### Phase 1: Orchestration Contract

Define the UBTR orchestration request and response contract around the Canonical
Semantic Artifact.

Acceptance criteria:

- deterministic schema;
- replay-safe hashes;
- explicit authority flags;
- compatibility with existing translation artifacts.

### Phase 2: Deterministic Orchestration Wrapper

Wrap existing Human to Governance and Governance to Human translation runtimes
under one UBTR orchestration entrypoint.

Acceptance criteria:

- no provider invocation required;
- existing deterministic behavior preserved;
- replay records orchestration stage decisions.

### Phase 3: UBTR to OCS Cognition Handoff

Create the bounded handoff where UBTR requests OCS cognition only after
replay-visible escalation criteria are met.

Acceptance criteria:

- OCS remains responsible for provider governance;
- UBTR does not call providers directly;
- provider unavailability fails closed.

### Phase 4: Provider Tier and Comparison Return Path

Return OCS cognition and comparison artifacts to UBTR as non-authoritative
semantic evidence.

Acceptance criteria:

- provider outputs preserve provenance;
- comparison output includes agreement, disagreement, confidence, and unresolved
  ambiguity;
- no provider output mutates workflow state.

### Phase 5: Canonical Semantic Artifact Builder

Generate one canonical artifact from deterministic and provider-assisted
semantic evidence.

Acceptance criteria:

- stable artifact hash;
- complete translation lineage;
- replay reconstruction;
- human-readable and technical projections.

### Phase 6: Consumer Migration

Migrate Platform Core consumers to consume the canonical semantic artifact rather
than local marker-based interpretation.

Acceptance criteria:

- ACLI, HIRR, routing, PPP, approval, resume, replay, hardening, and explanation
  consumers use canonical semantic fields;
- compatibility layers remain only until regression coverage proves migration.

### Phase 7: Certification

Certify UBTR orchestration end to end.

Acceptance criteria:

- deterministic-only scenario passes;
- provider escalation scenario passes;
- provider unavailable scenario fails closed;
- multi-provider comparison scenario reconstructs from replay;
- no authority boundary changes occur.

## 12. Non-Goals

This specification does not:

- redesign Governance;
- redesign OCS;
- redesign Replay;
- redesign HIRR;
- redesign PPP;
- introduce autonomous provider authority;
- introduce autonomous execution;
- remove human approval;
- require providers for deterministic requests;
- require immediate removal of compatibility layers.

## 13. Certification Impact

This architecture is a Generation 2 objective.

Platform Core Generation 1 remains certified with limitations because UBTR is
canonical but not exclusive.

Completing this specification would support Generation 2 certification by
making UBTR:

- the exclusive semantic orchestration authority;
- the single producer of canonical semantic artifacts;
- the governed bridge between deterministic semantics and OCS cognition;
- the semantic evidence source consumed by downstream Platform Core components.

## 14. Final Verdict

UBTR_ORCHESTRATION_ARCHITECTURE_READY
