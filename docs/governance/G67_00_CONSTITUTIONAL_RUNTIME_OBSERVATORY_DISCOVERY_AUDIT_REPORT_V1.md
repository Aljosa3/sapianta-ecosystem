# 1. Implementation Summary

Generation: G67-00

Report identity:
G67_00_CONSTITUTIONAL_RUNTIME_OBSERVATORY_DISCOVERY_AUDIT_REPORT_V1

Constitutional baseline: `CONSTITUTIONAL_GOVERNANCE_CLOSED`,
`CANONICAL_TYPED_SEMANTIC_COMPOSITION_CONVERGENCE_ESTABLISHED`,
`CONSTITUTIONAL_EXECUTION_SPINE_CONVERGENCE_ESTABLISHED`,
`PRODUCTION_ENTRY_MODE_CONSTITUTION_REQUIRES_RECLASSIFICATION`,
`CONSTITUTIONAL_PRODUCTION_WORKFLOW_REQUIRES_EXTENSION`,
`CLARIFICATION_PRODUCER_CONSUMER_CONTRACT_CONVERGENCE_ESTABLISHED`, and
`CONSTITUTIONAL_NATURAL_CONVERSATION_CAPABILITY_REQUIRES_IMPLEMENTATION`.

Authenticated repository identity:

- Commit: `0e88c6bfd42bbe050112d5a1a0b3c021a68a9936`
- Tree: `b2cea1a6e47e28c60318576a3e46b31ca0bd5f3b`
- Subject: `G66-19: audit constitutional natural conversation capability`

Input limitation:

The prompt declares G0 through G66-20 authenticated. The authenticated current
tree and local Git history contain G66-19 but no file, commit subject, or
reference identified as G66-20. This audit does not invent G66-20 findings.
All G66-20-specific assertions remain `NOT_VERIFIED`; the current source and
authenticated G0-through-G66-19 evidence are sufficient for the requested CRO
discovery.

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Flow Architecture; G15 Replay Observation Layer; G18 runtime
status projection and root-cause trace; G19 Canonical Presentation; G31 Common
Entry and execution spine; G47 Development Governance; G59 Conversation Layer
V2; G60 Human Interface/Conversation integration; G64 Reuse Proof and
constitutional completion; G65 Constitutional Nervous System; and G66-01
through G66-19.

Reporting date: 2026-08-04.

Objective:

Determine, without implementation or runtime instrumentation, whether the
repository already contains enough certified infrastructure to realize a
passive Constitutional Runtime Observatory that can reconstruct and visualize
the lifetime of a Human Intent without changing any observed owner.

Audit scope and method:

- Authenticated the current Git identity and clean initial worktree.
- Inspected Replay transport, 370 current top-level `reconstruct_*` functions,
  the Replay Observation Layer, unified reconstruction, chain inspection,
  dashboards, runtime inspectors, status projection, root-cause tracing,
  progress visibility, presentation, G65's static nervous-system map, and the
  current G66 Conversation/execution compositions.
- Mapped current evidence for Human input, Conversation, semantic state,
  proposal, validation, Commitment, admission, Governance, Authorization,
  Worker, execution, result, Replay Review, termination, Certification, and
  Human-visible return.
- Distinguished existing event evidence from correlation, visualization, and
  instrumentation.
- Ran focused read-only inspection/reconstruction regressions and governance
  conformance. Test data was confined to pytest temporary roots.

No production runtime, event, instrumentation, API, schema, Replay owner,
workflow, Conversation, Governance, Authorization, Worker, provider,
Certification, baseline, or PCBV31 change is authorized or made.

Primary finding:

The repository contains enough certified infrastructure to build a passive,
post-hoc Constitutional Runtime Observatory with minimal new composition.

The evidence substrate is already substantial:

- immutable owner-local artifacts, wrapper hashes, artifact hashes, timestamps,
  identity fields, predecessor references, and Replay references across the
  current lifecycle;
- deterministic reconstructors for each material owner family;
- G66 Production Conversation Flow Binding with ordered Conversation
  predecessors and owner-local Replay references;
- G66-14 one-lineage default execution evidence through 14 reconstructed
  post-admission stages and final execution Certification;
- G15 normalized Replay observations;
- G18 replay-backed status projection and backward root-cause tracing;
- unified chain reconstruction and read-only CLI chain inspection;
- runtime summaries, Replay ledgers, dashboards, progress snapshots, and
  canonical presentation normalization; and
- G65's machine-readable static map of nodes, transitions, decisions, owners,
  artifacts, reachability, and fail-closed exits.

These capabilities are not one CRO today. They are fragmented by generation,
runtime root, identity vocabulary, artifact recognition tables, and user
surface. No current component accepts a G66 Human Intent/session identity and
returns one normalized, complete, owner-ordered journey from Human entry to
final Certification. No current certified renderer produces all required
sequence, state, decision, timeline, owner, and interruption views from that
journey.

The principal gaps are therefore `missing correlation` and `missing
visualization`, not wholesale `missing evidence` or `missing event capture` for
the established successful G66-14 path. Event capture remains incomplete for
pre-artifact Human-channel entry, failures that occur before any owner persists
evidence, deliberately non-Replay raw provider content, and workflows whose
runtime composition is itself absent, such as the one-chain mutation-to-G64
completion gap identified by G66-16.

A future CRO can remain entirely passive by:

1. reading only authenticated existing evidence;
2. invoking owner-local reconstructors or their pure/read-only modes;
3. correlating existing session, Conversation, Commitment, chain, owner,
   reference, and hash identities;
4. producing an in-memory non-authoritative journey projection; and
5. rendering deterministic views without writing Replay or calling runtime
   owners.

The CRO must not use write-producing observation helpers, progress recorders,
or persisted reconstruction-report modes. Those existing APIs are reusable
evidence precedents, but the passive CRO must select their pure/read-only
operations such as `replay_observation_artifact(...)`, reconstruction with
`persist_report=False`, Replay readers, and existing validators.

Modified modules:

- `docs/governance/G67_00_CONSTITUTIONAL_RUNTIME_OBSERVATORY_DISCOVERY_AUDIT_REPORT_V1.md`
  — this read-only G48 discovery audit.

Intentionally unchanged modules:

- All Human Interaction, Canonical Entry, Conversation, CWM, Semantic Slot,
  proposal, Commitment, Platform Core, Governance, Authorization, Worker,
  provider, execution, result, Replay, termination, Certification,
  Presentation, observability, schema, policy, baseline, PCBV31, adapter,
  bridge, deployment, and test behavior.

# 2. Code Evidence

## Public API

The canonical production entry remains:

~~~python
run_human_interface_runtime_entry(...)
~~~

Existing observation and reconstruction APIs include:

~~~python
replay_observation_artifact(...)
replay_observation_layer_artifact(...)
reconstruct_replay_observation_layer(...)

reconstruct_latest_chain(..., persist_report=False)
reconstruct_chain_by_id(..., persist_report=False)
reconstruct_execution_lifecycle(..., persist_report=False)
reconstruct_full_lineage(..., persist_report=False)

trace_platform_core_root_cause(...)
reconstruct_production_conversation_flow_binding_v1(...)
reconstruct_runtime_progress_replay(...)
reconstruct_post_execution_replay_review(...)
reconstruct_governed_termination_replay(...)
reconstruct_final_execution_certification_binding(...)

present_platform_response(...)
validate_platform_presentation(...)
~~~

The repository currently exposes 370 top-level `reconstruct_*` functions in
334 source modules under `aigol/` and `runtime/`. They are not one consistent
generic API, but they demonstrate broad owner-local deterministic
reconstructability.

Existing Human/operator-facing passive surfaces include:

- `aigol show-latest-chain`, `show-chain`, `show-execution-lifecycle`,
  `show-learning-lifecycle`, `show-full-lineage`, and `show-chain-summary`;
- `aigol dashboard` summary/approvals/bridges/chains/learning/execution;
- Replay summary, ledger, verify, operation report, and explanation commands;
- the read-only runtime operator query CLI; and
- canonical Platform presentation for supported response families.

These are partial entry views. None is the complete G67 CRO.

## Orchestration Entry Point

The observable default production lineage established by current source and
G66 evidence is:

~~~text
./aicli / Human act
-> Canonical Human Entry
-> G66 precedence and Production Conversation Flow Binding
-> G59 source turn / proposal / validation / commit / CWM
-> Candidate Review / exact Human confirmation / readiness / Commitment
-> G60-02 committed-Objective handoff
-> Platform Objective and admission
-> Reuse Proof / G47 / execution preparation
-> exact Human execution authorization
-> Worker request / selection / assignment / dispatch / invocation
-> local or provider execution
-> result capture / validation / capability Completion
-> Post-Execution Replay Review
-> Governed Termination
-> final execution Certification
-> Canonical Human Interface return
~~~

Every material owner after Canonical Entry emits or binds an artifact under the
established successful branch. G66 Flow Binding captures the ordered early
predecessors. G60/G66-14 captures the admitted/authorized execution lineage and
reconstructs 14 late stages. No CRO call is present in this orchestration and
none is required for the workflow to continue.

The existing observation topology is separate and fragmented:

~~~text
owner-local Replay ----> owner-local reconstructors
        |               -> G15 normalized observations
        |               -> G18 status projection/root-cause trace
        |               -> unified chain reconstruction/CLI inspection
        |               -> dashboards/replay summaries
static source map ------> G65 descriptive nervous-system topology
selected responses -----> G19 canonical Presentation
browser evidence -------> development-only governed-execution observatory UI
~~~

The future CRO belongs entirely on the right side of this diagram as a consumer
of already-produced evidence.

## Semantic Reductions

The CRO requires no semantic reduction. It must never interpret Human prose,
create Semantic Slots, assess a proposal, commit CWM, decide readiness, infer
an Objective, select a route, or explain missing evidence with generated facts.

For Conversation, the observable semantic sequence is already encoded by:

~~~text
HUMAN_INTENT_PRECEDENCE
-> INTERPRETER_PROPOSAL
-> PROPOSAL_VALIDATION
-> PROPOSAL_COMMIT
-> HUMAN_CONFIRMATION
-> OBJECTIVE_READINESS
-> OBJECTIVE_COMMITMENT
~~~

The G66 validator rejects invalid order. A CRO may project that order and show
missing stages; it may not complete or repair the sequence.

## Public Validators

Reusable validators and reconstructors already enforce:

- canonical wrapper serialization and Replay hashes;
- artifact hashes, immutable replay indexes, steps, and predecessor order;
- Conversation/session/workspace/CWM identity and revision lineage;
- source-turn, proposal, validation, commit, clarification, confirmation,
  readiness, and Commitment lineage;
- Platform admission, Reuse Proof, G47, capability route, and execution-summary
  lineage;
- execution Authorization and Worker request/selection/assignment/dispatch/
  invocation lineage;
- execution, result capture, result validation, capability Completion, Replay
  Review, termination, and Certification lineage;
- canonical chain ownership, reference/hash matching, ambiguous lineage, and
  multiple-chain ownership; and
- Presentation source-response binding and non-authority flags.

The CRO should delegate validation to each owner-local validator. It should not
replace 370 reconstructors with a second interpretation of their schemas.

## Canonical Data Models

No single CRO model exists. The reusable evidence model families are:

| Region | Existing model/evidence |
|---|---|
| Human/entry | UHI session/turn workspace state, Human request/source hashes, interface/session identity |
| Conversation | CWM V2, Semantic Slots, state-machine transitions, Flow Binding and owner-bound clarification |
| semantic decisions | Interpreter Proposal, Proposal Validation, Proposal Commit, Candidate Review, Human confirmation, readiness, Commitment |
| Platform/Governance | Project Objective, admission context, Reuse Proof, G47 bundle, planning/Durable Work, route and execution preparation |
| authorization/execution | execution summary, Human confirmation, Authorization, Worker request/selection/assignment/dispatch/invocation, execution artifact |
| terminal | result capture/validation, capability Completion, Replay Review, termination, final execution Certification, HIR completion |
| observation | G15 observation artifacts, G18 trace, runtime status projection, progress visibility snapshots |
| static topology | G65 nodes, transitions, decisions, owners, authority classes, artifact types, reachability and source references |

A future CRO may define a non-authoritative view model containing references to
these artifacts. It must not replace or rewrite them.

## Deterministic Algorithms

The evidence-supported passive CRO algorithm is:

1. Accept an existing entry identity such as session, Conversation, Objective,
   chain, Replay, Flow Binding, artifact hash, or owner-local reference.
2. Resolve the permitted evidence roots without path escape or broad
   unauthenticated filesystem discovery.
3. Load wrappers and validate Replay/artifact hashes.
4. Invoke the matching owner-local reconstructors.
5. Follow explicit predecessor references and validated hash bindings.
6. Correlate identity aliases only through recorded bridges; never through
   filename similarity or timestamp proximity alone.
7. Normalize validated references into an in-memory ordered journey.
8. Compare observed owner/stage identities with a versioned static topology.
9. mark missing, ambiguous, corrupt, unsupported, and uncomposed transitions
   explicitly.
10. Render deterministic views from the journey without persisting or invoking
    any observed owner.

Ordering should prefer explicit predecessor order, replay index, revision, and
hash lineage. Timestamps are presentation metadata only because field names and
coverage vary and equal timestamps occur in deterministic tests.

## Responsibility Boundaries

| Responsibility | Existing owner | CRO boundary |
|---|---|---|
| source Human act | Human plus interface adapter | observe recorded provenance; never infer Human authority |
| semantic state/decisions | G59 Conversation | reconstruct only through G59/G66 evidence |
| Objective/admission | Platform Core | display existing admission decision and evidence |
| Governance | Reuse Proof/G47/exact Governance owners | show decision and scope; never reassess or approve |
| Authorization | Human Authority plus Authorization runtime | show exact subject/digest/predecessors; never authorize |
| Worker/provider/execution | exact lifecycle owners | show selection and effects; never dispatch, invoke, retry, or cancel |
| Replay Review | Post-Execution Replay Review owner | display its existing decision; ordinary reconstruction is not Review |
| termination/Certification | exact terminal owners | show terminal evidence; never certify |
| observation/correlation | future CRO presentation owner | read-only view composition with no workflow authority |
| visualization | future CRO renderer | deterministic rendering of validated references only |

## Repository Evidence

### Existing observation families

| Evidence family | Current implementation | Current callers/use | Boundary finding |
|---|---|---|---|
| Replay serialization | `transport.serialization`, `transport.replay`, ledger | nearly every owner | canonical hash/read/write substrate; CRO reuses reads only |
| owner-local reconstruction | 370 `reconstruct_*` functions | owners, certification, inspection, tests | strongest integrity source; fragmented interfaces |
| Replay Observation Layer | `replay_observation_layer.py` | Replay Certification; root-cause trace uses pure observation builder | deterministic categories/stages; persisted generator writes separate observation Replay |
| unified reconstruction | `unified_replay_reconstruction_runtime.py` | CLI chain inspection | generic scan for older chain vocabulary; read-only when `persist_report=False` |
| runtime status projection | private CHE projection in `human_interface_runtime_entry_service.py` | canonical HIR result | reuses flattened and discovered Replay evidence; only selected late-runtime fields |
| root-cause trace | `platform_core_root_cause_trace.py` | Platform Query Router | backward trace from result/projection to runtime stage, Governance, request |
| runtime inspectors | `observability/*` | no non-test production caller found | read-only runtime-store snapshot/lineage; separate older runtime store |
| runtime progress | `runtime_progress_visibility.py`, conversational binding | interactive historical/compatibility flows | useful existing snapshots; recording API is instrumentation and Replay-writing |
| dashboards/summaries | CLI dashboard, Replay report/summary, operator query | explicit `aigol` inspection commands | passive aggregates; narrow artifact recognition and older chain focus |
| canonical Presentation | `platform_presentation_layer.py` | Project Services and semantic capability lifecycle | normalizes selected Platform responses; no whole-lifecycle input |
| static nervous-system map | G65-10 report and JSON map | documentation/static analysis only | 45 nodes, 40 transitions, 19 decisions, 84 artifact types, 22 owners; stale descriptive baseline, not runtime registry |
| browser governed-execution observatory | `browser_companion`, root observatory report/tests | development UI only | deterministic static cards; G66-15 browser path is not canonical production and does not ingest current complete Replay |
| Replay experience specification | `AIGOL_REPLAY_EXPERIENCE_V1.md` | product guidance | defines personas/navigation/timeline fields; does not implement visualization |

### Static topology evidence

The authenticated G65 map declares:

~~~text
descriptive_only: true
runtime_registry: false
grants_authority: false
authorizes_execution: false
authorizes_mutation: false
static_reconstruction_only: true
exhaustive_dynamic_reachability_claimed: false
~~~

It contains 45 nodes, 40 transitions, 19 decisions, 17 entry points, 84
artifact types, 22 owners, 21 authority classes, 17 fail-closed exits, eight
reachability records, and 57 source references. It is an excellent view
ontology seed, but it predates G66-13/14/18/19 changes and cannot be treated as
the current event registry.

### Current reconstruction coverage

Current source contains 370 top-level reconstruction functions across 334
modules. The count has increased from the 355 recorded by G66-15, which
confirms continued owner-local evidence growth and also reinforces the need for
an adapter/correlation catalog rather than another generic parser.

Focused observability regressions passed 53 tests across Replay observation,
unified reconstruction, CLI chain inspection, session dashboard, root-cause
trace, runtime progress, and canonical Presentation. They validate existing
capabilities under temporary roots; they do not establish a single CRO.

## Capability Inventory

| Capability | Owner | Certified generation | Current purpose | Observable? | Reusable? | Passive? | Requires modification? |
|---|---|---|---|---:|---:|---:|---|
| immutable Replay wrapper/hash substrate | Replay/transport owners | foundational through G31 | persist and verify owner evidence | yes | yes | reads are passive | no |
| owner-local reconstructors | each exact artifact owner | G31-G66 | validate one owner lineage | yes | yes, preferred | yes | no |
| Production Conversation Flow Binding | G66 Conversation binding owner | G66-07/13/18 | ordered early owner/predecessor correlation | yes | yes | reconstruction is passive | no |
| CWM/Slot revision state | G59 Conversation | G59-01..07 | durable semantic state and protocol transitions | yes | yes | read/reconstruct only | no |
| G60/G66-14 execution completion capture | G60 orchestration plus exact owners | G60-02/03, G66-14 | correlate admitted lineage through 14 late stages | yes | yes | reconstruction is passive | no |
| Replay Observation Layer pure builders | Platform Core observation owner | G15-01 | normalize an artifact into stage/category/severity | yes | yes | pure builders yes | no |
| Replay Observation Layer persisted generator | Platform Core observation owner | G15-01 | write observation Replay for certification | yes | bounded | no; it writes | CRO must not call write mode |
| unified Replay reconstruction | Replay inspection owner | G13-era current surface | scan canonical-chain evidence and validate references | yes | yes | yes with `persist_report=False` | extend recognition through adapters, not source schemas |
| CLI chain inspection | operator presentation | current Product 1 surface | read-only chain/lifecycle summary | yes | yes | yes | no for reuse; insufficient alone |
| runtime-store inspector/snapshot | runtime observability owner | pre-G32 certified surface | inspect dispatch/result/capability/policy/continuity/lineage | yes | bounded | yes | adapter needed for G66 roots |
| CHE runtime status projection | Canonical HIR projection owner | G18-05/07 | project provider/Worker/Certification reachability | yes | yes | reads only | no; private narrow helper |
| Platform root-cause trace | Platform Core Replay | G18-09 | deterministic backward causal trace | yes | yes | yes | mappings need broader coverage for CRO |
| runtime progress snapshots | progress visibility owner | G17/G18-era | stage/activity/elapsed/ETA visibility | yes | read side yes | reader yes; recorder no | no event insertion permitted |
| conversational progress binding | Human-interface progress projection | G17 | bind historical turn to eight visibility stages | yes | limited | reader yes | current G66 stage model adapter needed |
| Replay summary/operation ledger | operator Replay owner | current operator surface | aggregate operation results and missing evidence | yes | yes | yes | no; narrow scope |
| session dashboard | operator dashboard | current Product 1 surface | approvals, bridges, chains, learning, execution requests | yes | yes | yes | artifact recognition adapter needed |
| canonical Presentation | Platform Core Presentation | G19-06 | normalize selected Platform responses | yes | yes | yes | new CRO extractor/view type required; existing source types unchanged |
| static nervous-system map | governance evidence owner | G65-10 | source-level topology/owners/decisions/reachability | static only | yes | yes | version/update overlay required |
| Post-Execution Replay Review | Replay Review owner | G31/G66-14 | authority-bearing review after result validation | yes | yes as evidence | reconstructor yes | no |
| Governed Termination | termination owner | G31/G66-14 | close reviewed operation | yes | yes as evidence | reconstructor yes | no |
| final execution Certification | Certification owner | G31/G66-14 | certify exact terminated execution | yes | yes as evidence | reconstructor yes | no |
| browser observatory cards | browser companion UI | development evidence | static execution-layer display | partial | visual precedent only | rendering is passive | cannot be promoted unchanged |
| Replay experience specification | product experience owner | current product guidance | personas, navigation and timeline requirements | descriptive | yes | yes | implementation required |

## Runtime Event Inventory

| Event class | Existing event/artifact evidence | Coverage | Sufficient for reconstruction? |
|---|---|---|---|
| Human input | UHI workspace/turn record, exact request/source-turn binding, request/session hashes | `PARTIAL` | yes from Canonical Entry onward; terminal invocation before first persisted act is not standardized |
| Conversation | CWM envelope/state, Conversation identity, revisions, state-machine transitions, Flow Binding | `OBSERVABLE` | yes through owner validators |
| State transition | Proposal Commit, CWM revisions, protocol transitions, progress snapshots, owner status artifacts | `OBSERVABLE_FRAGMENTED` | yes owner-local; generic cross-owner state vocabulary missing |
| Decision | precedence, route, readiness, admission, Governance, Human confirmation, Authorization, Review, Certification | `OBSERVABLE` | yes when each owner emits its artifact |
| Validation | proposal, CWM, readiness, admission, result, Replay, conformance and Certification validators | `OBSERVABLE` | yes; validation subjects must remain distinct |
| Replay | wrapper index/step/event/hash plus owner reconstructors | `OBSERVABLE` | yes owner-local |
| Authorization | exact Human confirmation, execution summary, execution Authorization artifacts | `OBSERVABLE` | yes |
| Worker selection | resource selection, invocation request, assignment and selection evidence | `OBSERVABLE` | yes |
| Execution | dispatch, invocation, local/provider execution, output and result capture | `OBSERVABLE` | yes for completed/persisted stages |
| Termination | Replay Review, termination evidence/classification/result, final Certification | `OBSERVABLE` | yes |
| Presentation | Canonical Presentation for supported Platform responses; HIR completion return | `PARTIAL` | source result is visible; exact terminal bytes and every service family are not uniformly persisted |
| Clarification | owner-bound envelope, context reference, question, required code/control and restoration evidence | `OBSERVABLE` | yes |
| Proposal | source turn, Interpreter Proposal, Proposal Validation and candidate operations | `OBSERVABLE` | yes, subject to content/privacy boundaries |
| Commitment | candidate digest, exact Human confirmation, readiness and immutable Objective Commitment | `OBSERVABLE` | yes |
| Admission | committed projection, Platform Objective, admission status/context | `OBSERVABLE` | yes |
| Governance | Reuse Proof, G47 bundle/planning evidence and execution-ready preparation | `OBSERVABLE_FRAGMENTED` | yes through exact roots; one universal index is absent |

Existing events are sufficient for post-hoc reconstruction of the established
successful non-mutating G66 path. They are not a complete live event stream.
Polling existing evidence remains passive but can only observe artifacts after
their owners persist them.

## Evidence Inventory

| Evidence subject | Existing authenticated artifact family | Principal correlation |
|---|---|---|
| Intent | Human request/source binding and Human Intent precedence | session, interface, workspace, request/source digest |
| Conversation | CWM envelope/state, state transitions, Production Flow Binding | Conversation identity, CWM identity/revision/hash |
| Proposal | Interpreter Proposal, validation and Proposal Commit | source-turn identity/digest, proposal identity/hash, expected revision |
| Objective | Candidate Review, confirmation, readiness, Commitment, Platform Objective | candidate/objective digest, Commitment identity/hash, project context |
| Authorization | execution summary, exact Human confirmation, Authorization artifact | summary hash, actor, session, authorization identity/hash |
| Worker | selection, invocation request, assignment, dispatch and invocation | chain, request/assignment/dispatch/invocation identities and hashes |
| Execution | execution artifact, provider/local evidence, result capture/validation | invocation, execution, result identities and predecessor hashes |
| Replay | wrappers, references, indexes, steps, event types and reconstructors | filesystem reference, wrapper hash, artifact hash |
| Governance | Reuse Proof, G47 record, planning/Durable Work, dry-run/execution-ready evidence | Objective/scope, chain, owner references and hashes |
| Presentation | Canonical Presentation and HIR completion result | source-response hash, presentation hash, session return |
| Termination | Replay Review, termination, final Certification | chain identity and validation/review/termination hashes |
| hash lineage | `artifact_hash`, `replay_hash`, source/predecessor hashes | deterministic hash equality |
| owner lineage | explicit owner fields, stage-specific artifact types, G65 owner map | owner identity plus validator/reconstructor |
| state lineage | revision, semantic revision, prior-state and predecessor references | CWM/Conversation/chain state sequence |

No evidence family needs replacement. CRO correlation must retain reference to
the exact source artifact and owner validator for every displayed fact.

## Correlation Capability Assessment

Current evidence supports these correlation axes:

| Axis | Current capability | Assessment |
|---|---|---|
| session | UHI, Canonical Entry, clarification and G66 binding fields | strong in early/multi-turn lineage |
| Conversation | Conversation/CWM identities and revisions | strong through Commitment |
| Objective | readiness/Commitment and G60 committed projection | strong at Conversation-to-Platform handoff |
| Replay | paths, wrapper hashes, indexes, steps and reconstructors | strong owner-local |
| Flow Binding | ordered predecessors and owner-local Replay references | strong for G66 early stages |
| owner | explicit owners, artifact types and G65 map | strong but vocabulary is distributed |
| artifact hash | pervasive artifact and predecessor hashes | strongest cross-owner integrity key |
| canonical chain | late Platform/Governance/Worker families and older unified reconstruction | strong where present; not universal at initial Human turn |

Correlation gaps:

- no one journey identity is mandatory from terminal entry through final
  Certification across every current branch;
- early G66 uses session/Conversation/Flow Binding identities while many late
  and historical tools index by `canonical_chain_id` or operation ID;
- unified reconstruction recognizes a closed older set of artifact, identity,
  reference, and timestamp fields and does not natively model all G59/G66
  artifacts;
- references vary between logical identity, filesystem path, Replay directory,
  wrapper hash, and artifact hash;
- timestamps use several field names and are sometimes deliberately identical;
- the G65 static map predates current G66 topology and is not a runtime registry;
  and
- read-only, non-mutating execution, accepted-mutation, and G64 constitutional
  completion are conditional branches rather than one universal linear chain.

A future resolver can bridge these axes through existing recorded handoffs and
hashes. It must fail closed rather than correlate by filename, timestamp, or
similar text alone.

## Observability Gap Analysis

| Lifecycle region | Observability | Gap type | Exact finding |
|---|---|---|---|
| shell/Human Enter before first canonical artifact | partial | missing event capture | process invocation and keystroke arrival are not one authenticated runtime event; first reliable evidence begins at adapter/CHE capture |
| Canonical Entry and source intent | observable | missing correlation | evidence exists but no universal journey index links every downstream branch |
| Conversation through Commitment | observable | missing visualization | ordered G66/G59 evidence is complete; no complete journey renderer consumes it |
| Platform admission/Governance | observable but distributed | missing correlation | artifacts span Project Services, Reuse Proof, G47 and preparation roots |
| Authorization through final Certification | observable | missing visualization | G66-14 proves one lineage and 14 late reconstructions; no CRO view aggregates it with early Conversation |
| read-only Self/Platform branch | observable | missing correlation/visualization | terminates correctly without execution; generic execution-centric tools can misrepresent absent stages unless branch-aware |
| accepted mutation branch | partially connected | missing correlation | G31 evidence exists, but G66-16 found no single default G66-to-G64 provenance chain |
| G64 constitutional completion | owner-local observable | missing workflow composition | finalizer evidence exists, but absent production caller cannot be visualized as traversed default state |
| live in-progress transient state | partial | missing event capture | only existing progress-enabled flows emit snapshots; passive polling cannot observe unpersisted call-stack state |
| failed-before-write transitions | invisible | missing event capture | no evidence exists to reconstruct a failure before its owner writes any fail-closed artifact |
| raw provider content | intentionally invisible to Replay in bounded paths | constitutional exclusion | CRO may show provider identity/status/hash, not invent or recover prohibited content |
| complete CRO views | absent | missing visualization | no certified sequence/state/decision/intent/timeline/owner/interruption renderer over current G66 lineage |

The audit does not recommend filling intentional content exclusions or
instrumenting every call. A passive CRO must display `NOT_OBSERVED`,
`NOT_RECORDED`, `INTENTIONALLY_EXCLUDED`, `NOT_REACHED`, `UNCOMPOSED`, and
`CORRUPT` as distinct states.

## Visualization Readiness Assessment

Existing evidence can already support:

| View | Readiness | Existing inputs | Remaining work |
|---|---|---|---|
| sequence diagram | `READY_WITH_CORRELATION` | ordered G66 predecessors, G66-14 late stages, owner map | join early and late identities; branch-aware ordering |
| state diagram | `READY_WITH_NORMALIZATION` | CWM/protocol revisions and owner status artifacts | map distinct owner states without merging authority |
| decision tree | `READY_WITH_STATIC_OVERLAY` | G65 decisions/fail-closed exits and current decision artifacts | update/version topology for G66-13..19 |
| intent journey diagram | `PARTIAL` | session, source turn, Flow Binding, Commitment and late chain | add fail-closed identity bridge and branch model |
| runtime timeline | `READY_WITH_LIMITS` | timestamps, revisions, replay indexes and predecessor order | treat timestamps as metadata; show missing timestamps explicitly |
| constitutional owner map | `READY` | G65 owners/nodes/authority classes plus current owner evidence | apply current-version overlay; never imply dynamic reachability from static map |
| workflow interruption map | `READY_WITH_GAP_CLASSIFICATION` | fail-closed artifacts, missing-evidence trace, G65 exits | normalize `NOT_REACHED` versus corrupt/missing/uncomposed |

The root `GOVERNED_EXECUTION_OBSERVATORY_V1.md` and browser companion provide
a development-only UI precedent with deterministic cards and explicit
input/output/authority/boundary/status labels. It is not current CRO runtime
evidence: the browser path is noncanonical under G66-15, the UI does not read
the complete G66 Replay lineage, and its tests explicitly prohibit live runtime
architecture.

The Replay Experience specification already defines operator, auditor,
executive, and developer personas; stable identifier navigation; timeline
fields; raw-evidence drill-down; missing-evidence handling; and source hashes.
It can guide CRO presentation without changing runtime.

## Passive Layer Assessment

| Required CRO behavior | Entirely passive today? | Evidence-based condition |
|---|---:|---|
| observe | yes, post-persistence | read existing wrappers/artifacts only |
| correlate | partially | existing keys suffice, but one new read-only resolver is needed |
| reconstruct | yes, owner-local | call exact reconstructors; generic aggregation is missing |
| visualize | not implemented | rendering can be passive once correlation view exists |
| avoid workflow change | yes | CRO has no production caller or successor role |
| avoid Replay change | yes | use read-only/pure modes; do not persist observation/reconstruction reports |
| avoid Governance change | yes | render existing Governance evidence only |
| avoid Conversation change | yes | read Flow Binding/CWM; never mutate or parse Human input |
| avoid Authorization change | yes | render exact Authorization; never create it |
| avoid Worker/execution change | yes | no dispatch/invocation/retry/cancel API is required |

The strongest passive building blocks are pure observation construction,
owner-local reconstruction, unified reconstruction with
`persist_report=False`, read-only dashboards/inspectors, root-cause trace, and
Presentation normalization.

APIs that write observation Replay, reconstruction reports, progress snapshots,
or diagnostic evidence must not be invoked by the passive CRO. Reusing their
schemas or pure helpers does not authorize their write behavior.

## Reuse Matrix

| Capability | Current owner | Current purpose | Reusable for CRO | Modification required | Certified generation |
|---|---|---|---:|---|---|
| canonical serialization/hash loading | Replay transport | verify immutable evidence | yes | none | foundational |
| owner-local reconstructors | exact artifact owners | reconstruct one lineage | yes | none | G31-G66 |
| G66 Flow Binding | Conversation binding | ordered semantic lineage | yes | none | G66-07/13/18 |
| G60/G66 execution completion | G60 orchestration | correlate/reconstruct late execution | yes | none | G60-02/03, G66-14 |
| pure Replay observation | Platform Core observation | normalize category/stage/severity | yes | recognition adapter only | G15-01 |
| unified reconstruction | Replay inspection | generic chain scan | yes | extend via non-invasive adapters | G13-era current surface |
| runtime status projection | Canonical HIR | project late-stage reachability | yes | expose through CRO adapter, not API mutation | G18-05/07 |
| root-cause trace | Platform Core Replay | causal backward trace | yes | broader field mappings optional | G18-09 |
| runtime progress reader | visibility owner | reconstruct existing progress | yes | none; recorder forbidden | G17/G18-era |
| chain inspection/dashboard/summary | operator presentation | human-readable read-only aggregation | yes | compose, do not replace | current Product 1 |
| Canonical Presentation | Platform Core Presentation | normalized supported response | yes | add separate CRO view extractor later | G19-06 |
| static nervous map | governance evidence | owner/topology model | yes | versioned current overlay | G65-10 |
| Replay experience specification | product experience | personas/navigation/timeline | yes | implement renderer | current product guidance |
| browser observatory UI | development UI | static layer cards | design precedent only | cannot reuse as canonical data path | development evidence |

## Reuse Impact Assessment

1. Which existing certified capabilities are reused?

   A CRO would reuse immutable Replay wrappers and hashes; 370 owner-local
   reconstructors; G66 Production Conversation Flow Binding; G59 CWM, Slot,
   proposal, readiness and Commitment evidence; G60/G66-14 execution
   completion and 14 late-stage reconstructions; G15 pure Replay observation;
   G18 status projection and root-cause tracing; unified Replay reconstruction;
   read-only chain inspection, dashboards, summaries and runtime inspectors;
   G19 canonical Presentation; G65's static nervous-system map; and existing
   Replay Review, termination and Certification reconstructors. Focused source
   review and 53 passing observability regressions establish these reusable
   capabilities.

2. Which new capabilities, if any, would actually be required to realize the Constitutional Runtime Observatory?

   Four bounded, passive composition capabilities are required: a versioned
   lifecycle/artifact adapter catalog; a fail-closed correlation resolver that
   bridges session, Conversation, Commitment, chain, owner, Replay reference
   and artifact hash; an in-memory non-authoritative journey/gap projection;
   and deterministic renderers for the required diagrams, timeline, owner and
   interruption views. A current-version overlay for the G65 static map is also
   required. No new runtime events, instrumentation, owner schemas, Replay
   writer, workflow API, Governance decision, Conversation operation,
   Authorization, Worker, or Certification capability is required for post-hoc
   observation.

3. Does any currently certified capability become unreachable?

   No. This audit changes no code. A correctly implemented CRO reads existing
   evidence after owners act and does not become a predecessor or successor in
   any production decision. Every certified production, compatibility,
   development, Replay-only, and test capability retains its present
   reachability and classification.

4. Would the Constitutional Runtime Observatory create a parallel production path?

   No. It is a read-only consumer outside the production workflow. It neither
   accepts Human intent as a production ingress nor calls Conversation,
   Platform, Governance, Authorization, Worker, provider, execution, Replay
   Review, termination, or Certification as an authority-bearing successor.
   Promoting the browser companion or a persisted observation workflow as a
   production peer would violate this boundary and is not recommended.

5. Would the Constitutional Runtime Observatory increase or decrease the number of production workflows?

   Neither. It would add one passive view over existing evidence, not a
   production workflow. Read-only, non-mutating, mutating, and constitutional
   completion branches remain the same conditional branches within the one
   canonical entry topology. The CRO must represent uncomposed gaps rather
   than creating transitions to close them.

## Constitutional Recommendation

The repository is ready for a separately authorized minimal CRO implementation
that performs post-hoc, read-only correlation and visualization only.

That implementation should:

1. consume explicit authenticated evidence roots and stable entry identities;
2. use owner-local reconstructors as the source of integrity truth;
3. normalize references in memory without rewriting source Replay;
4. use a versioned current overlay over the descriptive G65 map;
5. distinguish observed, not reached, missing, corrupt, intentionally excluded,
   unsupported and uncomposed states;
6. preserve raw-source references and hashes for drill-down;
7. keep timestamps presentation-only and prefer predecessor/hash order;
8. implement deterministic sequence, state, decision, journey, timeline, owner
   and interruption views;
9. expose no dispatch, invoke, retry, cancel, approve, authorize, commit,
   certify, promote, mutation, or Replay-write operation; and
10. remain outside Canonical Human Entry and every production workflow.

No event insertion or runtime instrumentation is recommended for the first
CRO. If future real-time pre-artifact telemetry is required, it needs a
separate constitutional audit because it would cross the present passive,
post-hoc evidence boundary.

# 3. Constitutional Self-Assessment

## Verified

- The current repository contains broad deterministic owner-local Replay and
  reconstruction capability.
- Current source contains 370 top-level `reconstruct_*` functions across 334
  modules.
- G66 Flow Binding preserves ordered early Conversation predecessors and
  owner-local Replay references.
- G66-14 preserves one default admitted execution lineage through 14
  reconstructed late stages and final execution Certification.
- G15 supplies deterministic observation normalization and explicit
  non-authority boundaries.
- G18 supplies Replay-backed status projection and deterministic root-cause
  tracing.
- Unified reconstruction, CLI chain inspection, dashboards, Replay summaries,
  runtime inspectors, progress readers, and canonical Presentation are
  implemented in bounded scopes.
- The G65 map is machine-readable, descriptive-only, non-authoritative, and a
  useful static topology baseline.
- Existing evidence supports session, Conversation, Objective, Replay, Flow
  Binding, owner, artifact-hash and late canonical-chain correlation.
- No universal Human-Intent journey index or complete current G66 CRO renderer
  exists.
- The principal implementation gaps are correlation, normalization, gap
  classification and visualization.
- A post-hoc CRO can remain passive without changing production runtime or
  Replay.
- Write-producing observation/progress/report APIs are not required and must
  be excluded from a passive CRO.
- The browser observatory is development UI evidence, not a canonical CRO
  production path.
- No runtime, event, instrumentation, API, schema, Replay, workflow, baseline,
  PCBV31, or test file was changed.

## Not Verified

- No G66-20 artifact or Git-history identity is present; G66-20-specific
  findings are not verified.
- No complete current runtime journey was reconstructed by a single existing
  CRO API because no such API exists.
- Exhaustive live observation before artifact persistence is not established.
- Failures before any evidence write remain unobservable.
- Exact terminal keystroke arrival and terminal-rendered bytes are not one
  uniform authenticated event family.
- Raw provider content intentionally excluded from Replay is not observable and
  must not be reconstructed.
- One default provenance chain through accepted mutation and G64
  constitutional completion remains unestablished as recorded by G66-16.
- No live provider, external Worker, browser, GUI, Web server, REST/API, Speech,
  Agent-to-Agent transport, deployed process, container, or external production
  system was invoked.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact top-level sections and standard Code Evidence subsections | deterministic heading review | `PASS` |
| authenticated baseline | current commit/tree/subject and clean initial worktree | exact Git inspection | `PASS` |
| prompt G66-20 baseline | tree/history/reference search | no artifact found | `NOT_VERIFIED_INPUT_LIMITATION` |
| Replay inventory | transport, observation, unified reconstruction and owner reconstructors | current source search/review | `PASS` |
| reconstruction count | top-level definitions under `aigol/` and `runtime/` | 370 functions across 334 modules | `PASS` |
| Conversation evidence | G59/G66 state, predecessor and binding evidence | current source and accepted G66 reports | `PASS` |
| admission/execution evidence | G60/G66-14 preparation and 14-stage completion | current source and focused baseline | `PASS` |
| runtime event inventory | 16 required event/transition classes | artifact/caller/reconstructor correlation | `PASS_WITH_EXPLICIT_GAPS` |
| evidence inventory | Intent through state/owner/hash lineage | artifact family review | `PASS` |
| correlation capability | session, Conversation, Objective, Replay, Flow Binding, owner, hash, chain | exact field/reference review | `PARTIAL_COMPOSITION_REQUIRED` |
| passive observation | pure/read-only modes and authority flags | source and test review | `PASS_POST_HOC` |
| visualization readiness | seven required view types | evidence and product/static UI review | `READY_WITH_CORRELATION` |
| focused observability regression | seven observation/reconstruction/presentation modules | pytest: 53 passed | `PASS` |
| governance regression | `tests/test_governance_conformance.py` | pytest: 5 passed | `PASS` |
| governance conformance | read-only engine | 20 passed, 0 failed, 0 warnings, 0 critical violations, `CONFORMANT` | `PASS` |
| Reuse Impact Assessment | five exact required questions | deterministic review | `PASS` |
| document consistency | six headings, inventories, gap classes, five Reuse questions, recommendation and one verdict | deterministic review | `PASS` |
| whitespace integrity | complete repository diff and added report | `git diff --check`; no-index check produced no whitespace errors | `PASS` |

# 5. Repository Mutation Summary

Added one governance evidence artifact:

- `docs/governance/G67_00_CONSTITUTIONAL_RUNTIME_OBSERVATORY_DISCOVERY_AUDIT_REPORT_V1.md`

No production Human Interaction, Canonical Entry, Conversation, CWM, Semantic
Slot, proposal, Commitment, Platform Core, Governance, Authorization, Worker,
provider, execution, result, Replay, termination, Certification, Presentation,
observability, schema, policy, baseline, PCBV31, adapter, bridge, deployment, or
test file changed.

This report creates no runtime event, instrumentation, trace store,
observability schema, route, decision, admission, authority, Authorization,
Worker invocation, execution, Replay evidence, Certification, workflow, or
production identity.

All focused test mutations were confined to pytest temporary roots and removed
with them. No repository runtime evidence store or external system was used.

Unrelated pre-existing changes:

- None. The worktree was clean at audit start.

# 6. Certification Verdict

CONSTITUTIONAL_RUNTIME_OBSERVATORY_DISCOVERY_COMPLETED
