# G4-13 PGSP Multi-Session And Context Management Architecture V1

Status: PGSP multi-session and context management architecture defined.

Final verdict: PGSP_MULTI_SESSION_READY

## 1. Purpose

This artifact defines the canonical architecture for concurrent and long-lived Platform Governed Session Protocol sessions.

The objective is to ensure that multiple governed sessions remain isolated, replayable, resumable, and governable without changing Platform Core responsibilities.

This is an architecture and contract milestone only. It does not introduce a new runtime layer, redesign G4-02, redesign G4-04, redesign G4-05, invoke providers, execute workers, create approvals, create authorization, mutate repositories, deploy software, or change replay semantics.

## 2. Canonical Multi-Session Architecture

PGSP multi-session architecture introduces a canonical session management responsibility around PGSP session identity and lifecycle coordination.

Canonical model:

```text
Human
-> Interface Adapter
-> PGSP Session Manager
-> PGSP Session
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

The PGSP Session Manager is a Platform Core coordination concept. It maintains session registry, session selection, lifecycle projection, and cross-session references. It does not own semantic interpretation, reusable communication, governance decisions, replay mutation, provider execution, worker execution, repository mutation, approval creation, authorization creation, or deployment.

## 3. Session Manager Responsibilities

The PGSP Session Manager owns:

- session registry metadata;
- active session pointer per adapter or operator context;
- inactive session listing;
- session lifecycle projection derived from replay;
- session switching coordination;
- session persistence references;
- session archival references;
- restoration eligibility checks;
- cross-session reference declarations;
- isolation boundary declarations.

The PGSP Session Manager does not own:

- UBTR translation;
- CSA structured intent;
- OCS proposal semantics;
- Governance checkpoint decisions;
- UHCL communication generation;
- Replay evidence mutation;
- provider execution;
- worker execution;
- approvals;
- authorization;
- repository mutation;
- deployment;
- adapter rendering.

The manager coordinates sessions. It does not become a translator, orchestrator, governance engine, replay engine, adapter, provider, worker, or product runtime.

## 4. Multiple Simultaneous Sessions

PGSP must support multiple simultaneous governed sessions.

Each session has:

- globally stable session id;
- specialization id;
- lifecycle state;
- replay root;
- governance disposition;
- adapter participation history;
- context boundary;
- optional cross-session references;
- archival state.

Simultaneous sessions must not share mutable semantic context. Shared information must be copied or referenced through replay-visible cross-session references.

## 5. Active And Inactive Sessions

Canonical activity states:

| State | Meaning |
| --- | --- |
| `ACTIVE_SELECTED` | The session currently selected by an adapter or operator context. |
| `ACTIVE_BACKGROUND` | The session is open and may receive events, but is not currently selected. |
| `INACTIVE_SUSPENDED` | The session is paused and may be resumed after replay reconstruction. |
| `INACTIVE_COMPLETED` | The session is closed and available for replay or archival. |
| `INACTIVE_FAILED_CLOSED` | The session cannot continue without repair or governance review. |
| `ARCHIVED` | The session is stored for audit, replay, and restoration eligibility checks. |

Only one session should be `ACTIVE_SELECTED` per adapter interaction surface unless a future adapter explicitly supports split-view interaction. Multiple sessions may exist in `ACTIVE_BACKGROUND` or inactive states.

Activity state is an adapter and session-manager view over replay-backed lifecycle state. It must not override lifecycle state or governance status.

## 6. Session Switching

Session switching changes the selected session for an adapter or operator context.

Switching requires:

- current session id;
- target session id;
- adapter id or operator context id;
- replay-visible switch event;
- current lifecycle projection for target session;
- governance visibility for any blocked or failed state.

Switching must not:

- merge context;
- copy semantic state silently;
- bypass resume requirements;
- convert inactive state into execution authority;
- hide pending governance obligations.

If the target session is suspended, failed closed, archived, or awaiting governance, the adapter must render that state and PGSP must determine whether resume, review, or restoration is admissible.

## 7. Session Persistence

Session persistence stores the durable identity and replay references required to reconstruct a session.

Persistence must include:

- session id;
- specialization id;
- created-at timestamp;
- last transition id;
- last replay hash;
- replay root;
- lifecycle state projection;
- governance disposition;
- archival state;
- adapter participation summary;
- cross-session reference summary.

The persisted current-state projection is a cache. Replay remains the source of truth.

## 8. Context Isolation

PGSP context isolation means each governed session has its own semantic, governance, replay, and communication lineage.

Isolation rules:

- UBTR translation evidence is session-scoped.
- CSA structured intent evidence is session-scoped.
- OCS proposal evidence is session-scoped.
- Governance checkpoint evidence is session-scoped.
- UHCL communication evidence is session-scoped.
- Human response evidence is session-scoped.
- Replay roots are session-scoped.
- Adapter rendering state is adapter-local and must not become canonical context.

Context may cross session boundaries only through explicit cross-session references that are replay-visible and governance-checkable.

## 9. Replay Isolation

Replay isolation requires every session to have a distinct replay root or deterministic replay namespace.

Replay isolation must preserve:

- artifact ordering inside each session;
- replay hash continuity inside each session;
- branch and merge lineage inside each session;
- cross-session reference artifacts when one session cites another;
- archive and restoration evidence;
- failure evidence for incomplete or invalid sessions.

Replay systems may provide aggregate indexes for search or listing, but aggregate indexes must not replace session-local replay as the source of truth.

## 10. Governance Isolation

Governance isolation requires each session to be evaluated independently.

Governance decisions must not leak across sessions unless a cross-session reference explicitly imports evidence and a governance checkpoint accepts that import.

Governance isolation must preserve:

- separate approval status;
- separate authorization status;
- separate provider boundary status;
- separate worker boundary status;
- separate mutation boundary status;
- separate deployment boundary status;
- separate replay boundary status;
- separate human response and confirmation lineage.

One session cannot authorize another session by implication.

## 11. Cross-Session References

Cross-session references allow one session to cite another without merging state.

A cross-session reference must record:

- source session id;
- target session id;
- target replay hash;
- reference purpose;
- referenced artifact or transition id if applicable;
- governance checkpoint for admissibility;
- whether the reference is read-only, advisory, or merge-candidate evidence.

Cross-session references may support:

- replay review;
- governance review;
- diagnostics;
- continuation from prior work;
- branch or merge preparation;
- audit evidence comparison.

Cross-session references must not silently import authority, approvals, authorizations, mutation rights, provider output, or worker output.

## 12. Session Archival

Session archival moves a completed, failed-closed, superseded, or inactive session into long-term audit state.

Archival must record:

- archival timestamp;
- archival reason;
- final lifecycle state;
- final replay hash;
- governance disposition;
- restoration eligibility;
- retention classification;
- known limitations or unresolved gaps.

Archived sessions remain replayable. Archival does not erase governance obligations or authorize future execution.

## 13. Session Restoration

Session restoration reconstructs an archived or inactive session for review, continuation, or successor creation.

Restoration requires:

- replay reconstruction;
- identity verification;
- replay hash verification;
- archival metadata verification;
- governance disposition review;
- adapter identity capture if an adapter is resuming interaction;
- restoration reason.

Restoration outcomes:

| Outcome | Meaning |
| --- | --- |
| `RESTORED_FOR_REVIEW` | Session is available for replay or governance review only. |
| `RESTORED_FOR_CONTINUATION` | Session may continue after resume checks pass. |
| `RESTORED_AS_SUCCESSOR_SOURCE` | Session may seed a new session through explicit cross-session reference. |
| `RESTORATION_FAILED_CLOSED` | Replay or governance evidence is insufficient. |

Restoration must fail closed if replay cannot be reconstructed or if governance state is ambiguous.

## 14. Context Management Strategy

Context management must be explicit, session-scoped, and replay-visible.

Recommended context categories:

| Context Category | Scope | Source of Truth |
| --- | --- | --- |
| Adapter display context | Adapter-local | Adapter state, not canonical |
| Session lifecycle context | Session-scoped | PGSP lifecycle replay |
| Semantic context | Session-scoped | UBTR and CSA artifacts |
| Orchestration context | Session-scoped | OCS artifacts |
| Governance context | Session-scoped | Governance checkpoints |
| Communication context | Session-scoped | UHCL artifacts |
| Cross-session context | Explicit reference | Cross-session reference artifact |
| Archive context | Session-scoped | Archive metadata plus replay |

Implicit global memory must not be used to affect session behavior. If future memory or context services are introduced, they must provide replay-visible evidence and governance checkpoints before influencing PGSP sessions.

## 15. Replay Model

The multi-session replay model requires:

- per-session replay roots;
- session registry replay or ledger;
- session switching artifacts;
- cross-session reference artifacts;
- archival artifacts;
- restoration artifacts;
- replay-derived current projections;
- aggregate indexes that are explicitly non-authoritative.

Canonical reconstruction order:

1. Reconstruct the session registry.
2. Resolve the selected session id.
3. Reconstruct the selected session replay.
4. Reconstruct referenced sessions only when needed.
5. Verify cross-session reference hashes.
6. Derive the current session projection.
7. Run or reference governance checks for any continuation, restoration, branch, or merge.

Replay isolation is the default. Cross-session reconstruction is opt-in and evidence-bound.

## 16. Governance Model

Multi-session governance must evaluate:

- session creation admissibility;
- session switching visibility;
- continuation admissibility;
- suspension and resume admissibility;
- branch and merge admissibility;
- cross-session reference admissibility;
- archival disposition;
- restoration eligibility;
- fail-closed triggers.

Governance must reject:

- hidden context sharing;
- unverified replay references;
- ambiguous active session selection;
- session switching that hides pending obligations;
- cross-session imports without explicit reference evidence;
- restoration from incomplete replay;
- merge by adapter-local convention;
- execution authority inferred from another session.

## 17. Ownership Matrix

| Concern | Session Manager | PGSP Session | Adapter | UBTR | CSA | OCS | Governance | UHCL | Replay |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Session registry | Owns coordination | Registers | Displays | Excludes | Excludes | Excludes | Checks | Excludes | Records |
| Active selection | Owns coordination | Referenced | Requests/displays | Excludes | Excludes | Excludes | Checks visibility | Excludes | Records |
| Session context | Scopes | Owns envelope | Displays | Produces semantic input | Owns structured intent | Owns proposal context | Checks | Owns communication context | Records |
| Session switching | Coordinates | Supplies state | Requests | Excludes | Excludes | Excludes | Checks | Explains state | Records |
| Persistence references | Owns registry metadata | Owns session metadata | Displays | Excludes | Excludes | Excludes | Checks | Excludes | Records |
| Cross-session references | Coordinates | Owns source/target declarations | Requests/displays | Excludes | Excludes | May evaluate | Checks | Explains | Records |
| Archival | Coordinates | Owns disposition | Displays | Excludes | Excludes | Supplies final intent | Checks | Explains | Records |
| Restoration | Coordinates | Reconstructs | Requests/displays | Re-runs or references | Reconstructs | Re-evaluates | Checks | Explains | Reconstructs |
| Provider execution | Excludes | Excludes unless future governed scope permits | Excludes | Excludes | Excludes | Governs request path only | Checks | Excludes | Records if authorized |
| Worker execution | Excludes | Excludes unless future governed scope permits | Excludes | Excludes | Excludes | Governs request path only | Checks | Excludes | Records if authorized |

## 18. Compatibility Strategy

G4-13 does not require immediate runtime changes.

Compatibility requirements:

- current single-session G4-04 and G4-05 flows remain valid;
- G4-11 real PGSP validation remains valid as a single selected session;
- G4-12 lifecycle states remain the canonical state model;
- session manager metadata must be additive;
- replay roots and hashes must remain stable;
- existing adapters may continue to invoke PGSP without multi-session UI;
- future adapters should surface session selection without owning session semantics;
- aggregate session indexes must not invalidate existing replay artifacts.

The multi-session model is a forward architecture contract. It should be implemented incrementally only after replay schema impact is audited.

## 19. Certification Criteria

A future PGSP multi-session implementation is certifiable only if it:

- preserves per-session replay roots;
- preserves per-session governance status;
- prevents implicit context sharing;
- records session switching events;
- distinguishes active, inactive, suspended, completed, failed, archived, and restored sessions;
- reconstructs current session state from replay;
- verifies cross-session references by replay hash;
- fails closed on ambiguous session selection;
- fails closed on incomplete restoration evidence;
- keeps adapters limited to selection, rendering, and response capture;
- prevents approvals, authorization, provider execution, worker execution, mutation, or deployment from leaking across sessions.

## 20. Recommended Implementation Order

Recommended next implementation order:

1. `G4_14_PGSP_MULTI_SESSION_REPLAY_SCHEMA_AUDIT_V1`
2. `G4_15_PGSP_SESSION_REGISTRY_READ_MODEL_V1`
3. `G4_16_PGSP_ADAPTER_SESSION_SWITCHING_CONTRACT_V1`
4. `G4_17_PGSP_SESSION_RESTORATION_VALIDATION_V1`
5. `G4_18_PGSP_CROSS_SESSION_REFERENCE_VALIDATION_V1`

Implementation should begin with replay schema and read-model audits before any interactive multi-session runtime behavior is introduced.

## 21. Final Determination

PGSP can support concurrent and long-lived governed sessions through a session manager architecture that coordinates identity, selection, persistence, isolation, archival, and restoration without changing Platform Core responsibilities.

Existing Generation 4 runtimes remain valid as single-session PGSP instances. Multi-session support should be added through additive registry, replay, and adapter-selection contracts.

Final verdict:

```text
PGSP_MULTI_SESSION_READY
```
