# UBTR Responsibility Boundary Specification V1

Status: Generation 2 responsibility boundary specification.

This artifact freezes the responsibility boundaries for the Universal
Bidirectional Translation Runtime before Generation 2 implementation begins.

It does not implement runtime code.
It does not redesign Platform Core.
It does not change Governance, OCS, Replay, HIRR, PPP, workers, providers, or
approval semantics.

## 1. Purpose

Generation 2 defines UBTR as the canonical semantic authority and introduces the
Canonical Semantic Artifact as the shared semantic input for Platform Core
consumers.

This creates a necessary boundary question:

What does UBTR own, and what must UBTR never own?

This specification answers that question by defining:

- UBTR responsibilities;
- non-responsibilities;
- shared responsibilities;
- explicitly forbidden responsibilities;
- implementation constraints for future migration work.

## 2. Boundary Principle

UBTR owns semantic translation and semantic orchestration.

UBTR does not own governance authority, approval authority, execution authority,
worker authority, provider authority, or replay authority.

The invariant remains:

```text
LLM proposes.
UBTR translates.
OCS governs cognition.
Governance constrains.
Human approves.
Workers execute.
Replay records.
```

## 3. Interaction Diagram

```text
Human
  |
  v
UBTR
  |
  |  produces
  v
Canonical Semantic Artifact
  |
  +--> HIRR / Workflow Routing
  |
  +--> OCS Cognition Governance
  |
  +--> Approval Runtime
  |
  +--> Worker Projection
  |
  +--> Explanation Rendering
  |
  v
Replay Evidence
```

UBTR sits before and beside Platform Core consumers as the semantic authority.
It does not replace the consumers.

## 4. Responsibility Matrix

| Responsibility | UBTR | OCS | Governance | Replay | Workers | Ownership Classification |
| --- | --- | --- | --- | --- | --- | --- |
| Semantic interpretation | Owns canonical interpretation. | May consume for cognition context. | Constrains allowed use. | Records semantic evidence. | None. | Owned by UBTR |
| Deterministic translation | Owns deterministic Human to Governance and Governance to Human translation. | None. | Constrains admissibility. | Records artifacts and hashes. | None. | Owned by UBTR |
| Ambiguity detection | Owns semantic ambiguity detection and ambiguity flags. | May consume ambiguity to govern escalation. | Constrains unsafe ambiguity. | Records ambiguity evidence. | None. | Owned by UBTR |
| Confidence evaluation | Owns semantic confidence scoring and thresholds for escalation request. | Consumes confidence for provider governance. | Defines fail-closed expectations. | Records confidence evidence. | None. | Owned by UBTR |
| Cognition escalation request | Creates bounded request when deterministic translation is insufficient. | Owns admissibility and execution of cognition workflow. | Constrains escalation policy. | Records request and decision. | None. | Shared |
| Provider selection | Specifies semantic need and required capability. | Selects eligible provider. | Constrains provider eligibility. | Records provider decision. | None. | Owned by OCS |
| Provider invocation | Never directly invokes providers. | Owns invocation through governed cognition path. | Constrains invocation. | Records request and response. | None. | Owned by OCS |
| Provider comparison | Requests comparison when semantic uncertainty remains. | Owns governed comparison execution. | Constrains comparison admissibility. | Records all comparison evidence. | None. | Owned by OCS |
| Consensus integration | Integrates provider comparison output into semantic artifact. | Supplies governed comparison result. | Constrains admissible synthesis. | Records integration lineage. | None. | Shared |
| Governance decisions | Supplies semantic evidence only. | May govern cognition-specific decisions. | Owns governance decisions. | Records decisions. | None. | Owned by Governance |
| Approval decisions | Supplies human-readable semantic context. | None. | Constrains approval model. | Records approval evidence. | None. | Owned by Human / Approval Runtime |
| Workflow routing input | Produces canonical semantic artifact consumed by routing. | None. | Constrains route admissibility. | Records route evidence. | None. | UBTR produces input; routing owns decision |
| Workflow routing decision | Must not select authoritative workflow by itself. | None. | Constrains routing. | Records route decision. | None. | Owned by Routing / HIRR |
| Execution authorization | Must never authorize execution. | None. | Constrains authorization. | Records authorization evidence. | None. | Owned by Approval / Governance |
| Worker projection | May describe intended worker need in semantic artifact. | None. | Constrains worker admissibility. | Records projection and later worker evidence. | Consume authorized worker request only. | UBTR may project; workers execute |
| Worker dispatch | Forbidden. | None. | Constrains dispatch. | Records dispatch evidence. | Execute authorized work. | Owned by Worker Runtime |
| Replay recording | Emits replay-safe translation evidence. | Emits cognition evidence. | Emits governance evidence. | Owns recording and reconstruction. | Emits worker evidence. | Owned by Replay |
| Evidence creation | Creates semantic evidence. | Creates cognition governance evidence. | Creates governance evidence. | Persists evidence. | Creates execution evidence. | Shared by evidence type |
| Explanation rendering | Produces semantic human-readable projection. | May provide cognition summary. | Constrains claims. | Records rendered explanation. | None. | Shared, UBTR owns semantic projection |
| LLM explanation output | May consume as non-authoritative provider-assisted wording. | Governs provider use if invoked through cognition path. | Constrains authority. | Records request and response. | None. | Advisory only |
| Replay mutation | Forbidden. | Forbidden. | Governance may define replay rules but not mutate history. | Owns append-only recording. | Forbidden. | Explicitly forbidden for UBTR |
| Governance mutation | Forbidden. | Forbidden except governed cognition evidence. | Owns governed changes through approved processes. | Records. | Forbidden. | Explicitly forbidden for UBTR |

## 5. UBTR-Owned Responsibilities

UBTR owns:

- natural language normalization;
- deterministic semantic translation;
- canonical semantic interpretation;
- ambiguity detection;
- semantic confidence evaluation;
- semantic escalation decision making;
- bounded cognition escalation request creation;
- canonical semantic artifact generation;
- semantic artifact hashing;
- semantic translation lineage;
- human-readable semantic projection;
- technical semantic projection;
- replay-safe semantic evidence emission.

Ownership means UBTR is accountable for producing semantic artifacts, not for
authorizing action.

## 6. OCS-Owned Responsibilities

OCS owns:

- governed cognition workflow execution;
- provider eligibility evaluation;
- provider selection;
- provider invocation;
- provider failure handling;
- capability-aware provider escalation;
- multi-provider comparison execution;
- cognition governance evidence;
- fail-closed cognition handling.

UBTR may ask OCS for cognition.
UBTR may not bypass OCS to contact providers directly.

## 7. Governance-Owned Responsibilities

Governance owns:

- governance constraints;
- admissibility rules;
- approval model constraints;
- fail-closed requirements;
- authority boundaries;
- certification and conformance expectations;
- governed mutation processes.

UBTR supplies semantic evidence to governance.
UBTR does not become governance.

## 8. Replay-Owned Responsibilities

Replay owns:

- append-only recording;
- deterministic reconstruction;
- replay identity;
- replay lineage;
- replay artifact persistence;
- replay evidence retrieval;
- replay source-of-truth semantics.

UBTR may emit semantic evidence for replay.
UBTR may not mutate replay, rewrite replay, delete replay, or reinterpret replay
history.

## 9. Worker-Owned Responsibilities

Workers own:

- authorized execution;
- bounded mutation;
- deterministic execution evidence;
- worker result reporting;
- worker fail-closed behavior.

UBTR may project that a worker could be needed.
UBTR may not dispatch a worker or authorize worker execution.

## 10. Shared Responsibilities

Some responsibilities are shared by evidence flow, not by authority.

### 10.1 Cognition Escalation

UBTR owns the semantic reason for requesting cognition.
OCS owns whether and how cognition is executed.
Replay records both.
Governance constrains the allowed boundary.

### 10.2 Consensus Integration

OCS owns governed provider comparison execution.
UBTR owns semantic integration into the canonical artifact.
Providers remain non-authoritative.
Replay records all intermediate artifacts.

### 10.3 Explanation

UBTR owns semantic projection.
Human-friendly explanation runtime owns operator presentation.
LLM-assisted explanation may provide advisory wording.
Replay records the explanation source and rendered output.

No explanation output can approve, authorize, execute, or override governance.

## 11. Explicitly Forbidden UBTR Responsibilities

UBTR must never:

- approve actions;
- reject actions as a human authority substitute;
- authorize execution;
- dispatch workers;
- invoke providers directly outside OCS governance;
- select providers as an authority;
- mutate replay;
- rewrite replay;
- delete replay;
- become governance;
- replace OCS;
- replace HIRR decision making;
- replace approval runtime;
- bypass workflow routing;
- bypass approval boundaries;
- bypass fail-closed behavior;
- treat provider output as authoritative;
- treat explanation output as authoritative;
- create hidden runtime mutation paths;
- silently change deterministic rules without governed approval;
- infer human approval from semantic confidence;
- infer execution authorization from provider confidence;
- transform proposal-only cognition into execution.

## 12. Authority Boundaries

### 12.1 Semantic Authority

UBTR is the canonical semantic authority.

This means UBTR owns the canonical representation of what the human request
means for Platform Core consumers.

It does not mean UBTR decides what the system is allowed to do.

### 12.2 Governance Authority

Governance remains the authority for admissibility, constraints, conformance,
and fail-closed requirements.

UBTR cannot weaken governance constraints.

### 12.3 Human Authority

Human authority remains final for approval, rejection, modification, and stop
decisions.

UBTR must preserve approval boundaries in all projections and artifacts.

### 12.4 Provider Non-Authority

Providers can only produce cognition artifacts.

Provider output may inform UBTR semantic synthesis, but it cannot become
approval, execution authorization, governance, or replay truth.

### 12.5 Replay Authority

Replay remains the source of truth for what happened.

UBTR semantic artifacts are replay evidence, not replay authority.

## 13. Implementation Constraints

Future UBTR implementation must:

- consume and produce deterministic schemas;
- preserve stable artifact hashes;
- preserve replay lineage;
- preserve workflow identity where known;
- preserve conversation identity;
- preserve translation lineage;
- preserve provider provenance;
- preserve ambiguity and confidence evidence;
- fail closed when semantic artifacts are malformed;
- fail closed when replay persistence fails;
- keep compatibility layers until each consumer is regression-protected;
- migrate consumers incrementally;
- avoid changes to governance, replay, approval, worker, and OCS semantics.

Future UBTR implementation must not:

- introduce new authority concepts;
- introduce hidden provider calls;
- introduce automatic execution;
- remove human approval;
- weaken deterministic replay;
- collapse OCS provider governance into UBTR;
- remove compatibility layers before migration evidence exists.

## 14. Future Extension Rules

Future extensions are allowed only when they preserve this boundary model.

Allowed extensions:

- richer ambiguity models;
- richer confidence models;
- additional provider capability metadata;
- improved multilingual normalization;
- additional canonical semantic artifact fields;
- better human-readable projections;
- replay-derived deterministic translation improvements after governed approval;
- compatibility layer retirement after regression coverage.

Forbidden extensions:

- UBTR executing workflows;
- UBTR dispatching workers;
- UBTR directly selecting or invoking providers outside OCS;
- UBTR approving or rejecting on behalf of humans;
- UBTR mutating governance;
- UBTR mutating replay;
- UBTR silently promoting learned semantic rules without governed approval.

## 15. Certification Implications

This boundary specification is required before Generation 2 implementation
because exclusive UBTR semantic authority increases centrality without
increasing execution authority.

Generation 2 certification must verify:

- UBTR is the exclusive producer of canonical semantic artifacts;
- consumers stop independently deriving semantic meaning after migration;
- OCS still governs provider cognition;
- Governance still constrains admissibility;
- Human approval remains required for execution;
- Workers execute only through authorized worker paths;
- Replay records every semantic and cognition decision;
- provider output remains non-authoritative.

## 16. Final Verdict

UBTR_RESPONSIBILITY_BOUNDARIES_FROZEN
