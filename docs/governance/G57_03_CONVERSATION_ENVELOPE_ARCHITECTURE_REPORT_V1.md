# 1. Implementation Summary

Generation: G57-03

Report identity: G57_03_CONVERSATION_ENVELOPE_ARCHITECTURE_REPORT_V1

Reporting date: 2026-07-31

Constitutional baseline:
TYPED_SEMANTIC_SLOT_TAXONOMY_REQUIRES_REVISION

Authenticated repository anchor:

- Commit: `ca3237ca4f242d09daa779b5177ba60913d01c16`
- Direct parent: `33dba4d42bfb8a18f8baa5c18e6e967a454c5591`
- Tree: `ce1366d25e3456bd8c50161f5e018e8c9f12a425`
- Subject: `G57-02: validate and minimize typed semantic slot taxonomy`

Implementation contracts:

- G48 Constitutional Evidence Reporting Standard V1
- G55-03 Conversation Working Memory Runtime Implementation Report V1
- G57-01 Typed Semantic Conversation Working Memory Architecture Report V1
- G57-02 Typed Semantic Slot Taxonomy Validation Report V1
- PCBV31 Baseline Identity Record V1

Objective:

Define the constitutional Conversation Envelope that owns bounded
conversation identity, scope, participation, availability, phase, and
candidate-binding metadata independently of semantic understanding. The
Envelope must compose deterministically with the existing G55-03 persistence
substrate, the six-class semantic model recommended by G57-02, and a future
Objective Commitment boundary without entering the certified execution
pipeline or acquiring constitutional authority.

Implementation scope:

- Defined the canonical Envelope data model and closed ownership boundary.
- Separated conversation availability from semantic readiness and Objective
  commitment.
- Defined deterministic conversation, workspace, session, interface, and
  participant bindings without treating those bindings as authentication.
- Defined lifecycle, phase derivation, suspension, restoration, expiration,
  closure, and cleanup transitions.
- Defined an active Objective-candidate binding containing only exact CWM
  revision and digest metadata, never candidate semantics or an Objective.
- Defined atomic interaction with G55-03 CWM, G57-02 typed semantic slots, and
  a future separately authorized Objective Commitment owner.
- Defined a fail-closed, versioned migration from G55-03 schema V1.
- Performed architecture and compatibility validation only. No runtime
  implementation was authorized or performed.

Modified modules:

- `docs/governance/G57_03_CONVERSATION_ENVELOPE_ARCHITECTURE_REPORT_V1.md`:
  this architecture-only G48 evidence report.

Intentionally unchanged modules:

- `aigol/runtime/platform_core_conversation_working_memory_runtime.py` and its
  tests: G55-03 remains the implemented V1 runtime.
- AiCLI, Human Interface Runtime, Platform Core, Objective, Development
  Governance, Capability, Replay, Authorization, Worker, and completion
  runtime: the certified execution path is outside this architecture.
- PCBV31 and every constitutional artifact: no identity, topology, authority,
  or baseline mutation was authorized.

Architectural boundaries preserved:

- The Envelope is local mutable working state, not a constitutional artifact,
  Replay record, Objective, capability route, authorization, or Worker request.
- Envelope identity is a local correlation identity only. It does not prove a
  human identity, authenticate a participant, or grant Human Authority.
- Semantic content remains owned by Semantic CWM. Envelope fields cannot
  contain operative action, subject, desired outcome, work type, qualifiers,
  semantic references, or free-form prompt text.
- The active candidate field is a binding to an exact semantic revision and
  digest. It cannot create, name, authorize, or execute an Objective.
- A single persisted CWM document and one global optimistic revision preserve
  atomicity; this architecture does not introduce a second state store.
- Expiration and cleanup remove local working state and create no Replay event,
  constitutional tombstone, or execution-side effect.

## Executive Summary

The canonical Conversation Envelope is a **logical component of the same
atomic CWM state document**, not a separate database, sidecar file, or runtime
authority. This is the smallest architecture compatible with G55-03: it reuses
the existing workspace/session isolation, lock, atomic write, integrity, TTL,
recovery, and revision controls while separating metadata from semantic
understanding.

The Envelope owns four kinds of information:

1. local correlation identity and immutable workspace/session bindings;
2. bounded participant and interface assertions;
3. availability lifecycle and deterministically derived conversation phase;
4. exact bindings to a Semantic CWM revision and, when present, its validated
   Objective-candidate digest.

Semantic CWM owns the six G57-02 semantic classes, provenance, conflicts,
clarification state, readiness, and candidate content. Constitutional owners
outside both components continue to own Objective creation, capability
selection, Development Governance, Replay, Authorization, Worker execution,
and completion.

The architecture therefore removes the `CONTEXT_SCOPE` overlap found in
G57-02 without moving semantic interpretation into metadata. It is compatible
with G55-03 only as a future versioned schema V2; V1 correctly rejects unknown
fields and must remain readable until a deterministic migration succeeds.

# 2. Code Evidence

No runtime code was added or changed. In this architecture generation, the
material evidence consists of authenticated predecessor artifacts, exact V1
runtime excerpts, the canonical model below, deterministic transition rules,
and validation against the existing runtime boundary.

## Authenticated Evidence Inventory

| Evidence | Git blob | SHA-256 | Architectural use |
|---|---|---|---|
| G57-02 taxonomy validation | `df1c7f5941eb1293bb4dc354116e5db0b589a84e` | `f02f2963d241900c94b4771c51124805d7fb8416b7f832ce52cd07b4a1b60e16` | Establishes the six semantic classes and moves `CONTEXT_SCOPE` into an Envelope. |
| G57-01 typed CWM architecture | `a48077d1075b5891beb531defcc207990eca823e` | `dfcb9f36502f334d9b9858c924df4a1d725d01b45ce768fc191463f195022086` | Establishes provisional semantics, clarification, semantic revision, and the future one-way commitment boundary. |
| G55-03 runtime report | `b019730293bce282c29bbc6b10576705d74c3094` | `1c8de6fecb34787a47495c3d527fa6eccde54c1f391cb440bd9091a5f557074c` | Establishes the implemented persistence, lifecycle, recovery, and non-authority substrate. |
| G55-03 runtime source | `e903bf29923b91e4fa4ffbe0cc6a5463a70ae981` | `6c144a8c10f97f56fa5177bf6c691d2bbbe7c139fea66dd2e8d30cc12277ab13` | Supplies exact current boundary fields, schema closure, identities, revision, TTL, and integrity behavior. |

## Existing Runtime Boundary

The following exact excerpt from
`aigol/runtime/platform_core_conversation_working_memory_runtime.py` defines
the non-authority boundary reused by the Envelope:

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

The following exact excerpt establishes the V1 persistence identities and
global revision fields that must be preserved by a future V2 schema:

```python
        "workspace_identity": workspace,
        "workspace_identity_hash": _identity_hash(workspace),
        "session_identity": session,
        "session_identity_hash": _identity_hash(session),
        "revision": 0,
        "lifecycle_state": EXPLORING,
```

The current `_STATE_FIELDS` validator is closed. Unknown Envelope or typed-slot
fields are therefore correctly rejected by V1. Compatibility requires a new
schema/runtime version; it does not permit an in-place reinterpretation of V1.

## Constitutional Rationale

G57-02 established that workspace, session, availability, suspension,
restoration, TTL, and cleanup are necessary conversation context but are not
semantic intent. Keeping those values as semantic slots would create two
owners for the same context: storage metadata and semantic memory. Moving all
semantic values into the Envelope would create the inverse error by making a
metadata component interpret human meaning.

The architecture therefore uses this ownership equation:

```text
Conversation state
  = Envelope(metadata, availability, bindings)
  + Semantic CWM(typed meaning, clarification, candidate content)

Constitutional execution state
  != Conversation state
```

The Envelope frames a conversation. It does not understand the request.
Semantic CWM understands provisionally. A future Objective Commitment owner,
not either mutable component, decides whether an exact candidate may cross
into the existing constitutional pipeline.

## Canonical Envelope Model

The proposed canonical identity is:

- Envelope type:
  `PLATFORM_CORE_CONVERSATION_ENVELOPE_SCHEMA_V1`
- Envelope runtime version:
  `PLATFORM_CORE_CONVERSATION_ENVELOPE_RUNTIME_V1`
- Runtime owner: `PLATFORM_CORE_HUMAN_INTENT_CONVERSATION`
- Persistence container: future
  `PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2`

The Envelope is nested beside `semantic_memory` in one state document:

```json
{
  "working_memory_type": "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2",
  "runtime_version": "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_RUNTIME_V2",
  "schema_version": "PLATFORM_CORE_CONVERSATION_WORKING_MEMORY_SCHEMA_V2",
  "runtime_owner": "PLATFORM_CORE_HUMAN_INTENT_CONVERSATION",
  "revision": 17,
  "envelope_revision": 5,
  "semantic_revision": 12,
  "envelope": {
    "envelope_type": "PLATFORM_CORE_CONVERSATION_ENVELOPE_SCHEMA_V1",
    "envelope_runtime_version": "PLATFORM_CORE_CONVERSATION_ENVELOPE_RUNTIME_V1",
    "conversation_identity": "conversation-local-sha256:<digest>",
    "workspace_identity": "<canonical-absolute-workspace>",
    "workspace_identity_hash": "<sha256>",
    "session_identity": "<bounded-session-identity>",
    "session_identity_hash": "<sha256>",
    "origin_interface_identity": "<closed-interface-identity>",
    "current_interface_identity": "<closed-interface-identity>",
    "participants": [],
    "context_scope": {},
    "availability_state": "ACTIVE",
    "conversation_phase": "COLLECTING",
    "semantic_memory_binding": {},
    "active_objective_candidate_binding": null,
    "created_at": "<canonical-UTC-timestamp>",
    "updated_at": "<canonical-UTC-timestamp>",
    "expires_at": "<canonical-UTC-timestamp>",
    "suspended_at": null,
    "restored_at": null,
    "closed_at": null,
    "constitutional_artifact": false,
    "constitutional_authority": false,
    "replay_visible": false,
    "authorization_eligible": false,
    "worker_eligible": false,
    "objective_creation_supported": false,
    "capability_routing_supported": false
  },
  "semantic_memory": {},
  "integrity_algorithm": "SHA256_CANONICAL_JSON",
  "integrity_checksum": "<sha256>"
}
```

This is a canonical architecture model, not an implemented schema. Every
object shown as `{}` requires a closed validator before implementation.

## Envelope Field Contract

| Field | Cardinality | Mutability | Deterministic rule | Explicit non-meaning |
|---|---:|---|---|---|
| `conversation_identity` | 1 | Immutable | Local digest derived once from canonical schema identity, workspace hash, session hash, and `created_at` | Not Replay, Objective, authorization, artifact, or person identity |
| `workspace_identity` and hash | 1 pair | Immutable | Reuse G55-03 canonical absolute identity and digest validation | Not semantic file or scope inference |
| `session_identity` and hash | 1 pair | Immutable | Reuse G55-03 bounded identity and digest validation | Not a transport credential |
| origin/current interface | 1 pair | Origin immutable; current explicitly rebindable | Closed identity vocabulary; rebind requires expected revision and participant confirmation | Does not make interfaces constitutionally equivalent |
| `participants` | 1 bounded set | Revisioned | Closed roles, opaque asserted identity, canonical sort, no duplicates | Not authentication, permission, or Human Authority proof |
| `context_scope` | 1 closed record | Revisioned | Contains only workspace/session/interface locality and scope revision | No operative subject, artifact inference, or semantic restriction |
| `availability_state` | 1 | State machine | Only transitions in the availability table are valid | Not semantic readiness or execution status |
| `conversation_phase` | 1 | Derived | Recomputed from validated CWM control state and commitment-boundary result | Not freely asserted and not Objective lifecycle |
| semantic-memory binding | 1 | Derived | Exact schema, global revision, semantic revision, and integrity digest | Does not copy semantic values |
| candidate binding | 0..1 | Derived | Exact semantic revision, projection ruleset, candidate digest, and review status | Does not contain candidate content or Objective identity |
| timestamps and TTL | 1 set | State-machine controlled | Canonical UTC, monotonic update, bounded TTL, explicit observed time | No wall-clock background authority |
| boundary flags | 1 fixed set | Immutable | Must exactly equal the G55-03 non-authority values | Cannot be promoted by stored data |

## Identity Model

### Conversation identity

`conversation_identity` is a local correlation key. Its conceptual input is:

```text
SHA256(
  canonical_json({
    "envelope_schema": fixed_schema_identity,
    "workspace_identity_hash": validated_workspace_hash,
    "session_identity_hash": validated_session_hash,
    "created_at": canonical_created_at
  })
)
```

The digest input is fixed and order-independent through canonical JSON. No
prompt text, semantic slot, username, credential, Objective identity, Replay
identity, Git commit, or nondeterministic random value is included. A duplicate
conversation identity at a different state path is rejected as copied state.

Changing workspace or session starts a new Envelope. Those identities cannot
be edited through an update call.

### Workspace and session identity

The workspace identity establishes storage locality. The session identity
establishes the bounded conversation instance within that workspace. Their
existing G55-03 hash checks remain authoritative for persistence validation.

Workspace identity does not authorize repository mutation. Session identity
does not authenticate a terminal, person, or provider. Neither may be inferred
from semantic slot values.

### Interface identity

The origin interface records where the Envelope was created. The current
interface records the explicitly bound transport after restoration. A future
closed vocabulary may include values such as `AICLI_TERMINAL` and
`CODEX_SESSION`, but equal vocabulary values do not imply equal context or
execution paths.

Cross-interface restoration is fail closed unless a separately specified
adapter supplies the exact conversation/workspace/session identities, expected
revision, valid integrity, unexpired TTL, and explicit participant
confirmation. The Envelope cannot infer continuity from similar prompt text.

### Participant identity

Each participant record has this conceptual form:

```json
{
  "participant_role": "HUMAN_ORIGINATOR",
  "asserted_identity": "<opaque-bounded-value>",
  "identity_source": "<closed-source-kind>",
  "binding_disposition": "ASSERTED_NOT_AUTHENTICATED",
  "first_bound_revision": 0,
  "last_confirmed_revision": 0
}
```

Allowed initial roles are `HUMAN_ORIGINATOR`, `INTERFACE_TRANSPORT`, and
`CONVERSATION_OWNER_RUNTIME`. A role states conversational function only.
Credentials, tokens, operating-system secrets, Authorization decisions, and
proof of legal or constitutional identity are outside both Envelope and CWM.
Until a future authenticated participant adapter is authorized, the only
valid human disposition is `ASSERTED_NOT_AUTHENTICATED`.

## Context Scope

`context_scope` is a closed locality record:

```json
{
  "workspace_identity_hash": "<must-match-envelope>",
  "session_identity_hash": "<must-match-envelope>",
  "current_interface_identity": "<must-match-envelope>",
  "scope_revision": 3,
  "scope_status": "BOUND"
}
```

It answers only **where and within which bounded conversation** mutable state
is valid. It must not contain filenames, requested implementation scope,
capability names, protected subsystems, output format, or natural-language
environment constraints. Those values are semantic qualifiers/references or
belong to an external constitutional owner.

## Ownership Matrix

| Information or operation | Envelope | Semantic CWM | Future Objective Commitment | Certified downstream owner |
|---|---|---|---|---|
| Conversation correlation identity | Owns local identity | Reads binding only | Validates snapshot binding | No ownership |
| Workspace/session locality | Owns immutable binding | Reads locality only | Validates exact binding | Existing owners use their own context contracts |
| Interface and participant assertions | Owns bounded metadata | May cite participant ordinal in provenance | Requires explicit human commitment evidence under its future contract | Authorization independently owns authorization identity/evidence |
| Availability, suspension, restoration, TTL | Owns | Cannot override | Rejects unavailable/expired state | No downstream effect |
| Conversation phase | Derives from validated inputs | Supplies semantic/control facts | Supplies boundary outcome | No ownership |
| Six G57-02 semantic classes | Prohibited | Owns provisional values and revision | Reads exact immutable projection | Objective owns committed meaning afterward |
| Clarification queue and conflicts | Binding/status only | Owns | Requires resolved state | No ownership |
| Candidate content and projection | Prohibited | Owns | Consumes exact projection | Objective owner creates immutable Objective if accepted |
| Candidate revision/digest binding | Owns derived binding | Produces source revision/digest | Validates exact match | No ownership |
| Capability selection | Prohibited | Prohibited | Prohibited | Platform Core Capability Selection |
| Replay | Prohibited | Prohibited | Boundary contract must define any later evidence handoff | Replay owner |
| Authorization | Prohibited | Prohibited | Prohibited | Authorization owner |
| Worker dispatch/execution/completion | Prohibited | Prohibited | Prohibited | Worker and Completion owners |

## Information Placement

| Information class | Inside Envelope | Inside Semantic CWM | Outside both |
|---|---:|---:|---:|
| Conversation/workspace/session/interface identity bindings | Yes | No | No |
| Participant role and asserted local binding | Yes | No | Authentication proof remains outside |
| Availability, phase, timestamps, TTL, restore data | Yes | No | No |
| Exact semantic revision and candidate digest binding | Yes | Source only | Objective identity remains outside |
| Operative action, subject, outcome, work type | No | Yes | Committed meaning later belongs to Objective |
| Preservation/output/acceptance/assumption qualifiers | No | Yes | Constitutional validation/disposition belongs to its owner |
| Scope/capability-hint/evidence semantic references | No | Yes | Referenced artifact contents remain externally owned |
| Provenance fragments, conflicts, dependencies, clarification queue | No | Yes | Full transport transcript remains outside |
| Raw terminal/transport frames and PTY control characters | No | No | Transport owner; only bounded semantic fragments may enter CWM provenance |
| Credentials, access tokens, OS identity proof | No | No | Authentication/security owner |
| Objective ID or immutable Objective | No | No | Objective owner |
| Capability route, G31 synthesis artifact, Development Governance decision | No | No | Respective certified owners |
| Replay, Authorization, Worker request/result, Completion evidence | No | No | Respective certified owners |
| Repository/Git contents | Workspace identity only | Opaque reference only | Repository/evidence owner |

## Availability Lifecycle

Availability is independent of semantic readiness. The canonical stored
availability values are:

- `ACTIVE`: unexpired, integrity-valid, and open for revisioned Envelope/CWM
  updates.
- `SUSPENDED`: preserved but closed to semantic mutation until exact restore.
- `CLOSED`: explicit terminal local state pending deterministic cleanup.

`ABSENT` is an API observation, not a stored value. `EXPIRED` is a transition
disposition observed under the store lock, not a durable state. This preserves
G55-03 cleanup semantics and avoids constitutional-looking tombstones.

| Current observation | Trigger | Next observation | Required effects | Fail-closed condition |
|---|---|---|---|---|
| `ABSENT` | Create with valid identities, participant binding, and time | `ACTIVE` | Revision 0, `COLLECTING`, atomic write | Existing path, invalid identity, invalid participant, or invalid TTL |
| `ACTIVE` | Valid semantic/envelope update | `ACTIVE` | Increment global revision once; recompute component revisions, phase, bindings, integrity | Stale expected revision or prohibited field |
| `ACTIVE` | Explicit suspend or transport suspension contract | `SUSPENDED` | Preserve current phase unchanged; record time; increment revision | Missing participant confirmation or stale revision |
| `SUSPENDED` | Exact restore | `ACTIVE` | Validate identity, integrity, revision, TTL, participant/interface binding; restore saved phase | Mismatch, expiration, copied state, or implicit cross-interface continuation |
| `ACTIVE` or `SUSPENDED` | Observed time at/after expiry | `ABSENT` | Remove local state atomically | Corrupt state is quarantined/rejected, not restored |
| `ACTIVE` or `SUSPENDED` | Explicit close | `CLOSED`, then `ABSENT` | Record close under lock, reject further semantic update, then cleanup | Stale revision or invalid participant binding |
| `CLOSED` | Any update/restore | `CLOSED` | No mutation | Always reject |

Expiration does not run as an autonomous semantic event. It is evaluated from
an explicit canonical `observed_at` during a locked load, recover, update, or
cleanup operation.

## Conversation Phase

Phase describes bounded conversational progress, not availability and not
Objective lifecycle. Canonical phases are:

- `COLLECTING`: semantic state is incomplete and no clarification item has
  precedence.
- `CLARIFYING`: Semantic CWM has a deterministic unresolved clarification item.
- `CANDIDATE_REVIEW`: a validated candidate exists at the bound semantic
  revision and awaits human review/correction.
- `COMMITMENT_PENDING`: a future commitment owner has accepted an exact review
  request but has not produced an acceptance/rejection result.
- `HANDED_OFF`: a future commitment owner accepted the candidate for transfer
  to the Objective owner. This is not proof that downstream execution ran.

The phase is recomputed, never freely patched. Precedence is:

```text
if availability != ACTIVE:
    preserve conversation_phase; no phase transition
else if future commitment result == ACCEPTED_HANDOFF:
    HANDED_OFF
else if future commitment request is valid and unresolved:
    COMMITMENT_PENDING
else if semantic clarification queue has a current item:
    CLARIFYING
else if candidate binding exactly matches validated semantic revision/digest:
    CANDIDATE_REVIEW
else:
    COLLECTING
```

An implementation predating Objective Commitment may support only
`COLLECTING`, `CLARIFYING`, and `CANDIDATE_REVIEW`. It must reject the two
reserved future phases rather than setting them speculatively.

## Active Objective Candidate Binding

The Envelope may record only:

```json
{
  "semantic_revision": 12,
  "candidate_projection_ruleset_version": "<closed-version>",
  "candidate_digest": "<sha256-of-canonical-projection>",
  "review_status": "AWAITING_HUMAN_REVIEW",
  "bound_at_global_revision": 17
}
```

Candidate text and structured semantic fields remain in Semantic CWM. The
binding is cleared whenever:

- any candidate-contributing semantic slot changes;
- a dependency becomes unresolved;
- a conflict or clarification becomes active;
- the candidate projection ruleset changes;
- integrity, workspace, session, or revision validation fails; or
- the human requests correction after review.

Forbidden keys include `objective_id`, `replay_identity`,
`authorization_id`, `worker_request_id`, `artifact_hash`, and any natural
language candidate payload. A digest match demonstrates local byte identity
only; it does not demonstrate constitutional acceptance.

## Atomic Revision Model

Envelope and semantics must not be persisted in separate files. Every accepted
mutation occurs under the existing conversation-store lock and creates one
new canonical document. The rules are:

1. caller supplies exact `expected_revision`;
2. runtime validates current identity, schema, boundary, integrity, and TTL;
3. runtime applies either Envelope, semantic, or combined changes in memory;
4. runtime recomputes semantic readiness, phase, candidate binding, component
   revisions, global revision, and integrity in a fixed order;
5. runtime writes one temporary file, fsyncs, atomically replaces, and returns
   the validated document.

`revision` increments once per transaction. `envelope_revision` increments
only when Envelope-owned canonical data changes. `semantic_revision`
increments only when Semantic CWM canonical data changes. Derived candidate
and phase changes participate in the same global transaction and cannot race
the semantic revision they describe.

## State and Interaction Diagrams

### Conversation lifecycle

```text
                         exact restore
                    +---------------------+
                    |                     |
ABSENT -- create --> ACTIVE -- suspend --> SUSPENDED
  ^                   |  ^                  |
  |                   |  | valid update     |
  |                   +--+                  |
  |                   |                     |
  |                   +-- explicit close ---+--> CLOSED
  |                                             |
  +--------- cleanup after close ---------------+
  |
  +--------- expiration cleanup from ACTIVE/SUSPENDED

Any identity, revision, integrity, TTL, participant, or interface mismatch:
FAIL_CLOSED with no semantic mutation and no pipeline entry.
```

### Envelope, CWM, and future commitment

```text
Human / interface assertion
          |
          v
Conversation Envelope
  identity | scope | participant | availability
          |
          | exact atomic binding
          v
Semantic CWM
  six typed classes | provenance | clarification | candidate content
          |
          | exact revision + projection digest
          v
Envelope candidate binding
          |
          | future explicit human commitment request
          v
Objective Commitment Gate (not implemented; separately owned)
          |
          | accepted immutable handoff only
          v
Objective -> Development Governance -> Capability -> Authorization
          -> Worker -> Completion -> Replay

Envelope and Semantic CWM have no call or mutation path into the final line.
```

### Explicit capability precedence

```text
Human request
     |
     v
Existing Platform Core admission precedence
     |
     +-- explicit authenticated capability request
     |       -> existing certified capability path
     |          (Envelope/CWM cannot delay or reinterpret it)
     |
     +-- generic or ambiguous development conversation
             -> Envelope + Semantic CWM only
             -> clarification/candidate review
             -> future commitment boundary, if separately authorized
```

This preserves the G54 admission rule: no implicit capability execution is
introduced, and active-objective continuation remains owned by Platform Core.

## Deterministic Interaction Contract

### Envelope and G55-03 CWM Runtime

1. The runtime creates or loads the single workspace/session state document.
2. The Envelope validates storage identity, participant/interface assertions,
   availability, TTL, and expected revision.
3. Semantic operations are rejected unless availability is `ACTIVE`.
4. A valid semantic update is applied within the same transaction.
5. Envelope bindings and derived phase are refreshed before integrity is
   calculated.
6. Suspension preserves the complete semantic state but blocks semantic
   mutation.
7. Restoration returns the exact atomic state or fails closed; it never
   reconstructs missing semantics from a transcript.

### Envelope and G57-02 Typed Semantic Slots

- Envelope supplies validated locality and participant ordinals for provenance
  association.
- Semantic slots never supply or overwrite Envelope identity.
- Semantic readiness and clarification facts are inputs to phase derivation.
- Candidate projection supplies exact semantic revision, ruleset, and digest
  for the Envelope binding.
- A context-changing Envelope transaction clears stale candidate bindings and
  causes the semantic owner to revalidate context-sensitive references.
- Environment restrictions stated by a human remain typed qualifiers or
  references; they do not migrate into `context_scope`.

### Envelope and Future Objective Commitment

A future gate may read one exact immutable transaction snapshot containing:

- conversation, workspace, session, interface, and participant bindings;
- global, Envelope, and semantic revisions;
- active availability and unexpired time;
- `CANDIDATE_REVIEW` phase;
- exact candidate projection ruleset and digest;
- resolved clarification/conflict disposition; and
- explicit human commitment evidence defined by the future gate contract.

The gate must reject any mismatch or subsequent revision. It may not edit the
Envelope or Semantic CWM to make a candidate eligible. If rejected, the local
phase returns deterministically to `CANDIDATE_REVIEW`, `CLARIFYING`, or
`COLLECTING` based on current validated state. If accepted, `HANDED_OFF` records
only local boundary disposition; the Envelope still stores no Objective ID.

## Certified Execution Pipeline Separation

| Certified owner | Envelope/CWM behavior before commitment | Permitted future boundary input | Prohibited behavior |
|---|---|---|---|
| Platform Core admission | Explicit capability precedence remains first and unchanged | Generic branch may later receive an accepted Objective through a separate adapter | Envelope selecting or routing a capability |
| Objective | No Objective exists | Exact candidate projection after separate acceptance | Storing/claiming Objective identity |
| Development Governance | No call or decision | Receives only an Objective through existing contracts | Envelope interpreting governance policy |
| Capability | No selection or execution binding | Existing Objective path only | Capability hint treated as route |
| Replay | No Replay visibility or identity | Future downstream owners retain existing Replay duties | Envelope persistence becoming Replay evidence |
| Authorization | No request or eligibility | Existing authorization request only | Participant assertion treated as authorization |
| Worker | No request, dispatch, execution, or completion | Existing authorized Worker path only | Envelope invoking or completing Worker work |

Logical integration in one working-state document does not constitute runtime
integration with the certified pipeline. No Envelope method may import or call
Objective, capability selection, Replay, Authorization, Worker, or Completion
entrypoints.

## Suspension, Restoration, Expiration, and Closure

### Suspension

Suspension is a local availability transition. It preserves the exact semantic
revision, candidate binding, clarification queue, and conversation phase. It does
not imply approval, refusal, completion, or Objective suspension. All semantic
updates and candidate review actions are rejected while suspended.

### Restoration

Restoration requires all of the following:

- exact state path derived from canonical workspace/session identities;
- valid closed schema and fixed boundary flags;
- valid canonical integrity checksum;
- exact caller-supplied expected global revision;
- unexpired canonical observed time;
- unchanged conversation identity;
- valid participant confirmation; and
- same interface or an explicitly validated interface rebind.

Failure of any item leaves the state unchanged and returns a fail-closed
disposition. Restoration cannot use text similarity, model inference, or a
partial transcript to repair identity or semantics.

### Expiration and closure

Expiration is time-driven cleanup under an explicit operation. Closure is a
participant-requested terminal transition. Both end mutable conversation state
without producing a constitutional record. If retention evidence is later
required, that must be designed under a separate constitutional evidence owner;
this Envelope must not silently become that owner.

## G55-03 Compatibility Assessment

| G55-03 property | V2 disposition | Compatibility |
|---|---|---|
| `.platform-core-working/conversation` root | Preserve | Compatible |
| Canonical workspace/session path isolation | Preserve exactly | Compatible |
| Closed schema validation | Preserve; introduce explicit V2 schema | Versioned extension required |
| Single `state.json` document | Preserve; nest Envelope and Semantic CWM | Compatible and required for atomicity |
| One store lock and atomic replacement | Preserve | Compatible |
| Global optimistic revision | Preserve and supplement with component revisions | Compatible extension |
| SHA-256 canonical JSON integrity | Preserve over full V2 document | Compatible |
| TTL, recovery, cleanup | Preserve; availability clarifies suspension/closure | Compatible extension |
| Size, collection, text, permission bounds | Preserve principle; V2 exact budgets need measurement | Exact limits not yet verified |
| Non-authority boundary flags | Preserve exactly at document and Envelope boundary | Compatible |
| V1 `EXPLORING`/`CANDIDATE_READY` lifecycle | Reclassify as semantic readiness during migration | Deterministic mapping required |
| Reserved `COMMITTING`/`COMMITTED` values | Do not reinterpret; future gate owns commitment | Boundary preserved |
| Empty `commitment_metadata` | Preserve empty in V1; no Objective metadata in Envelope | Compatible |

## Migration Assessment

Migration is optional until separately authorized. If implemented, it must be
read-validate-transform-write-validate and fail closed.

| V1 source | V2 destination | Rule |
|---|---|---|
| workspace/session identities and hashes | Envelope immutable bindings | Copy only after existing V1 identity validation |
| created/updated/expires timestamps | Envelope timestamps | Preserve exact canonical bytes |
| boundary flags | document and Envelope boundaries | Must equal fixed false values; otherwise reject |
| revision | global revision migration anchor | Record exact source revision; no reset that could admit stale writers |
| `EXPLORING` | Envelope `ACTIVE`; semantic readiness incomplete | Lifecycle meaning is split, not renamed blindly |
| `CANDIDATE_READY` | Envelope `ACTIVE`; legacy candidate review required | Does not automatically produce `CANDIDATE_REVIEW` eligibility |
| topic, entities, inferred intent, facts, assumptions, ambiguities, references | Semantic CWM legacy import area | Must be normalized/reconfirmed under G57-02 before canonical use |
| candidate snapshot/digest | Semantic legacy candidate plus Envelope legacy binding | `LEGACY_REVIEW_REQUIRED`; never commitment eligible without reprojection |
| confidence/discarded interpretations | Semantic control/provenance | Preserve only if valid and mappable |
| empty commitment metadata | No Envelope field | Do not invent commitment history |

A safe sequence is:

1. acquire the existing store lock;
2. validate V1 identity, schema, integrity, TTL, and boundary;
3. create a deterministic V2 candidate in memory with a migration provenance
   record and `PARTICIPANT_BINDING_REQUIRED` disposition;
4. validate all V2 closed fields and size budgets;
5. atomically write a new versioned state while preserving the V1 source until
   V2 post-write validation succeeds;
6. require explicit participant binding and semantic reconfirmation before
   candidate review; and
7. never infer missing participant, interface, or semantic values.

If V1 state is expired, corrupt, copied, contains a reserved commitment
lifecycle, or cannot fit the V2 bounds, migration is rejected. No partial V2
state is retained.

## Risk Assessment

| Risk | Failure mode | Required control |
|---|---|---|
| Duplicate metadata store | Envelope and CWM revisions diverge | One atomic document, one lock, one global revision |
| Identity overclaim | Local digest mistaken for constitutional identity | Explicit local namespace and fixed non-authority fields |
| Participant overclaim | Assertion mistaken for authentication or authorization | `ASSERTED_NOT_AUTHENTICATED`; credentials outside |
| Phase drift | Stored phase contradicts semantic state | Derive in fixed precedence during every transaction |
| Candidate semantic leakage | Envelope becomes a second semantic owner | Binding only; reject payload fields |
| Cross-interface hijack | Similar session text resumes wrong state | Exact identity/revision/integrity plus explicit rebind |
| Expiration race | Update admitted after TTL | Validate observed time under lock before mutation |
| Restoration reconstruction | Missing semantics synthesized from transcript | Exact-state restoration only; no inference |
| Replay contamination | Mutable metadata treated as immutable evidence | Working root, `replay_visible: false`, forbidden identity keys |
| Capability bypass | Hint or phase routes execution | No routing methods/imports; explicit capability precedence unchanged |
| Migration authority drift | V1 candidate treated as committed meaning | Legacy-review disposition and human reconfirmation |
| Unbounded participant/context growth | State budget bypass | Closed roles, item/text counts, full-document byte cap |

## Architecture Acceptance Invariants

1. One conversation has exactly one immutable Envelope identity within one
   workspace/session state path.
2. The Envelope and Semantic CWM share one atomic document and global revision.
3. Envelope fields contain no semantic slot value or free-form request payload.
4. Semantic CWM cannot alter Envelope identity or availability.
5. A participant assertion never authenticates or authorizes a participant.
6. Phase is derived; availability and semantic readiness are independent axes.
7. Suspended, expired, closed, corrupt, stale, or mismatched state cannot be
   semantically updated or offered for commitment.
8. Candidate binding must exactly match the current validated semantic revision
   and canonical projection digest.
9. The Envelope stores no Objective, Replay, authorization, Worker, capability,
   or constitutional artifact identity.
10. Explicit certified capability admission remains upstream and unchanged.
11. Future commitment requires a new separately authorized owner and exact
    snapshot validation.
12. Cleanup produces no hidden constitutional or execution side effect.

## Future Implementation Recommendations

These recommendations do not authorize implementation:

1. Specify a closed V2 JSON schema with byte/item budgets before changing the
   G55-03 runtime.
2. Implement Envelope validation as a pure module with no imports from
   Objective, capability selection, Replay, Authorization, Worker, or
   Completion packages.
3. Refactor G55-03 storage only enough to persist one V2 document under the
   existing lock and atomic-write discipline.
4. Implement the six G57-02 semantic classes separately from Envelope records.
5. Derive phase and candidate binding in a single pure reducer after semantic
   validation.
6. Add transition-table tests, copied-state tests, stale revision tests,
   cross-interface restoration tests, expiration-boundary tests, payload
   smuggling tests, and reserved-identity tests.
7. Implement V1 migration as an explicit utility; do not auto-migrate on load
   until migration evidence is certified.
8. Design Objective Commitment in a later generation with its own authority,
   human-evidence, Replay, and rejection contracts.

## Validation Evidence

Focused G55-03 CWM and adjacent Conversation Boundary regression:

```text
python -m pytest -q \
  tests/test_g55_03_conversation_working_memory_runtime.py \
  tests/test_g49_02_platform_core_conversation_boundary.py
29 passed in 1.42s
```

Governance conformance tests:

```text
python -m pytest -q tests/test_governance_conformance.py
5 passed in 0.03s
```

Repository conformance engine:

```text
python -m runtime.governance.governance_conformance_engine
status: PARTIALLY_CONFORMANT
checks_passed: 18
checks_failed: 2
critical_violations: 0
deterministic: true
fail_closed: true
read_only: true
report_hash: 0790499ee53f9a82e15225e15eff1c2637b7e60523fa38be0c921281abe4cbea
```

The two failures are the pre-existing visible hook mismatches:

- root pre-commit hooks are expected but both repository and installed hooks
  are missing; and
- the system pre-commit hook lacks `promotion_gate_v02` and
  `check_layer_freeze` tokens.

They are non-critical to this architecture-only artifact, but the result
remains `PARTIAL` and is not reframed as full repository conformance.

G48 structure and whitespace:

```text
awk 'BEGIN { fence=0; count=0 } /^```/ { fence=!fence; next } \
  !fence && /^# / { count++; print count ":" $0 } \
  END { if (count != 6) exit 1 }' \
  docs/governance/G57_03_CONVERSATION_ENVELOPE_ARCHITECTURE_REPORT_V1.md
1:# 1. Implementation Summary
2:# 2. Code Evidence
3:# 3. Constitutional Self-Assessment
4:# 4. Validation Matrix
5:# 5. Repository Mutation Summary
6:# 6. Certification Verdict

git diff --check
<no output; exit 0>
```

## Responsibility Boundaries

- Conversation Envelope owns local identity, bounded participant/interface
  assertions, locality, availability, phase derivation, and exact bindings.
- Semantic CWM owns provisional typed meaning, provenance, clarification,
  semantic revision, and candidate content.
- G55-03 persistence infrastructure owns file location, locking, atomicity,
  integrity, revision checks, bounded storage, recovery, and cleanup.
- A future Objective Commitment component must own the mutable-to-immutable
  admission decision and explicit human commitment evidence.
- Objective, Development Governance, Capability, Replay, Authorization,
  Worker, and Completion retain all existing downstream responsibilities.
- Human Authority remains external and cannot be represented by an Envelope
  participant assertion.

# 3. Constitutional Self-Assessment

## Verified

- The architecture assigns conversation metadata and semantic meaning to
  disjoint owners and provides an explicit inside/outside placement matrix.
- Conversation, workspace, session, interface, and participant identities have
  deterministic construction or validation boundaries and explicit
  non-authority semantics.
- Availability lifecycle, semantic readiness, conversation phase, and future
  Objective commitment are modeled as distinct concerns.
- Suspension, restoration, expiration, closure, and cleanup have deterministic
  transition and fail-closed criteria.
- Active Objective-candidate metadata is limited to exact revision/ruleset/
  digest binding and cannot contain candidate content or Objective identity.
- A single atomic state document, one global revision, component revisions,
  and derived-field recomputation prevent Envelope/CWM cross-file races.
- The interaction contract preserves G55-03 storage controls, the six G57-02
  semantic classes, and a one-way future commitment boundary.
- Explicit certified capability admission remains upstream and unchanged.
- The architecture assigns no new semantic responsibility to transport or any
  downstream execution owner.
- The V1-to-V2 migration model preserves source validation, non-authority,
  exact revisions, human reconfirmation, and fail-closed handling.
- No runtime source, test, constitutional artifact, PCBV31 record, or existing
  governance report was changed.

## Not Verified

- The Envelope schema, validators, reducer, lifecycle operations, persistence,
  and V1 migration utility are architecture only and are not implemented.
- Exact V2 document, participant, collection, and text size budgets have not
  been measured against representative persisted states.
- Participant identity is deliberately an unauthenticated local assertion;
  no authenticated participant source or human-commitment evidence contract
  has been designed or verified.
- Cross-interface restoration has not been implemented or exercised. Its
  adapter ownership and approved interface vocabulary remain future work.
- Semantic slot normalization, phase derivation, candidate reprojection, and
  atomic combined transactions have not been executed in a V2 runtime.
- Future Objective Commitment, Objective creation, and any evidence handoff to
  Replay remain unimplemented and outside this generation.
- No live conversation was migrated from V1 to V2 because repository mutation
  beyond this report and runtime implementation were forbidden.
- Repository-wide conformance remains subject to the existing declared hook
  drift; this architecture does not claim to repair or conceal it.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| Canonical Envelope model | Canonical model and field contract | Reviewed every field for type, owner, mutability, and non-meaning | PASS |
| Conversation identity | Local digest construction and copied-state rule | Deterministic input and prohibited-input review | PASS |
| Workspace/session identity | G55-03 exact runtime excerpt and identity model | Compatibility review against current hash/path contract | PASS |
| Participant identity | Closed conceptual record and asserted-not-authenticated disposition | Authority-confusion and credential-placement review | PASS |
| Context scope | Closed locality record | Compared with G57-02 semantic qualifier/reference boundary | PASS |
| Inside/Semantic CWM/outside classification | Information placement matrix | Exhaustive ownership review for requested information classes | PASS |
| Availability lifecycle | Transition table and lifecycle diagram | State/trigger/effect/failure review | PASS |
| Conversation phase | Five phases and derivation precedence | Checked independence from availability and Objective lifecycle | PASS |
| Suspension/restoration | Exact validation gates | Identity, revision, integrity, TTL, participant, and interface review | PASS |
| Expiration/closure | Locked observed-time and cleanup rules | Verified no durable constitutional tombstone or side effect is specified | PASS |
| Active Objective-candidate binding | Closed binding model and clearing rules | Payload-smuggling and stale-binding review | PASS |
| Atomic Envelope/CWM interaction | One-document revision algorithm | Race and stale-writer analysis against G55-03 substrate | PASS |
| G57-02 slot compatibility | Six-class interaction contract | Confirmed no semantic class moved into Envelope | PASS |
| Future Objective Commitment compatibility | Exact snapshot inputs and one-way handoff | Owner and mutation-boundary review | PASS |
| Certified pipeline separation | Separation matrix and admission diagram | Verified no proposed Envelope call, identity, or authority enters downstream owners | PASS |
| G55-03 persistence compatibility | Property-by-property compatibility table | Static comparison with authenticated V1 source/report | PASS |
| V1 migration | Migration mapping and fail-closed sequence | Static transform and authority-drift review | PASS |
| Runtime Envelope behavior | Proposed V2 implementation | No implementation authorized | NOT_APPLICABLE |
| Live V1-to-V2 migration | Proposed migration utility | No implementation or state mutation authorized | NOT_APPLICABLE |
| Objective Commitment execution | Future separate owner | Outside architecture scope and not implemented | NOT_APPLICABLE |
| Existing CWM runtime regression | G55-03 focused test suite | Executed after report creation | PASS |
| Governance conformance tests | Governance conformance test suite | Executed after report creation | PASS |
| Repository conformance engine | Existing conformance engine | Executed; known non-critical hook drift remains visible | PARTIAL |
| G48 top-level structure | This report | Verified exactly six required top-level headings in required order | PASS |
| Repository whitespace integrity | Current repository diff | `git diff --check` | PASS |
| No forbidden mutation | Git status and diff inventory | Confirmed only this report was added | PASS |

# 5. Repository Mutation Summary

Modified files:

- `docs/governance/G57_03_CONVERSATION_ENVELOPE_ARCHITECTURE_REPORT_V1.md`:
  added the canonical Envelope model, ownership matrices, lifecycle,
  transitions, interaction diagrams, compatibility assessment, migration
  assessment, risks, validation evidence, and verdict.

Unchanged subsystems:

- AiCLI and Human Interface Runtime.
- Platform Core admission, Objective inference/creation, and Development
  Governance.
- Capability selection, execution binding, and G31/G35 behavior.
- Replay and Authorization protocols.
- Worker lifecycle, dispatch, execution, completion adapter, and presentation.
- Conversation Boundary and the implemented G55-03 CWM runtime/tests.
- PCBV31 and all constitutional specifications and manifests.

API compatibility:

- No runtime API or stored schema changed. The report explicitly requires a
  future versioned V2 schema rather than silently extending V1.
- G55-03 V1 remains the only implemented CWM public API and correctly rejects
  unknown schema fields.

Boundary preservation:

- The Envelope remains mutable, local, nonconstitutional, non-Replay,
  nonauthorizing, nonexecuting, and incapable of Objective creation or
  capability routing.
- Semantic CWM and every certified downstream owner retain exclusive
  responsibility for their existing meanings and actions.

Unrelated pre-existing changes:

- None observed before this report was created.

# 6. Certification Verdict

CONVERSATION_ENVELOPE_ARCHITECTURE_CHARACTERIZED
