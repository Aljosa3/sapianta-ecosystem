# 1. Implementation Summary

Generation: G57-01

Report identity:
G57_01_TYPED_SEMANTIC_CONVERSATION_WORKING_MEMORY_ARCHITECTURE_REPORT_V1

Reporting date: 2026-07-31

Constitutional baseline:
AICLI_CODEX_EXECUTION_PATH_DIVERGENCE_CHARACTERIZED

Authenticated repository anchor:
9ce12b86efb183a22c41606b176e6dfc9f127c86

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G55-03 Conversation Working Memory Runtime Implementation Report V1
- G56-01 End-to-End AiCLI Development Flow Validation Report V1
- G56-02 Real Terminal Multi-Turn Development Characterization Report V1
- G56-03 AiCLI vs Codex Execution Path Equivalence Audit Report V1
- existing Conversation Boundary, Platform Core, Objective, Development
  Governance, Capability Selection, Replay, Authorization, Worker, PCBV31,
  G31, and G35 contracts

Objective:

Define an evidence-derived, deterministic, typed semantic Conversation
Working Memory architecture that preserves provisional human intent across
clarification rounds while remaining outside the certified execution pipeline
until explicit Objective Commitment.

Implementation scope:

- Authenticated the G55-03 isolated CWM substrate and the complete G56-01
  through G56-03 empirical evidence chain.
- Derived a minimal semantic-slot taxonomy from the observed Objective drift,
  repeated clarification, cross-invocation discontinuity, constraint
  misclassification, artifact-remediation loop, and output-relevance findings.
- Defined slot identity, ownership, lifecycle, completeness, confidence,
  provenance, revision history, dependencies, normalization, clarification,
  contradiction handling, rollback, conversation state, and bounded
  projection.
- Defined the one-way Objective Commitment boundary and fail-closed conditions.
- Assessed G55-03 compatibility, required V2 extensions, migration, future
  implementation order, constitutional classification, and risks.

Modified modules:

- `docs/governance/G57_01_TYPED_SEMANTIC_CONVERSATION_WORKING_MEMORY_ARCHITECTURE_REPORT_V1.md`:
  this architecture-only G48 evidence report.

Intentionally unchanged modules:

- The G55-03 CWM runtime and tests.
- AiCLI, Human Interface Runtime, Conversation Boundary, Admission,
  Platform Core project services, Objective inference, Development
  Governance, and Capability Selection.
- Replay, Authorization, Worker lifecycle, completion adapters, G31, G35,
  PCBV31, and every execution contract.

Architectural boundaries preserved:

- The proposed model is not a production call site and grants no CWM
  integration authority.
- Typed slots are provisional mutable working state, not constitutional or
  Replay artifacts.
- Explicit authenticated capability admission continues to take precedence;
  CWM cannot reinterpret or select a capability.
- `CANDIDATE_READY` is not Objective Commitment, execution approval,
  Authorization, or Worker eligibility.
- Only the existing Objective owner may create an immutable Objective after a
  future separate commitment gate validates exact human commitment.

## Executive Summary

The G56 evidence supports a second-generation CWM, but not unchanged
integration of G55-03. The existing runtime is a sound storage and isolation
substrate: it already provides canonical JSON, integrity checks, atomic
replacement, monotonic revisions, locking, TTL, bounded state, workspace and
session isolation, and explicit non-authority flags. Its semantic model is too
coarse because `topic`, `entities`, `inferred_intent`, free-form facts,
assumptions, ambiguities, and one scalar confidence value cannot preserve the
distinct action, subject, outcome, constraints, scope, and evidence state
proven necessary by G56.

The proposed V2 architecture therefore retains the G55-03 substrate and
replaces free-form meaning as the primary representation with twelve closed,
typed slot classes. Each slot has a stable session-local identity, cardinality,
canonical value, explicit status, ordinal confidence class, local provenance,
dependencies, and bounded revision history. Clarification is driven by exact
missing, conflicted, stale, or unconfirmed slots. Equivalent answers resolve
one semantic identity rather than appending prose. Contradictions create a
conflict; they never silently use “latest text wins.”

The design intentionally ends at a non-authoritative Objective candidate.
Commitment requires a future separately certified gate, an exact CWM revision
and digest, complete required slots, no material conflicts, a bounded
projection, and explicit human commitment. Only then may the candidate be
submitted to the existing Objective runtime. No integration or commitment
runtime is implemented by G57-01.

# 2. Code Evidence

No runtime code was added or changed. This section records authenticated
existing evidence and the proposed architecture. All proposed structures are
architectural contracts, not implemented APIs or artifacts.

## Authenticated Evidence Inventory

| Evidence | Commit | Report SHA-256 | Architectural use |
|---|---|---|---|
| G55-03 isolated CWM runtime | `6e9f7edab143cf50757507324ea7a417cee40cb1` | `1c8de6fecb34787a47495c3d527fa6eccde54c1f391cb440bd9091a5f557074c` | Establishes safe mutable storage and non-authority substrate. |
| G56-01 workflow validation | `46fcbe8d4cd104cd7c736069b0b0b98724384647` | `3f1873652063e386f245311a632c21c3a3ed24e96dce731ca83c36da685cd4a6` | Establishes when CWM is useful and where it must not be universally inserted. |
| G56-02 multi-turn characterization | `bc85641eb9a49bdde5a6fc902a85adc11d8ce894` | `bb6c1abdceb5662d4eab914990f7f26e33625a429f47a3291e27e192ea3f9907` | Supplies slot, clarification, repetition, drift, and continuity evidence. |
| G56-03 path-equivalence audit | `9ce12b86efb183a22c41606b176e6dfc9f127c86` | `c382a912bda542bcd7c3e9f5e10dd55d5d6cccf73868a8fa06f7af7d5fa9e604` | Locates conversational limitation before Objective and excludes downstream owners as the cause. |

The commits form one direct parent chain from G55-03 through G56-03. The
architecture does not rely on unattested external conversational evidence.

## Constitutional Rationale

G56 establishes two complementary facts:

1. the certified execution pipeline functions without CWM; and
2. provisional multi-turn understanding can lose or inflate semantic content
   before Objective Commitment.

Therefore the repair belongs in mutable human-intent conversation state, not
in Objective, Development Governance, Capability Selection, Replay,
Authorization, Worker, or G31. The required separation is:

```text
Human conversation
  -> provisional typed semantic state
  -> explicit human review
  -> Objective Commitment boundary
  -> existing immutable Objective owner
  -> existing certified execution pipeline
```

An explicit authenticated capability request remains governed by existing
admission precedence and bypasses generic CWM refinement. CWM is applicable
only to generic or ambiguous conversational development continuity after that
precedence decision. It does not participate in capability selection.

## Empirical Justification from G56

| G56 observation | Measurement | Required architectural response |
|---|---:|---|
| First-turn semantic clarification was common in G56-01 | 3 of 5 semantic scenarios | Required-slot completeness and targeted clarification. |
| Cross-invocation workspace restoration lacked usable semantic accumulation | T2 required a complete new 89-character request | Session-restorable typed values independent of full prior prose. |
| Objective subject drifted across clarification | T3: terminal status summaries -> capability name -> `focused tests` | Stable `OPERATIVE_ACTION` and `OPERATIVE_SUBJECT` slots that constraints/tests cannot replace. |
| Clarification inflated the canonical request | T3: 294 human characters -> 514 canonical, then 534 with prefix against 240 | Typed projection and deduplication; no transcript concatenation. |
| User repeated almost the entire original request | T3 final answer repeated 16 of 17 normalized tokens | Preserve completed slots and ask only for the triggering slot. |
| Equivalent desired outcomes did not discharge one question | T4: four answers, 261 characters | Stable desired-outcome identity and deterministic equivalence/confirmation. |
| Invalid artifact reference caused repeated ingress attempts | T4: five attempts | Owner-scoped attachment disposition separate from Objective refinement. |
| Safety constraints became capability candidates | G56-01 S4 | Typed preservation constraints excluded from capability hints. |
| Explicit paths were weakened in the proposal | G56-01 S3 | Preserve exact human-supplied scope references without inventing authentication. |
| Successful completion did not ensure answer relevance | G56-02 T5 | Desired outcome and output/acceptance criteria remain distinct. |
| Full raw memory would worsen expansion | G56-02 recommendation | Raw prose may support provenance but cannot be the primary semantic state. |
| AiCLI/external Codex diverge before HIR | G56-03 | CWM architecture is transport-neutral and cannot repair downstream owners. |

These findings justify the model below. No slot is included solely because it
is conventional in a chatbot memory design.

## Existing Public API and Substrate

G55-03 already exposes create, load, recover, update, replace, cleanup,
validate, and state-path APIs. Its exact non-authority boundary is:

```python
_BOUNDARY_FIELDS = {
    "runtime_owner": PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_OWNER,
    "constitutional_artifact": False,
    "constitutional_authority": False,
    "replay_visible": False,
    "authorization_eligible": False,
    "worker_eligible": False,
    "objective_creation_supported": False,
    "capability_routing_supported": False,
}
```

The lifecycle currently permits mutable `EXPLORING` and `CANDIDATE_READY`
states and rejects commit entry:

```python
MUTABLE_LIFECYCLE_STATES = frozenset({EXPLORING, CANDIDATE_READY})
```

```python
def _mutable_lifecycle(value: Any) -> str:
    if value not in MUTABLE_LIFECYCLE_STATES:
        raise FailClosedRuntimeError(
            "commit lifecycle is reserved for a future commitment runtime"
        )
```

The architecture preserves these controls. It does not repurpose
`CANDIDATE_READY` as commitment.

## Proposed Architecture Overview

```text
Existing explicit-capability admission precedence
  |
  +-- explicit authenticated capability established
  |     -> existing certified capability path; CWM not read
  |
  +-- generic or ambiguous conversation
        -> V2 typed CWM session
             -> normalize one human turn into slot deltas
             -> validate provenance and dependencies
             -> detect duplicate / conflict / stale state
             -> ask one slot-bound clarification when needed
             -> project bounded candidate when ready
             -> human reviews exact projection
             -> future Objective Commitment Gate
                  -> existing Objective owner
                  -> existing certified pipeline
```

The architecture has five internal responsibilities:

1. a closed typed-slot schema;
2. deterministic normalization into proposed slot deltas;
3. revision-safe slot application and history;
4. slot-bound clarification and readiness calculation; and
5. a non-authoritative bounded Objective candidate projector.

It has no run, route, authorize, execute, dispatch, Replay-write, Worker, or
Objective-create operation.

## Typed Semantic Slot Record

The proposed logical record is:

```text
semantic_slot:
  slot_id: session-local stable identifier
  slot_type: one closed taxonomy value
  cardinality_key: primary or deterministic collection key
  value_kind: ENUM | TEXT | PATH | REFERENCE | CLAUSE
  surface_value: bounded exact human fragment
  canonical_value: bounded typed value
  equivalence_key: local semantic deduplication key
  status: PROPOSED | ASSERTED | CONFIRMED | CONFLICTED | STALE
  completeness: EMPTY | PARTIAL | COMPLETE | CONFLICTED | STALE
  confidence_class: CONTEXT_DERIVED | DETERMINISTIC_NORMALIZATION |
                    HUMAN_ASSERTED | HUMAN_CONFIRMED | CONFLICTED
  materiality: REQUIRED | CONDITIONAL | OPTIONAL
  depends_on: ordered session-local slot identifiers
  provenance: ordered bounded local provenance entries
  slot_revision: monotonic integer
  history: ordered bounded revision events
```

`slot_id`, `equivalence_key`, and local digests are mutable-store identifiers
only. They MUST NOT be named or used as constitutional artifact, Replay,
Objective, Authorization, or Worker identities.

### Slot identity

- A single-valued slot uses `slot_type + cardinality_key=primary`.
- A multi-valued slot uses `slot_type + canonical qualifier key`, not insertion
  order, so repeated equivalent statements address the same slot.
- Identity remains stable when a value is corrected; the correction increments
  `slot_revision` and appends history.
- A new materially independent value receives a new collection key.
- Slot identity is scoped to the exact workspace and conversation session and
  is meaningless outside that CWM state.

### Slot ownership

- Human Authority owns the meaning of explicit human assertions and
  confirmations.
- `PLATFORM_CORE_HUMAN_INTENT_CONVERSATION` owns only provisional slot storage,
  normalization proposals, completeness calculation, and clarification state.
- Artifact ingress or another existing evidence owner owns any referenced
  attachment disposition; CWM may cache an opaque owner result but cannot
  validate or authenticate it.
- Platform Core Objective owns committed Objective semantics.
- Capability Selection, Development Governance, Replay, Authorization, and
  Worker owners receive no CWM authority.

### Completeness and confidence

Completeness is deterministic and per slot:

- `EMPTY`: no candidate value;
- `PARTIAL`: a typed structure lacks a required component;
- `COMPLETE`: the value passes its closed type validator;
- `CONFLICTED`: two non-equivalent active candidates exist;
- `STALE`: a context-sensitive value requires owner revalidation.

Confidence is ordinal evidence classification, not a probabilistic score:

1. `HUMAN_CONFIRMED` — the human confirmed the exact canonical projection;
2. `HUMAN_ASSERTED` — the human directly supplied the value;
3. `DETERMINISTIC_NORMALIZATION` — closed mechanical rules transformed a
   direct assertion without adding semantics;
4. `CONTEXT_DERIVED` — context suggests a value, but commitment requires
   clarification or confirmation;
5. `CONFLICTED` — no active value is eligible.

The G55-03 global floating `confidence` value cannot be used to make a slot
commitment-eligible.

### Provenance

Each provenance entry contains only bounded local working-memory data:

- source kind: `HUMAN_TURN`, `CLARIFICATION_REPLY`, `PRIOR_SLOT`, or
  `OWNER_DISPOSITION`;
- session-local turn number;
- source CWM revision;
- bounded source span or exact supplied fragment;
- local content digest;
- applied normalization rule identifiers; and
- human assertion/confirmation disposition.

It MUST NOT use reserved `artifact_*`, `replay_*`, `objective_*`,
`authorization_*`, or `worker_*` identity fields. A reference supplied by
another owner remains explicitly opaque and carries no authentication claim
inside CWM.

## Semantic Slot Taxonomy

The V2 taxonomy is closed and versioned. Questions and confirmation events are
control records, not additional open-ended semantic slot classes.

| Slot type | Cardinality | Commitment role | Empirical basis |
|---|---|---|---|
| `OPERATIVE_ACTION` | One primary | Required | T1 lacked actionable direction; T3 action was later obscured. |
| `OPERATIVE_SUBJECT` | One primary | Required | T3 subject drifted to capability and test fragments. |
| `DESIRED_OUTCOME` | One primary, optional secondary outcomes | Required primary | T4 repeated equivalent desired outcomes without resolution. |
| `WORK_TYPE` | One enum | Required | G56 distinguishes analysis from implementation and mutation boundaries. |
| `SCOPE_REFERENCE` | Multiple typed paths/components | Conditional | S3 supplied an exact path that later appeared unresolved. |
| `PRESERVATION_CONSTRAINT` | Multiple clauses | Optional but binding when present | Replay/Authorization preservation was misread as capability candidacy. |
| `OUTPUT_REQUIREMENT` | Multiple clauses | Conditional | “Return only” constraints differ from the desired semantic outcome. |
| `ACCEPTANCE_CRITERION` | Multiple clauses | Conditional | Focused tests must not replace the operative subject. |
| `CAPABILITY_HINT` | Multiple advisory identifiers | Optional, never selecting | T3 human named `human_interface`; selection remains an external owner. |
| `EVIDENCE_REFERENCE` | Multiple opaque references | Conditional | Explicit capability required authenticated evidence; CWM cannot create it. |
| `CONTEXT_SCOPE` | Multiple workspace/environment qualifiers | Conditional | T2 demonstrated session restoration without usable semantic continuity. |
| `ASSUMPTION` | Multiple propositions | Optional; material assumptions require confirmation or removal | G55-03 already stores assumptions; silent assumptions cannot cross commitment. |

`confirmed decisions` are represented by slot status and confirmation history,
not duplicated into another semantic slot. `unresolved questions` are derived
clarification-control records keyed to the slot that caused them. Generic
`entities` are represented within typed subject, scope, evidence, or context
values rather than retained as an unbounded semantic category.

## Slot Dependency Model

| Slot | Dependencies | Rule |
|---|---|---|
| `OPERATIVE_ACTION` | None | Must be an explicit or human-confirmed action. |
| `OPERATIVE_SUBJECT` | `OPERATIVE_ACTION` | Must identify what the action operates on. |
| `DESIRED_OUTCOME` | Action and subject | Must describe the observable postcondition, not an implementation step. |
| `WORK_TYPE` | Action | May be deterministically normalized only from closed work-type markers. |
| `SCOPE_REFERENCE` | Subject | Narrows subject; cannot create or authenticate a path. |
| `PRESERVATION_CONSTRAINT` | Action or subject | Restricts execution; never becomes an operative target by itself. |
| `OUTPUT_REQUIREMENT` | Desired outcome | Governs presentation/format, not semantic result identity. |
| `ACCEPTANCE_CRITERION` | Desired outcome | Tests satisfaction and cannot replace action/subject. |
| `CAPABILITY_HINT` | Action and subject | Remains advisory until the external capability owner acts after commitment. |
| `EVIDENCE_REFERENCE` | Relevant subject or hint | Requires an external owner disposition before evidence-dependent commitment. |
| `CONTEXT_SCOPE` | None | Becomes stale if workspace/session context changes. |
| `ASSUMPTION` | Any referenced slot | Material assumptions block commitment until confirmed or discarded. |

A dependency change marks dependent values `STALE` unless the new dependency
has the same equivalence key. Stale values are not silently retained as
commitment-ready.

## Semantic Normalization Model

Normalization uses a versioned closed ruleset and produces slot-delta
proposals. It never directly commits an Objective.

### Deterministic normalization order

1. normalize line endings and Unicode to one declared form;
2. preserve quoted literals, paths, identifiers, and opaque references exactly;
3. segment clauses using closed punctuation and conjunction rules;
4. classify clause role as operative action, subject, desired outcome, work
   type, scope, preservation, output, acceptance, capability hint, evidence,
   context, or assumption;
5. apply only registered enum and lexical equivalence rules;
6. validate the typed value;
7. calculate the local equivalence key;
8. compare with the active slot and emit `NO_CHANGE`, `ADD`, `REFINE`,
   `CONFLICT`, `CONFIRM`, or `WITHDRAW`;
9. apply the delta through exact expected-revision control; and
10. recompute clarification and candidate readiness.

### Safe equivalence rules

- Whitespace and case differences may normalize where the value kind declares
  them non-semantic.
- Known work-type synonyms may map to one closed enum only when existing
  human-intent terminology already establishes equivalence.
- Delivery phrasing such as “return,” “produce,” or “the user receives” may
  normalize into the same output predicate while preserving the object value.
- Exact duplicate preservation clauses, tests, and scope references collapse
  by equivalence key.
- Human correction markers such as “instead,” “replace,” or “I mean” may
  propose replacement, but the old value remains in history.

### Prohibited normalization

- Constraints cannot become actions, subjects, or capability hints.
- Tests cannot replace the desired outcome or subject.
- Paths cannot lose extensions or be authenticated by normalization.
- `evidence` and `artifact` are not assumed equivalent unless a versioned rule
  or explicit human confirmation establishes it for the active conversation.
- A capability hint cannot become capability selection.
- A newer utterance cannot silently override a confirmed non-equivalent value.
- Raw turns cannot be concatenated to form the canonical candidate.

When no closed rule proves equivalence, the values remain distinct and trigger
one contrast clarification. This is safer than over-normalizing T4 while still
preventing repeated identical questions after the human confirms equivalence.

## Clarification Model

Clarification is a deterministic consequence of typed state. Each question is
bound to one triggering slot and one state revision.

### Trigger precedence

1. active material contradiction;
2. missing required `OPERATIVE_ACTION`;
3. missing required `OPERATIVE_SUBJECT`;
4. missing required primary `DESIRED_OUTCOME`;
5. missing or conflicted `WORK_TYPE`;
6. material unconfirmed assumption;
7. stale conditional scope/evidence disposition;
8. partial output or acceptance requirement only when the human made it
   material.

Optional absent slots do not trigger clarification.

### Clarification control record

```text
clarification:
  clarification_id: session-local control identity
  trigger_slot_id: exact slot identity
  trigger_reason: MISSING | PARTIAL | CONFLICTED | STALE | UNCONFIRMED
  state_revision: exact CWM revision
  candidate_values: bounded ordered values
  question_template_id: closed deterministic template
  clarification_fingerprint: local digest of trigger and candidates
  status: PENDING | ANSWERED | RESOLVED | CANCELED | FAILED_CLOSED
```

The rendered question states the currently understood action, subject, or
outcome and asks only for the missing or conflicting value. A clarification
reply updates only the addressed slot unless it explicitly corrects another
slot.

### No-progress and termination rules

- The same unresolved fingerprint MUST NOT be emitted repeatedly without a
  state change.
- An equivalent answer resolves the same slot; it does not create a new prose
  turn in the candidate.
- If a reply produces no slot delta, the next response must offer an explicit
  `confirm current value`, `correct value`, or `cancel/suspend` choice rather
  than repeat the same question.
- If the human does not choose a valid transition, the session suspends or
  fails closed; it does not loop indefinitely.
- Clarification terminates when every required slot is complete, no material
  slot is conflicted or stale, all material assumptions are confirmed or
  removed, owner-required evidence dispositions are valid, and the exact
  bounded projection is reviewable.

Measurable completion is therefore a state predicate, not a conversational
intuition:

```text
required_incomplete_count == 0
material_conflict_count == 0
material_stale_count == 0
unconfirmed_material_assumption_count == 0
pending_clarification_count == 0
candidate_projection_valid == true
```

## Semantic Revision Model

Every accepted turn creates at most one global CWM revision and one revision
event for each changed slot. Revision numbers never decrease.

### Replacement and conflict rules

- Exact equivalent value: `NO_CHANGE`, provenance may be extended without
  duplicating the slot.
- More specific compatible value: `REFINE`, previous value retained in history.
- Explicit correction of one value: `REPLACE`, old value becomes
  `SUPERSEDED` in history.
- Non-equivalent value without correction: `CONFLICT`; both candidates remain
  visible and commitment is blocked.
- Withdrawal: active value becomes absent and history records `WITHDRAWN`.
- Lower-confidence input cannot replace a higher-confidence active value.
- No update uses “last message wins.”

### Stale information

- Workspace-dependent paths and environment context become stale when the
  canonical workspace identity changes.
- Evidence disposition becomes stale when its external owner declares a new
  state or the referenced attachment changes.
- Action, subject, outcome, and human-confirmed constraints do not become stale
  merely because time passes; the bounded conversation itself expires under
  TTL.

### Semantic rollback

Rollback is a new forward revision that reapplies a prior validated slot value
and records `ROLLBACK_TO_SLOT_REVISION`. It never decrements global or slot
revision and never deletes intervening history. Rollback is permitted only
before Objective Commitment. After commitment, any changed intent requires a
new conversation candidate and the existing Objective owner's governed
supersession procedure; CWM cannot mutate the immutable Objective.

History is bounded. Reaching the bound fails closed or requires explicit
session closure and a new session; history is never silently truncated in a
way that would make conflict or rollback evidence disappear.

## Conversation State Model

Semantic readiness and session availability are separate dimensions.

### Semantic readiness

```text
EXPLORING
  -> EXPLORING             valid partial update
  -> CANDIDATE_READY       completion predicate satisfied

CANDIDATE_READY
  -> EXPLORING             correction, conflict, staleness, or withdrawal
  -> CANDIDATE_READY       equivalent confirmation or compatible refinement
  -> COMMITTING            future Objective Commitment Gate only

COMMITTING
  -> COMMITTED             future gate plus Objective-owner acceptance only
  -> CANDIDATE_READY       future gate rejects before Objective creation
```

G55-03 continues to permit only the first four mutable transitions involving
`EXPLORING` and `CANDIDATE_READY`. `COMMITTING` and `COMMITTED` remain
unimplemented placeholders until a separately authorized gate exists.

### Session availability

```text
ABSENT
  -> ACTIVE                create

ACTIVE
  -> SUSPENDED             explicit pause or transport disconnect policy
  -> EXPIRED               TTL observed
  -> CLEANED               validated explicit cleanup

SUSPENDED
  -> ACTIVE                exact identity/revision restore
  -> EXPIRED               TTL observed
  -> CLEANED               validated explicit cleanup

EXPIRED
  -> CLEANED               deterministic recovery cleanup
```

`RESTORED` is a transition event from `SUSPENDED` to `ACTIVE`, not a durable
steady state. Restore validates workspace identity, session identity, schema,
integrity, revision, bounds, and TTL before allowing further updates. A
restarted process cannot infer missing semantics from raw conversation logs.

Expiration and cleanup remain local mutable-store operations and create no
Replay artifact. Explicit closure may clean immediately; suspension preserves
state only until the bounded TTL.

## Objective Candidate Projection

The candidate projector serializes only active typed values in fixed taxonomy
order. It never concatenates turns, questions, or full provenance.

```text
candidate_objective_projection:
  action
  subject
  desired_outcome
  work_type
  scope_references[]
  preservation_constraints[]
  output_requirements[]
  acceptance_criteria[]
  capability_hints[]          advisory only
  evidence_references[]       opaque; owner disposition required
  context_scope[]
  confirmed_assumptions[]
  source_cwm_revision
  local_candidate_digest
  normalization_ruleset_version
```

The projection is deterministic, bounded, and contains no Objective, Replay,
Authorization, Worker, or constitutional identity. Its character/byte size is
calculated before human review. If the downstream admission contract's bound
cannot be satisfied without losing a required typed value, candidate readiness
fails closed; CWM does not call or bypass G31.

## Objective Commitment Boundary

Objective Commitment is a separate future constitutional transition, not a
CWM update API.

### Commitment criteria

All of the following are required:

1. session availability is `ACTIVE` and unexpired;
2. semantic readiness is `CANDIDATE_READY`;
3. the submitted workspace, session, revision, and candidate digest exactly
   match the validated CWM state;
4. every required slot is complete;
5. no material conflict, stale value, or unresolved question exists;
6. every material assumption is human-confirmed or removed;
7. any evidence-dependent request has a valid disposition from its existing
   evidence owner;
8. the deterministic projection is within its declared bound;
9. the human has reviewed the exact projection; and
10. Human Authority supplies an explicit commitment decision bound to that
    exact revision and digest.

### Commitment authority and operation

```text
Mutable CWM candidate
  -- exact human commitment --> Future Objective Commitment Gate
       -- validates only; no semantic invention --> Existing Objective owner
            -- creates immutable Objective --> Existing certified pipeline
```

- CWM may prepare but cannot accept commitment.
- The future gate owns only the transition validation and one-way handoff.
- Human Authority authorizes commitment of the reviewed meaning.
- The existing Objective runtime remains the only owner of immutable Objective
  creation and Objective identity.
- The gate must not select a capability, authorize execution, dispatch a
  Worker, or write Replay on behalf of downstream owners.
- Any constitutional/Replay evidence of commitment is written by existing
  constitutional owners after the boundary, never by mutable CWM storage.

### Rejection and fail-closed behavior

Commitment is rejected for stale revision, digest mismatch, expired or
suspended state, missing slots, conflict, stale context, unconfirmed material
assumption, invalid evidence disposition, oversize projection, normalization
ruleset mismatch, absent exact human decision, or any forbidden authority
field. Rejection creates no Objective and no execution eligibility. The CWM
state remains `EXPLORING` or returns from future `COMMITTING` to
`CANDIDATE_READY` only under the separately certified gate contract.

## Constitutional Separation Assessment

| Owner/subsystem | Before Objective Commitment | At boundary | After accepted commitment |
|---|---|---|---|
| Replay | No CWM read/write; working root remains excluded | CWM does not write Replay | Existing owners record resulting Objective/pipeline evidence |
| Authorization | No import, token, request, or eligibility | No execution authorization | Existing Authorization acts later if required |
| Worker | No identity, selection, request, dispatch, or result | No Worker action | Existing Worker lifecycle acts later |
| Development Governance | Not invoked | No planning disposition | Receives committed Objective through existing order |
| Capability Selection | Capability hints remain advisory; explicit capability path bypasses CWM | No selection | Existing owner resolves after commitment under existing precedence |
| Objective runtime | No Objective creation or identity | Receives exact committed projection from future gate | Owns immutable Objective |
| PCBV31 | No import, identity, mutation, or membership change | Unchanged | Unchanged |
| G31 | No preflight, limit change, or bypass | No G31 call by CWM | Existing chain evaluates its own downstream artifact |
| Conversation Boundary | No G57 implementation or call site | Future adapter requires separate authorization | Remains transport/boundary owner |

The architecture adds no downstream semantic interpretation responsibility.
The candidate projection is complete before it crosses the boundary.

## G55-03 Migration Assessment

### Sufficient unchanged substrate

- runtime owner and non-authority flags;
- `.platform-core-working/conversation` storage isolation;
- canonical JSON and local SHA-256 integrity;
- workspace/session hashing and validation;
- monotonic revision control and stale-writer rejection;
- global lock and atomic replacement;
- owner-only permissions and path safety;
- TTL, deterministic expiration, cleanup, and restart recovery;
- storage, text, collection, and candidate bounds; and
- `EXPLORING`/`CANDIDATE_READY` plus reserved commitment states.

### Required versioned extensions

- V2 exact schema with typed `semantic_slots`;
- per-slot status, completeness, confidence class, provenance, dependencies,
  revision, and history;
- normalization ruleset version and applied rule identifiers;
- clarification control queue and no-progress fingerprint;
- owner-scoped evidence/attachment disposition references;
- separate session availability and semantic readiness;
- deterministic typed candidate projection; and
- a future, separate Objective Commitment Gate contract.

G55-03 V1 rejects unexpected fields by design. Therefore unchanged V1 cannot
represent V2 by adding ad hoc keys, and typed slots must not be hidden inside
the arbitrary candidate snapshot. A new exact schema version is required.

### Components no longer primary

- global `topic` becomes presentation-only;
- free-form `entities` are replaced by typed subject/scope/reference values;
- global `inferred_intent` is replaced by action, subject, outcome, and work
  type slots;
- free-form `confirmed_facts`, `assumptions`, and ambiguity lists become typed
  slots/control records with provenance;
- scalar global `confidence` cannot authorize readiness;
- global `discarded_interpretations` becomes per-slot revision history; and
- arbitrary candidate snapshot becomes the closed projection model.

These V1 fields may remain readable for backward compatibility but cannot be
the V2 source of commitment eligibility.

### Migration path

1. Continue to validate all V1 state with the unchanged V1 validator.
2. New sessions use V2 only after a future implementation is certified.
3. A V1 session may expire normally or enter explicit read-only migration.
4. Migration copies V1 values into bounded `LEGACY_RECONFIRMATION_REQUIRED`
   inputs; it does not silently map free text into confirmed slots.
5. V1 candidate snapshots remain opaque legacy candidates and cannot become
   `CANDIDATE_READY` under V2 without human review of the typed projection.
6. Migration writes a new versioned state atomically and preserves the V1
   source until the new state validates; no in-place destructive rewrite.
7. The scalar V1 confidence value is not converted into a per-slot confidence
   class.
8. No migration creates an Objective, Replay artifact, Authorization, or
   Worker request.

Compatibility result:

`G55_03_STORAGE_SUBSTRATE_COMPATIBLE_SEMANTIC_SCHEMA_EXTENSION_REQUIRED`

## Future Implementation Roadmap

This roadmap is planning evidence only. Every mutation requires a later
authorized generation.

| Order | Future step | Affected module family | Classification | Size | Constitutional impact |
|---:|---|---|---|---|---|
| 1 | Freeze G56 T1-T6 semantic fixtures and expected slot timelines | New focused tests/fixtures | Additive | Small | None; evidence only |
| 2 | Define V2 closed slot/schema models and validators | New isolated CWM V2 model module | Additive | Medium | No downstream owner change |
| 3 | Reuse G55-03 storage, lock, TTL, integrity, and atomic primitives through a versioned persistence adapter | Isolated CWM persistence | Compatible extension | Medium | Preserves non-authority/storage boundaries |
| 4 | Implement deterministic normalization and slot-delta engine | New isolated semantic normalization module | Additive | Medium | Proposal-only semantics; no Objective authority |
| 5 | Implement slot revision, conflict, staleness, rollback, and bounded history | CWM V2 state service | Compatible extension | Medium | Mutable-state only |
| 6 | Implement clarification queue, fingerprint, completion predicate, and typed projection | New isolated CWM services | Additive | Medium | No HIR or pipeline call site |
| 7 | Add ACTIVE/SUSPENDED restore semantics while retaining TTL cleanup | CWM V2 lifecycle | Compatible extension | Small | No Replay change |
| 8 | Implement explicit non-destructive V1-to-V2 migration | New migration utility | Additive | Small | No automatic semantic promotion |
| 9 | Run shadow-only characterization after explicit capability admission precedence | Future Conversation Boundary adapter and tests | Compatible extension requiring authorization | Medium | Reads CWM but cannot affect execution |
| 10 | Specify and implement Objective Commitment Gate | New separately owned gate plus Objective adapter | Constitutional change | Large | First mutable-to-immutable boundary; separate audit mandatory |
| 11 | Certify production generic-conversation integration | AiCLI/HIR/Conversation Boundary integration tests | Constitutional change | Large | Requires complete end-to-end re-certification |

Steps 1-8 can be developed and certified while remaining isolated. Step 9
must initially be observational. Steps 10-11 must not begin under G57-01 and
must preserve the current execution pipeline unchanged until separately
certified.

## Risk Assessment

| Risk | Evidence/trigger | Impact | Deterministic mitigation |
|---|---|---|---|
| Semantic drift | T3 subject changed twice | Wrong Objective candidate | Stable slot identities; constraints/tests cannot replace action or subject |
| Slot explosion | Open-ended entity/fact models | Unbounded state and clarification | Closed twelve-type taxonomy; hard cardinality and size bounds |
| Ambiguity persistence | T4 repeated one unresolved outcome | Infinite questioning | Slot fingerprint, no-progress transition, explicit confirm/correct/cancel |
| Contradictory intent | Non-equivalent later statements | Silent intent replacement | Conflict state; no latest-wins; human correction required |
| Over-normalization | Treating evidence/artifact or distinct scopes as equal | Loss of human distinctions | Closed rules only; preserve literals; ask contrast clarification |
| Under-normalization | T4 equivalent delivery phrasing | Repeated clarification | Versioned safe equivalence plus one human confirmation reusable in-session |
| Deterministic reproducibility | Rule/version or ordering drift | Different candidate from same state | Ruleset version, fixed taxonomy order, canonical JSON, exact revision/digest |
| Replay exclusion failure | Provenance mistaken for evidence | Mutable state enters constitutional lineage | Reserved identity rejection, separate working root, negative imports, local-only naming |
| Stale scope/evidence | Workspace or attachment changes | Candidate refers to invalid context | Dependency staleness and external owner disposition required |
| Raw-history reintroduction | Convenience concatenation | Repeats T3 over-bound expansion | Candidate projector accepts typed active values only |
| Premature capability influence | Capability hint treated as selection | Authority transfer | Advisory type flag; no registry/selection import; explicit path bypasses CWM |
| Future scalability | Global lock and bounded history | Contention or full state | Keep V1 safety initially; measure before any partitioning; fail closed at bounds |
| Commitment race | State changes after human review | Different Objective than approved | Exact expected revision and candidate digest at gate |
| Post-commit rollback attempt | Human changes intent after commitment | Mutation of immutable Objective | New candidate and existing governed supersession only |

The highest constitutional risks are over-normalization, premature capability
influence, Replay leakage, and commitment race. All four are fail-closed in the
architecture.

## Responsibility Boundaries

The proposed CWM V2 owns:

- bounded provisional typed state;
- deterministic proposal-only normalization;
- slot completeness and conflict calculation;
- clarification-control state;
- local revisions, history, TTL, and cleanup; and
- a non-authoritative bounded candidate projection.

It does not own:

- explicit capability admission or selection;
- canonical artifact authentication;
- immutable Objective creation;
- Development Governance;
- Replay evidence;
- Authorization;
- Worker selection, dispatch, execution, or completion;
- G31 synthesis or limits;
- PCBV31; or
- human constitutional authority.

# 3. Constitutional Self-Assessment

## Verified

- The architecture is derived from exact G56 scenario and measurement
  evidence rather than a generic conversational-memory design.
- The twelve-slot taxonomy separates the action, subject, outcome, work type,
  scope, constraints, output, tests, capability hints, evidence, context, and
  assumptions implicated by G56.
- Slot identity, ownership, lifecycle, completeness, confidence, provenance,
  dependency, revision, conflict, staleness, and rollback rules are defined.
- Equivalent expressions are deduplicated only through closed deterministic
  rules or exact human confirmation; unsupported equivalence fails closed.
- Clarification has exact triggers, per-slot binding, no-progress handling, and
  measurable termination criteria.
- Conversation ACTIVE, SUSPENDED, restored, expiration, and cleanup behavior
  is defined separately from semantic readiness.
- The Objective Commitment boundary requires exact revision/digest and human
  commitment and leaves immutable Objective creation with the existing owner.
- Replay, Authorization, Worker, Development Governance, Capability Selection,
  Objective runtime, PCBV31, and G31 remain outside CWM before commitment.
- G55-03 is retained as a compatible storage substrate while its unchanged V1
  semantic schema is correctly classified as insufficient.
- Migration does not silently promote V1 free text or confidence into
  commitment-eligible V2 slots.
- The future roadmap identifies the first constitutional change and prevents
  it from being smuggled into isolated CWM implementation.
- The unchanged G55-03 CWM and adjacent Conversation Boundary, admission,
  Objective, and task-intake suites passed 50 focused tests.
- Five governance conformance tests passed, and repository formatting is
  clean.
- No runtime, test, constitutional specification, or existing governance
  artifact changed.

## Not Verified

- No V2 schema, normalizer, slot engine, clarification engine, migration
  utility, availability lifecycle, candidate projector, or Objective
  Commitment Gate is implemented.
- The proposed equivalence rules have not been exercised against a broader
  multilingual or domain-diverse corpus. Unsupported equivalence must remain
  clarification-bound until separately certified.
- The proposed T4 outcome equivalence still requires either a versioned
  canonical vocabulary rule or one explicit human equivalence confirmation;
  this architecture does not claim that `evidence` and `artifact` are always
  equivalent.
- Maximum per-type slot counts, per-slot history length, and V2 serialized byte
  budgets require implementation measurement. G55-03 bounds remain the upper
  compatibility envelope, not proven V2 allocations.
- Crash safety for a future cross-file V1-to-V2 migration is not demonstrated.
- No production admission, Conversation Boundary, HIR, AiCLI, Objective, or
  downstream pipeline integration was run or authorized.
- No commitment or post-commit supersession behavior was executed.
- The repository conformance engine remains `PARTIALLY_CONFORMANT`: 18 checks
  passed and two pre-existing hook checks failed. It reports zero critical
  violations, but the root pre-commit hook is missing and the system
  pre-commit hook lacks `promotion_gate_v02` and `check_layer_freeze`. This
  architecture generation did not repair or hide that baseline drift.

# 4. Validation Matrix

Executed validation:

```text
python -m pytest -q \
  tests/test_g55_03_conversation_working_memory_runtime.py \
  tests/test_g49_02_platform_core_conversation_boundary.py \
  tests/test_g54_09_platform_core_admission_precedence.py \
  tests/test_g21_02_platform_project_objective_inference.py \
  tests/test_g47_r01_objective_task_intake_compatibility.py
python -m pytest -q tests/test_governance_conformance.py
python -m runtime.governance.governance_conformance_engine
git diff --check
```

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Empirical derivation | G56-01 scenarios; G56-02 timelines/statistics; G56-03 divergence | Mapped every slot/control responsibility to certified observation | PASS |
| Typed slot taxonomy | Twelve closed slot types and empirical-basis table | Reviewed against T1-T6 and G56-01 S1-S6 | PASS |
| Slot identity and ownership | Typed record and ownership rules | Deterministic architecture review | PASS |
| Slot lifecycle and completeness | Status/completeness models | State-transition review | PASS |
| Slot confidence | Ordinal confidence classes | Confirmed no probabilistic score grants readiness | PASS |
| Slot provenance | Local provenance contract and reserved-identity prohibition | Reviewed against G55-03 forbidden identity boundary | PASS |
| Slot revision history | Replacement/conflict/stale/rollback rules | Applied to T2, T3, and contradiction cases | PASS |
| Slot dependencies | Dependency matrix | Reviewed subject, outcome, constraints, scope, evidence, and staleness | PASS |
| Semantic normalization | Ordered rules and prohibited transformations | Applied to T3 constraints/tests and T4 outcome variants | PASS |
| Ambiguity and contradiction handling | Contrast clarification and conflict state | Fail-closed architecture review | PASS |
| Partial and incremental refinement | Per-slot delta/update rules | Applied to T1/T2 refinement evidence | PASS |
| Clarification trigger and termination | Trigger precedence, fingerprint, completion predicate | Applied to T3 repetition and T4 loop | PASS |
| Conversation lifecycle | ACTIVE/SUSPENDED/restore/expire/cleanup diagram | Compared with G55-03 TTL/recovery/cleanup substrate | PASS |
| Objective Commitment boundary | Criteria, authority, transition, rejection model | Confirmed CWM cannot commit or create Objective | PASS |
| Replay separation | Working root, reserved identities, one-way boundary | Compared with G55-03 non-Replay fields | PASS |
| Authorization separation | Separation matrix | No authorization input/output in proposed CWM | PASS |
| Worker separation | Separation matrix | No worker identity/request/dispatch/result | PASS |
| Development Governance separation | Separation matrix | Begins only after Objective owner | PASS |
| Capability Selection separation | Advisory hints and explicit-capability bypass | No capability selection inside CWM | PASS |
| PCBV31 and G31 compatibility | Separation matrix and bounded projector | No identity/limit modification or bypass | PASS |
| G55-03 compatibility | Substrate/extension/component inventory | Classified V1 storage compatible and V1 semantics insufficient | PASS |
| Migration path | Eight-step non-destructive migration model | Prevents silent semantic promotion | PASS |
| Future implementation sequence | Eleven-step roadmap with classification | First constitutional boundary isolated to later generation | PASS |
| Risk assessment | Fourteen-risk matrix | Required risks and mitigations documented | PASS |
| Existing isolated CWM and adjacent boundaries | Five focused test modules | 50 passed in 2.46 seconds | PASS |
| Governance diagnostic and limitation visibility | Conformance tests and engine | 5 tests passed; deterministic/read-only/fail-closed engine reported 18 passed checks, 2 known hook mismatches, and 0 critical violations | PASS |
| Repository formatting | New report and worktree | `git diff --check` | PASS |
| Runtime implementation | Explicit architecture-only restriction | No implementation required or performed | NOT_APPLICABLE |

# 5. Repository Mutation Summary

Modified files:

- `docs/governance/G57_01_TYPED_SEMANTIC_CONVERSATION_WORKING_MEMORY_ARCHITECTURE_REPORT_V1.md`:
  added this empirical architecture and evidence report.

Unchanged subsystems:

- G55-03 CWM runtime and tests.
- AiCLI, HIR, Conversation Boundary, Admission, Platform Core, Objective,
  Development Governance, Capability Selection, Replay, Authorization,
  Worker, completion, G31, G35, and PCBV31.
- All existing constitutional and execution artifacts.

API compatibility:

- No existing API, schema, runtime call site, storage file, transport,
  Objective, governance, capability, authorization, Worker, completion, or
  Replay contract changed.
- All proposed V2 APIs and schema fields remain unimplemented architecture.

Boundary preservation:

- The report grants no authority to integrate CWM.
- The current CWM remains isolated and mutable under its existing non-authority
  flags.
- The proposed commitment boundary cannot be entered without a future separate
  implementation and certification generation.
- No raw conversation history is declared constitutional evidence.

Unrelated pre-existing changes:

- None observed in the Git worktree. The conformance engine continues to expose
  the pre-existing root and system pre-commit hook drift declared under
  `Not Verified`.

# 6. Certification Verdict

TYPED_SEMANTIC_CONVERSATION_WORKING_MEMORY_ARCHITECTURE_CHARACTERIZED
