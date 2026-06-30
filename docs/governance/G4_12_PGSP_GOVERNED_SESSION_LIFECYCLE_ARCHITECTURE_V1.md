# G4-12 PGSP Governed Session Lifecycle Architecture V1

Status: PGSP governed session lifecycle architecture defined.

Final verdict: PGSP_SESSION_LIFECYCLE_READY

## 1. Purpose

This artifact defines the canonical lifecycle of a Platform Governed Session Protocol session.

The lifecycle supports long-running, multi-step governed interactions while preserving the certified Platform Core ownership model:

```text
Human
-> Interface Adapter
-> PGSP
-> UBTR
-> CSA
-> OCS
-> Governance
-> UHCL
-> Interface Adapter
-> Human Response
-> Replay
-> Advisory or governed execution intent
```

This is an architecture and contract milestone only. It does not introduce a new runtime layer, redesign G4-02, redesign G4-04, redesign G4-05, invoke providers, execute workers, create approvals, create authorization, mutate repositories, deploy software, or change replay semantics.

## 2. Lifecycle Principles

PGSP lifecycle management must preserve these principles:

- session identity is stable and replay-visible;
- every lifecycle transition is governed;
- every transition creates deterministic replay evidence;
- continuation never bypasses UBTR, CSA, OCS, Governance, UHCL, or Replay;
- suspension preserves state without granting authority;
- resume reconstructs from replay before accepting new input;
- branching creates explicit lineage rather than hidden divergence;
- merge requires governance review and replay-visible conflict handling;
- completion records final state without implying execution authority;
- adapters manage interaction continuity, not Platform Core semantics.

The lifecycle governs session continuity. It does not transfer ownership of Platform Services into PGSP or adapters.

## 3. Lifecycle State Model

Canonical PGSP lifecycle states:

| State | Meaning | Execution Authority |
| --- | --- | --- |
| `CREATED` | Session identity and specialization are established. | None |
| `ACTIVE` | Session can receive governed human input and produce PGSP turns. | None by default |
| `AWAITING_HUMAN_RESPONSE` | UHCL communication has been rendered and a human response is required. | None |
| `AWAITING_GOVERNANCE` | A checkpoint, policy decision, approval evidence, authorization evidence, or readiness evidence is required. | None |
| `SUSPENDED` | Session is paused with replay-visible continuation state. | None |
| `RESUMED` | Session has been reconstructed and reactivated from replay. | None by default |
| `BRANCHED` | A child session lineage has been created from a parent session point. | None by default |
| `MERGE_PENDING` | One or more branches are proposed for lineage merge and require governance review. | None |
| `MERGED` | Branch evidence has been reconciled into a governed continuation lineage. | None by default |
| `COMPLETED` | Session is closed with final replay and governance evidence. | None unless separately authorized |
| `FAILED_CLOSED` | Session cannot continue because required evidence, mapping, or governance conditions failed. | None |
| `SUPERSEDED` | Session is replaced by a replay-linked successor session. | None |

Generation 4 currently exercises a subset of this lifecycle through advisory-only `CREATED`, `ACTIVE`, `AWAITING_HUMAN_RESPONSE`, `AWAITING_GOVERNANCE`, and replay-visible completion-like evidence. Future long-running sessions should add explicit state artifacts without changing Platform Service ownership.

## 4. State Transitions

Canonical transitions:

| Transition | From | To | Required Evidence |
| --- | --- | --- | --- |
| Create session | none | `CREATED` | session id, specialization, adapter capture reference, created-at timestamp |
| Activate session | `CREATED` or `RESUMED` | `ACTIVE` | replay-visible activation checkpoint |
| Request turn | `ACTIVE` | `AWAITING_HUMAN_RESPONSE` | UBTR, CSA, OCS, Governance, UHCL, adapter render evidence |
| Capture response | `AWAITING_HUMAN_RESPONSE` | `ACTIVE` or `AWAITING_GOVERNANCE` | canonical response class and response evidence |
| Require governance | any governed state | `AWAITING_GOVERNANCE` | checkpoint status and missing prerequisites |
| Suspend session | `ACTIVE`, `AWAITING_HUMAN_RESPONSE`, or `AWAITING_GOVERNANCE` | `SUSPENDED` | suspension reason, state hash, replay root |
| Resume session | `SUSPENDED` | `RESUMED` | replay reconstruction hash, resume reason, adapter identity |
| Branch session | `ACTIVE`, `SUSPENDED`, or `AWAITING_GOVERNANCE` | `BRANCHED` | parent session id, branch id, branch reason, parent replay hash |
| Propose merge | one or more `BRANCHED` sessions | `MERGE_PENDING` | branch replay hashes, conflict summary, governance checkpoint |
| Complete merge | `MERGE_PENDING` | `MERGED` | merge decision, retained evidence, discarded alternatives if any |
| Complete session | `ACTIVE`, `MERGED`, or `AWAITING_GOVERNANCE` | `COMPLETED` | final summary, replay hash, governance disposition |
| Fail closed | any state | `FAILED_CLOSED` | failure reason, failed checkpoint, replay evidence |
| Supersede session | any non-terminal state | `SUPERSEDED` | successor session id and replay linkage |

Transitions must be append-only in replay. A transition may update the current session view, but it must not erase prior transition evidence.

## 5. Session Creation

Session creation establishes:

- stable session id;
- PGSP version or contract version;
- session specialization, such as LGDS;
- adapter identity and adapter version where available;
- initiating human request reference;
- replay root;
- initial governance boundary declarations;
- initial non-authority flags.

Adapters may supply session ids and metadata, but PGSP owns the canonical session envelope. Adapters must not create semantic state outside PGSP.

## 6. Session Continuation

Continuation is a new governed turn in an existing session lineage.

Each continuation must:

- reconstruct or reference the prior replay state;
- capture new human input through an adapter;
- route the input through PGSP;
- invoke UBTR for semantic translation;
- preserve CSA structured intent evidence;
- allow OCS to produce proposal or advisory intent evidence;
- run governance checkpoints appropriate to the transition;
- render UHCL communication through the adapter;
- capture human response;
- append replay evidence.

Continuation must not reuse stale semantic conclusions without replay-visible justification.

## 7. Session Suspension

Suspension pauses a session without completing it.

Valid suspension reasons include:

- waiting for human availability;
- waiting for governance review;
- waiting for external evidence;
- waiting for future adapter reconnection;
- avoiding unsafe continuation after ambiguity;
- preserving state before a branch or merge review.

Suspension must record:

- suspension state;
- reason;
- last completed transition;
- replay hash;
- pending obligations;
- allowed resume conditions.

Suspension never grants execution authority.

## 8. Session Resume

Resume reactivates a suspended session.

Resume requires:

- replay reconstruction;
- verification of session identity;
- verification of specialization identity;
- verification of last known governance state;
- adapter identity capture;
- resume reason;
- new transition evidence.

If replay reconstruction fails, if the adapter cannot establish continuity, or if governance state is ambiguous, resume must fail closed.

Resume may occur from a different interface adapter only if the adapter renders PGSP/UHCL output and preserves the same canonical session identity and replay chain.

## 9. Session Branching

Branching creates a child lineage from a parent session state.

Branching is appropriate when:

- the human wants to explore an alternative plan;
- governance requires separating a risky path from a safe advisory path;
- multiple domain interpretations must be evaluated independently;
- a replay review needs an isolated evidence path;
- a suspended session needs a bounded investigation before continuation.

Branching must record:

- parent session id;
- parent replay hash;
- branch id;
- branch reason;
- branch initiator;
- branch specialization if different;
- governance checkpoint for branch admissibility.

Branches must not silently mutate parent session state.

## 10. Session Merge

Merge reconciles one or more branches into a continuing governed lineage.

Merge requires:

- branch replay reconstruction;
- conflict and compatibility analysis;
- governance checkpoint;
- clear selection of retained evidence;
- explicit rejection or archival of non-retained alternatives;
- final merged replay hash.

Merge must fail closed when branch evidence conflicts in a way that cannot be deterministically reconciled.

Merge does not create approval or authorization by itself. If a merged result requires execution, that execution must pass separate governed approval, authorization, worker readiness, and mutation certification gates.

## 11. Session Completion

Completion closes a session lineage.

Completion records:

- final state;
- final summary;
- final replay hash;
- governance disposition;
- outstanding gaps or blocked prerequisites;
- whether execution remained advisory-only;
- whether any future successor session is recommended.

Completion is not equivalent to successful execution. A session may complete as:

- advisory complete;
- blocked pending governance;
- rejected by human response;
- superseded by another session;
- failed closed;
- execution-ready only after future certified gates.

## 12. Replay Reconstruction Across Lifecycle

Full lifecycle replay must reconstruct:

- session identity;
- all state transitions;
- adapter capture and render evidence;
- UBTR translation evidence for each governed turn;
- CSA structured intent evidence for each governed turn;
- OCS proposal and advisory evidence for each governed turn;
- governance checkpoint evidence for each transition;
- UHCL communication evidence;
- human response evidence;
- branch and merge lineage;
- suspension and resume evidence;
- final session disposition.

Replay reconstruction must support two views:

| View | Purpose |
| --- | --- |
| Chronological transition log | Shows every lifecycle transition in order. |
| Current session projection | Shows the latest valid session state derived from replay. |

The current projection is derived from replay. It must not become an independent source of truth.

## 13. Governance Checkpoints During Transitions

Governance checkpoints must run or be referenced at every lifecycle transition that changes session authority, continuity, branch lineage, merge status, or completion state.

Checkpoint categories:

- creation admissibility;
- continuation admissibility;
- human response mapping;
- suspension admissibility;
- resume admissibility;
- branch admissibility;
- merge admissibility;
- completion disposition;
- fail-closed trigger validation.

Governance must preserve:

- approval boundary;
- authorization boundary;
- provider boundary;
- worker boundary;
- mutation boundary;
- deployment boundary;
- replay boundary;
- human authority visibility.

## 14. Adapter Responsibilities During Lifecycle Management

Adapters own:

- local session selection;
- raw input capture;
- display of current session state;
- rendering UHCL communication;
- response capture;
- adapter-local reconnect behavior;
- adapter-local branch or resume selection UI;
- surfacing replay references.

Adapters do not own:

- canonical lifecycle state;
- semantic translation;
- canonical structured intent;
- OCS proposals;
- governance checkpoints;
- reusable explanations;
- reusable confirmations;
- replay reconstruction;
- branch merge semantics;
- execution authorization;
- provider execution;
- worker execution;
- repository mutation.

Adapters may offer lifecycle controls, but PGSP and Governance determine whether the requested lifecycle transition is admissible.

## 15. Ownership Matrix

| Lifecycle Concern | PGSP | Adapter | UBTR | CSA | OCS | Governance | UHCL | Replay |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Session identity | Owns | Supplies or displays | Excludes | Excludes | References | Checks | Excludes | Records |
| State transition envelope | Owns | Requests or renders | Excludes | Excludes | References | Checks | Excludes | Records |
| Natural-language capture | Receives | Owns | Consumes | Excludes | Excludes | Excludes | Excludes | Records |
| Semantic translation | Uses | Excludes | Owns | Consumes | Consumes | References | Excludes | Records |
| Structured intent | Uses | Excludes | Produces input | Owns | Consumes | References | Excludes | Records |
| Proposal and advisory intent | Uses | Excludes | Excludes | Excludes | Owns | Checks | Communicates through UHCL | Records |
| Governance transition checks | Requires | Excludes | Excludes | Excludes | Supplies proposal evidence | Owns | Communicates outcome | Records |
| Human communication | Uses | Renders | Supplies communication semantics where applicable | Excludes | Supplies proposal context | Supplies checkpoint context | Owns | Records |
| Suspension and resume | Owns envelope | Requests and displays | Re-runs or references | Reconstructs references | Re-evaluates context | Checks | Explains | Reconstructs |
| Branch and merge | Owns envelope | Requests and displays | Re-runs or references | Reconstructs references | Evaluates alternatives | Checks | Explains | Reconstructs |
| Completion | Owns envelope | Displays | Excludes | Excludes | Supplies final intent status | Supplies disposition | Explains | Records |

## 16. Compatibility Strategy

G4-12 does not require immediate runtime changes.

Compatibility requirements:

- G4-02, G4-04, and G4-05 remain valid Generation 4 runtime lineage.
- Existing replay artifacts remain valid.
- Existing PGSP public API documentation remains valid.
- Current single-turn advisory sessions are valid lifecycle instances.
- Future lifecycle fields must be additive unless a later governance milestone certifies migration.
- Lifecycle state naming should be introduced as replay-visible metadata before runtime behavior depends on it.
- Future adapters must implement lifecycle controls through PGSP, not adapter-local protocol forks.

The lifecycle model is a canonical architecture target for long-running sessions, not a retroactive demand to rewrite certified G4 runtimes.

## 17. Certification Criteria

A future PGSP lifecycle implementation is certifiable only if it:

- preserves Platform Core ownership boundaries;
- records every lifecycle transition in replay;
- reconstructs current state from replay;
- fails closed on missing or inconsistent lifecycle evidence;
- runs or references governance checkpoints during lifecycle transitions;
- preserves human authority and confirmation visibility;
- prevents adapter-local semantic interpretation;
- prevents hidden branch divergence;
- prevents merge without governance review;
- preserves explicit non-authority flags;
- avoids provider execution unless separately governed;
- avoids worker execution unless separately governed;
- avoids repository mutation unless separately authorized and certified.

## 18. Recommended Next Implementation Batch

Recommended next batch:

```text
G4_13_PGSP_SESSION_LIFECYCLE_REPLAY_SCHEMA_AUDIT_V1
```

Recommended scope:

- audit existing G4-02, G4-04, and G4-05 replay artifacts against the lifecycle state model;
- determine the minimum additive replay metadata needed for multi-turn lifecycle support;
- avoid runtime implementation until the replay schema impact is certified.

## 19. Final Determination

The canonical PGSP governed session lifecycle can be defined without changing Platform Core responsibilities or adding new runtime layers.

The existing Generation 4 runtime remains valid as the first advisory, single-turn PGSP/LGDS lifecycle instance. Long-running behavior should be introduced through additive lifecycle metadata, replay reconstruction, and governance checkpoints.

Final verdict:

```text
PGSP_SESSION_LIFECYCLE_READY
```
