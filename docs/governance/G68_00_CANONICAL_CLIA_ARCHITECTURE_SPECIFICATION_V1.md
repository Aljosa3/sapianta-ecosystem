# 1. Implementation Summary

Generation: G68-00

Report identity:
G68_00_CANONICAL_CLIA_ARCHITECTURE_SPECIFICATION_V1

Constitutional baseline: G0 through G67-06, including
`CONSTITUTIONAL_GOVERNANCE_CLOSED`, Canonical Human Entry, Conversation
Runtime, Semantic Slot Composition, Proposal Validation, Proposal Commit,
Objective Commitment, Platform Admission, Governance, Authorization, Worker
Execution, Replay, Certification, and the Constitutional Runtime Observatory.

Authenticated repository identity:

- Commit: `f1b903239be0f15779795c02d34c76f053a0ffd9`
- Tree: `47055ade50918c2f5999385f838c141d3bcccf80`
- Subject: `G67-06: establish constitutional runtime observatory visualization`
- Immediate parent: `87a865b99f7d47b3308274298cf0c826f51efbb9`
- Parent subject: `G67-05: establish constitutional runtime observatory passive composition`

Implementation contracts: G48 Constitutional Evidence Reporting Standard V1;
Constitutional Architecture Specification V1; Canonical Layer Model;
Constitutional Flow Architecture; G31 Common Entry; G47 Development
Governance; G58 Conversation Interpreter architecture; G59 Conversation Layer
V2; G60 Human Interface/Conversation integration; G66-15 Production Entry
Mode audit; G66-19 Natural Conversation capability audit; and G67-00 through
G67-06 Constitutional Runtime Observatory evidence.

Reporting date: 2026-08-04.

Objective:

Specify a completely new future Canonical CLI Human Interaction Channel named
CLIA, the Constitutional Line Interface for AiGOL. CLIA is defined directly
from the constitutional workflow as a thin interactive session and transport
adapter into the existing Canonical Human Entry. It does not inherit the
implementation topology, parser modes, local workflow state, or historical
artifact families of any current CLI.

Implementation scope:

- define one future canonical CLI channel and one canonical execution lineage;
- define the CLIA/CHE boundary and transport-only responsibilities;
- classify the authenticated current CLI landscape and its intended future
  disposition;
- define Natural Conversation, passive CRO, and future-adapter placement; and
- define a non-parallel, separately authorized migration strategy.

No CLIA executable, package, API, schema, parser, adapter, session store,
runtime caller, route, migration, deprecation, or production-path change is
implemented or authorized by this specification.

Modified modules:

- `docs/governance/G68_00_CANONICAL_CLIA_ARCHITECTURE_SPECIFICATION_V1.md`
  — this architecture specification only.

Intentionally unchanged modules:

- `aicli`, `aigol/cli/aicli.py`, `aigol/cli/aigol_cli.py`, and
  `aigol/acli_next/`;
- `run_human_interface_runtime_entry(...)` and every Conversation, CWM,
  Semantic Slot, Proposal, Commitment, Platform, Governance, Authorization,
  Worker, execution, result, Replay, termination, and Certification owner;
- G67 CRO core, Query Interface, CLI transport, passive composition,
  visualization, `cro` launcher, catalog, and topology;
- all browser, bridge, provider, repository, policy, schema, baseline, PCBV31,
  deployment, and test behavior.

Architectural boundaries preserved:

- this document creates no runtime reachability or authority;
- current default `./aicli` and default `aigol next` classifications are not
  changed before a later certified cutover;
- Canonical Human Entry remains the sole production entry contract;
- all semantic and execution decisions remain with their established owners;
- CRO remains passive and cannot become a runtime predecessor; and
- no historical, compatibility, development, or inspection CLI is promoted.

## Architectural Motivation

G66-15 authenticated a singular normative production spine but also found
multiple Human-accessible surfaces with different entry behavior. Default
`./aicli`, its `submit` mode, and default `aigol next` delegate to Canonical
Human Entry. Explicit `aicli` Conversation modes bypass it at initial ingress;
named ACLI Next modes call older runtime families; historical `aigol` commands
enter HIRR/OCS/PPP/PGSP-era graphs; development commands can call provider,
Worker, mutation, or bridge owners directly; and inspection CLIs observe
evidence without entering the workflow.

G66-19 further established that unrestricted Natural Conversation is defined
as an untrusted proposal capability after canonical entry, but is not composed
into the current default production path. G67 then established a passive
observatory whose evidence correlation and query surfaces are separate from
runtime authority.

Those capabilities are individually bounded, but their accumulated launchers
and historical names do not provide one durable future identity for a Human
CLI session, its canonical evidence, or its CRO Journey. Repairing every old
transport would retain their topology as an architectural constraint. G68-00
therefore specifies a new channel identity with one responsibility: transport
exact Human acts to the already-established Canonical Human Entry and present
the exact response.

## Current Human Interaction Landscape

The authenticated landscape at G67-06 is:

| Surface | Authenticated behavior | Constitutional relation |
|---|---|---|
| default `./aicli` and `submit` | reference UHI adapter calls Canonical Human Entry | present canonical CLI channel/adapter |
| `aicli conversation-v2` | calls the G60/G59 Conversation terminal directly | compatibility ingress; initial CHE bypass |
| `aicli conversation-execute-v2` | calls the G60 complete terminal directly | compatibility parallel Human ingress |
| default `aigol next` | presentation path calls Canonical Human Entry | present canonical adapter |
| named `aigol next` modes and `aigol/acli_next/` | call retained ACLI Next runtimes | compatibility, not a canonical peer |
| historical conversational `aigol` commands | call older semantic/workflow families | historical |
| direct execution/provider/MOC/operator commands | call bounded development owners | development only |
| `sapianta_bridge` CLIs | call a separate retained bridge stack | compatibility/admin only |
| root `sapianta` | tracked launcher targets code absent from the authenticated tree | historical |
| `./cro` | explicit passive G67 observation composition | internal observability; not a Human Interaction Channel |
| runtime audit/certification and conformance CLIs | explicit validation scenarios | development only |

This architecture does not infer equivalence from a shared terminal, parser,
function name, or Human caller. A Human Interaction Channel is canonical only
when its ordinary production turns terminate at the sole Canonical Human Entry
without an alternate semantic, admission, or execution route.

# 2. Code Evidence

## Public API

The authenticated current Canonical Human Entry remains:

~~~python
run_human_interface_runtime_entry(...)
~~~

Its docstring states that it enters the certified runtime from any Unified
Human Interface. G66-15 reconstructs the non-test CLI callers as default
AiCLI and default `aigol next`; it separately classifies direct G60 terminals
and older CLI families.

G68-00 specifies, but does not implement, this future transport relation:

~~~text
CLIA interactive transport
-> exactly one Canonical Human Entry invocation for each submitted Human act
-> exact CHE response presentation
~~~

No public `clia` function, executable, request schema, or parser exists in the
authenticated tree. Names used below for CLIA envelopes and bindings are
architectural roles, not new APIs or canonical data types.

## Orchestration Entry Point

The sole future canonical execution path is:

~~~text
Human
-> CLIA
-> Canonical Human Entry
-> Conversation Runtime
-> Semantic Slots / CWM
-> Proposal Validation
-> Proposal Commit
-> Candidate Review
-> Exact Human Confirmation
-> Objective Commitment
-> Platform Admission
-> Governance
-> Authorization
-> Worker
-> Execution
-> Replay
-> Certification
~~~

CLIA invokes no stage after Canonical Human Entry. A response returning from
any downstream owner travels back through the owning runtime and CHE before
CLIA presents it. Presentation does not reverse authority or make CLIA an
owner of the response.

The path is singular by owner lineage, not by the number of permitted future
transport technologies. A future GUI, REST, Browser, Speech, or Agent-to-Agent
adapter may transport an eligible source act only to the same CHE boundary.
It cannot create a second Conversation, Platform, execution, or evidence
lineage.

## Semantic Reductions

CLIA performs no semantic reduction. In particular, it must not:

- classify prose, commands, Human intent, or work type;
- construct, update, confirm, or commit Semantic Slots or CWM state;
- generate, validate, accept, reject, or commit a proposal;
- interpret natural assent as Candidate confirmation, Objective Commitment,
  execution Authorization, acceptance, or any other Human authority act;
- convert a display selection into an owner decision; or
- infer a route from free-form content, prior prompts, filenames, or local
  session state.

The exact source act is transported without semantic normalization. Encoding,
line-ending, terminal-escape, and size checks may protect the transport, but
they may not rewrite content. Conversation and its certified interpreter
proposal boundary remain the first semantic owners after CHE.

## Public Validators

CLIA may validate only its transport contract:

- required local session binding is present;
- actor and channel credentials are presented to CHE rather than interpreted
  locally;
- one submitted turn has one exact byte/text representation;
- explicit attachment or continuation references are structurally bounded;
- response envelopes are complete enough to render; and
- duplicate submission, transport timeout, stream failure, or malformed CHE
  response fails closed without retrying as a new Human act.

CHE and the existing owners retain validation of Human identity, session and
workspace scope, intent precedence, continuation ownership, source-turn
identity, Conversation/CWM revisions, proposal admissibility, commit
predecessors, exact Human decisions, admission, Governance, Authorization,
Worker lineage, result, Replay, termination, and Certification.

CLIA must present an owner refusal or exact next required Human act. It must
not soften, repair, broaden, or replace a refusal. Transport validation cannot
be cited as semantic or constitutional validation.

## Canonical Data Models

CLIA requires only transport-local architectural roles:

| Role | Contents | Authority | Persistence owner |
|---|---|---|---|
| session binding | channel instance, authenticated actor reference, session/workspace reference, CHE endpoint identity | none | future adapter-local policy only |
| submitted Human act envelope | exact source act, ordering token, explicit opaque references, transport metadata | source transport only | CHE or established source owner after admission |
| CHE response envelope | owner status, exact presentation payload, next required input, opaque correlation references | none in CLIA | established response/evidence owner |
| presentation state | input buffer, display mode, transport status, last acknowledged correlation reference | none | ephemeral by default |

These are conceptual boundary roles. G68-00 creates no schema or canonical
artifact. A later implementation generation must prove whether the existing
CHE signature and owner artifacts are sufficient or whether a versioned
transport-only envelope is necessary. Any such envelope must not duplicate a
Source Turn, Conversation, CWM, proposal, Commitment, Authorization, Replay,
or Certification artifact.

## Deterministic Algorithms

The future CLIA turn algorithm is constrained to:

1. open or restore one transport-local session binding;
2. capture one exact Human act and explicit opaque references;
3. bind a unique transport submission identity to prevent accidental duplicate
   delivery;
4. deliver the act once to Canonical Human Entry;
5. receive one exact CHE response or a transport failure;
6. present the response without semantic reinterpretation; and
7. retain only bounded transport state required for the next delivery.

If delivery outcome is unknown, CLIA must not silently resubmit. It must use an
owner-supported idempotency/correlation check or ask the Human to resolve the
transport state. If CHE rejects a turn, CLIA presents the rejection and stops.
If CHE requests a specific next act, CLIA may render the request but cannot
predict or manufacture the response.

The session lifecycle is transport-only:

~~~text
CREATED -> OPEN -> CLOSED
             |
             +-> TRANSPORT_FAILED_CLOSED
~~~

No CLIA state denotes semantic readiness, proposal acceptance, Commitment,
admission, Authorization, execution success, Replay validity, or
Certification.

## Responsibility Boundaries

| Responsibility | Owner | CLIA relation |
|---|---|---|
| source act and exact authority decision | Human Authority | capture and transport only |
| interactive input/output and local session continuity | CLIA | owns transport mechanics only |
| canonical entry, identity, precedence, continuation handoff | CHE | first constitutional runtime boundary |
| semantic state and clarification | Conversation / G59 | CLIA presents owner output only |
| Natural Conversation proposal | bounded interpreter / G61 under Conversation | no direct CLIA call |
| proposal validation and commit | G59 owners | unreachable directly from CLIA |
| Candidate Review and exact confirmation | Human plus Conversation | exact act transported through CHE |
| Objective Commitment | Human plus G59 | never inferred by CLIA |
| Platform admission and Governance | established Platform/Governance owners | unreachable directly from CLIA |
| execution Authorization | Human plus Authorization owner | distinct exact act transported through CHE |
| Worker and execution | established Worker/execution owners | no CLIA API or routing |
| Replay and Certification | established terminal owners | CLIA may present references, never create them |
| Journey observation | G67 CRO | passive, out-of-band, never called as a runtime owner by CLIA |

## Canonical Human Interaction Architecture

CLIA means **Constitutional Line Interface for AiGOL**. It is the only future
Canonical CLI Human Interaction Channel. Its architectural position is fixed:

~~~text
terminal device
-> CLIA input/output and session transport
-> Canonical Human Entry
-> one established constitutional workflow
~~~

CLIA is not a replacement for CHE. It is not a general `aigol` multiplexer,
an operations console, a Replay browser, a CRO renderer, a provider shell, or
a development runner. Commands exposed by CLIA are limited to transport acts
whose meaning is owned beyond the adapter. A local help command may explain
transport usage; it cannot describe a locally decided workflow state as
constitutional fact.

One CLIA process may carry multiple turns only by preserving exact session and
ordering identity. Multiple terminals may not merge a session through local
heuristics. Reconnection must use an authenticated owner-issued continuation
reference or begin a distinct session.

## CLIA Responsibilities

CLIA SHALL:

- interact with the Human through line-oriented input and output;
- create, open, close, and restore bounded interactive transport sessions;
- collect exact Human acts and explicit attachment/reference selections;
- transport actor, session, workspace, ordering, and correlation information
  required by CHE;
- call only the Canonical Human Entry for production workflow advancement;
- render exact owner responses, required controls, refusals, and terminal
  states accessibly and deterministically; and
- fail closed on transport ambiguity, unknown delivery, malformed response,
  or session mismatch.

CLIA SHALL NEVER contain or exercise:

- workflow, semantic, Proposal, Commitment, Governance, Authorization, Worker,
  execution, Replay, CRO, repository, owner, or routing decisions;
- direct imports or calls to downstream owners for production advancement;
- hidden provider or model invocation;
- local semantic clarification or unrestricted-language parsing;
- local evidence reconstruction, Journey construction, or CRO querying;
- implicit retry that could duplicate a Human act; or
- a compatibility or development subcommand that bypasses CHE.

## CHE Boundary

The inbound boundary is one exact submitted Human act with authenticated
channel, actor, session, workspace, and ordering context plus explicitly
selected opaque references. CLIA may collect those values; CHE owns their
constitutional admission and interpretation. A shell user name, process owner,
terminal presence, or successful local login does not by itself prove Human
Authority to CLIA.

The outbound boundary is one CHE-owned response envelope containing an exact
status and presentation payload, the next permitted/required Human interaction,
and owner correlation references. CLIA displays those fields. It cannot turn a
missing field into a default, a refusal into a retry, a pending state into
success, or a descriptive CRO value into a runtime predecessor.

The boundary admits no direct CLIA edge to Conversation, Proposal Commit,
Platform Admission, Governance, Authorization, Worker, execution, Replay, or
Certification. Even if the implementation language makes those functions
importable, their callability is not a permitted CLIA dependency.

## Legacy Classification

The following is a closed owner-level classification of authenticated public
CLI surfaces and call paths. Each public surface has exactly one G68
classification. A shared helper may participate in different classifications
only through separately authenticated compositions; importability does not
give the helper an independent channel status. The future disposition is
architectural intent only; no status, file, command, or route changes in
G68-00.

| ID | Existing implementation or closed family | G68 classification | Authenticated evidence | Intended future status |
|---|---|---|---|---|
| LC01 | root `./aicli`, default/`submit`, `aigol.cli.aicli.main`, reference UHI session APIs | `Canonical` | G66-15 E01-E04; calls CHE | remain current canonical until atomic CLIA cutover, then `Deprecated` |
| LC02 | `aicli conversation-v2` and `conversation-execute-v2` | `Compatibility` | G66-15 E07-E08; initial CHE bypass | never exposed by CLIA; retain only under explicit compatibility policy, then deprecate separately |
| LC03 | default `aigol next`, `_run_acli_next_runtime_bound_session`, and the persistent conversational wrapper when injected with that CHE-bound turn runner | `Canonical` | G66-15 E06; exact default composition calls CHE | remain current canonical until atomic CLIA cutover, then `Deprecated` |
| LC04 | named `next session`/`interactive` modes and standalone non-CHE composition of ACLI Next conversational helpers | `Compatibility` | G66-15 E09; retained earlier runtime family | explicitly `Deprecated` after CLIA cutover; no production forwarding alias |
| LC05 | named `next readonly-worker`, `execution-plan`, and `dashboard` modes | `Compatibility` | G66-15 E09 | retain only for bounded compatibility evidence until separately retired |
| LC06 | `aigol conversation`, `prompt submit`, `conversational route`, `clarification unknown-domain`, `domain-reference resolve`, `decision-support recommend`, `g4-live-session` | `Historical` | G66-15 E10; HIRR/OCS/PPP/PGSP-era owners | remain non-production historical evidence; later removal requires consumer audit |
| LC07 | direct `aigol` execution, implementation, provider, `run-governed`, dispatch, credential mutation, MOC, ingress, and continuity-preview commands | `Development` | G66-15 E11-E13 | bounded developer/operator tooling only; never CLIA subcommands |
| LC08 | `aigol` status, approval/bridge/plan/dashboard queries, Replay, chain, diagnostics, cognition, return, credential-history/status, and runtime inspection commands | `Internal` | G66-15 E14 and E25; read/reconstruct only | remain separate inspection tooling; no Human workflow advancement |
| LC09 | browser Native Messaging and `scripts/run_minimal_bridge_transport.py` provider-capable path | `Development` | G66-15 E15-E16 | not reusable as production CLIA topology |
| LC10 | `sapianta_bridge` approval, observability, policy, protocol, and reflection CLIs | `Compatibility` | G66-15 E18; separate bridge stack | compatibility/admin only; no CLIA routing |
| LC11 | runtime operator execution CLIs and environment bootstrap | `Development` | G66-15 E26 | explicit operator use only |
| LC12 | runtime audit/certification `__main__` modules and capability review CLIs | `Development` | G66-15 E27 plus G67 focused modules | validation scenarios only |
| LC13 | `runtime.governance.governance_conformance_engine` | `Development` | G66-15 E28 | repository validation only |
| LC14 | root `sapianta` launcher | `Historical` | G66-15 E30; authenticated target absent | intended `Deprecated`, subject to separate consumer/history audit |
| LC15 | root `./cro` and G67-05 CLI composition/transport | `Internal` | G67-04/G67-05; explicit passive evidence query | remain separate passive observability CLI, never CLIA workflow logic |

The shared `aigol/acli_next/conversational.py` implementation currently serves
both LC03's CHE-bound default composition and LC04's retained compatibility
composition. The `acli_next_conversational` implementation family has no
future canonical role and is intended to become `Deprecated` at CLIA cutover.
Its exact Human-facing behavior may inform acceptance tests, but CLIA does not
inherit its local workflow, semantic, persistence, or routing implementation.

The ignored local `sapianta_system/` directory is not authenticated repository
evidence and cannot change LC14. Test functions and injected test adapters are
not CLI implementations; they remain test-only under G66-15 E29. REST, native
GUI, Speech, and Agent-to-Agent entries remain unimplemented at this baseline.

## Natural Conversation Integration

For a CLI Human, unrestricted language follows exactly:

~~~text
Human natural-language act
-> CLIA exact transport
-> Canonical Human Entry
-> Conversation-owned eligibility and current state
-> bounded deterministic or G61 interpreter proposal
-> existing G59 validation and commit owners
~~~

CLIA does not call G61, select a provider, build an interpreter request, parse
the response, commit proposed slots, or decide whether Natural Conversation is
eligible. Exact closed Human controls retain their established precedence at
CHE/Conversation. Natural prose can never substitute for exact Candidate
confirmation, Objective Commitment, execution Authorization, or acceptance.

Natural Conversation is therefore not a second channel. In CLI use it is a
proposal-generation capability downstream of the same CLIA-to-CHE transport.
For any future non-CLI adapter, the exact source act likewise terminates at
CHE before interpretation. G66-19's missing canonical caller and provider
policy remain unimplemented and require separate authorization.

## CRO Integration

The CRO observes owner evidence produced by the canonical lineage; CLIA does
not push runtime state into CRO and CRO does not instrument or direct CLIA.
The observation relation is:

~~~text
CLIA transports Human act to CHE
-> established owners create their own authenticated evidence
-> G67 receives explicit bounded evidence roots and exact selectors
-> owner-local reconstruction and passive Journey correlation
-> immutable query/presentation
~~~

For future CLIA Journey visibility, an established source owner must preserve
the CLIA channel/adapter identity, session identity, exact source-act identity,
CHE correlation, and later owner lineage in its own authenticated evidence.
CLIA must not manufacture Replay or CRO artifacts to satisfy observability.

G67-02 remains the sole Journey/evidence/correlation owner; G67-03 remains the
query owner; G67-04 remains CLI query transport; G67-05 remains passive
composition; and G67-06 remains presentation-only visualization. If a future
CLIA-owned transport artifact requires a new G67 evidence adapter, that adapter
requires a separate authorized generation. Unknown evidence continues to fail
closed. CRO output never becomes a CHE input, owner decision, route,
Authorization, or execution predecessor.

## Future Adapter Architecture

Every future adapter is thin and terminates at the same Canonical Human Entry:

~~~text
CLI / GUI / REST / Browser / Speech / Agent-to-Agent
-> channel-specific transport adapter
-> Canonical Human Entry
-> one constitutional workflow
~~~

| Adapter | Required channel-specific boundary | Prohibited interpretation |
|---|---|---|
| CLIA | line input/output, terminal session, exact controls and references | no local command-to-workflow routing |
| GUI | authenticated interaction/session and exact control rendering | a click is not authority unless CHE binds the exact act |
| REST | authenticated client, actor class, session, idempotency, exact payload | service identity is not automatically Human Authority |
| Browser | authenticated browser/session transport to CHE | existing Native Messaging/provider bridge is not reusable as the production path |
| Speech | audio/transcript provenance and exact audible/visible decision ceremony | transcription or vocal similarity cannot infer confirmation/Authorization |
| Agent-to-Agent | machine identity, non-Human authority profile, exact proposal provenance | an agent cannot impersonate a Human or supply Human-only acts |

CLIA is the sole future **CLI** channel; this does not prohibit separately
authorized non-CLI adapters. All adapters converge at CHE and add no production
spine. Channel-specific authentication, accessibility, privacy, availability,
rate, and transport policies remain adapter responsibilities only where they
do not decide constitutional meaning.

## Migration Strategy

Migration is staged but never dual-canonical:

1. **Architecture only.** G68-00 records this specification and changes no
   reachability.
2. **Bounded implementation.** A separately authorized generation creates a
   new CLIA package/launcher and transport-only tests. While uncertified it is
   a Development surface and cannot receive production traffic.
3. **Certification.** Disposable and authenticated tests prove exact CHE-only
   delegation, multi-turn continuity, duplicate-delivery protection,
   fail-closed transport behavior, exact Human controls, Natural Conversation
   placement, full downstream lineage, and passive CRO reconstruction. Legacy
   behavior may serve as input/output acceptance evidence, not source code or
   architecture authority.
4. **Atomic constitutional cutover.** One separately authorized release marks
   CLIA `Canonical` and simultaneously changes default `./aicli` and default
   `aigol next` to `Deprecated`. There is no interval in which two CLI channels
   are canonical production entry points.
5. **Compatibility containment.** Explicit compatibility, development,
   historical, internal inspection, and CRO CLIs remain outside production.
   CLIA contains no forwarding subcommand to them.
6. **Retirement.** File removal, aliases, package deletion, and migration of
   external consumers require separate authenticated consumer and release
   audits. This specification authorizes none.

The cutover must fail closed if CLIA certification, CHE lineage, Journey
reconstruction, exact Human decision transport, or release evidence is
incomplete. Redirecting old launchers into CLIA would retain multiple public
CLI channel identities and is not the default migration design; any temporary
alias would require explicit non-production status and separate authorization.

## Reuse Impact Assessment

1. Which existing certified capabilities are reused?

   The future CLIA reuses the existing Canonical Human Entry; G66 precedence,
   continuation, and production flow binding; G59 Conversation/CWM, Semantic
   Slots, Proposal Validation, Proposal Commit, Candidate Review, readiness,
   and Objective Commitment; G60 Platform admission and execution integration;
   Governance; distinct Human Authorization; Worker/execution/result owners;
   Replay, termination, and Certification; and passive G67 CRO observation.
   G66-15 authenticates the single-entry/downstream topology, G66-19
   authenticates Natural Conversation placement, and G67 authenticates passive
   Journey observation.

2. Which new capabilities, if any, are introduced?

   This specification introduces one architectural capability definition: the
   future CLIA transport identity and its thin responsibility boundary. It
   introduces no implemented capability, API, schema, executable, owner,
   runtime behavior, or authority. A future implementation will require
   bounded terminal session management, exact CHE transport, deterministic
   response presentation, and certification, all under separate authorization.

3. Does any existing certified capability become unreachable?

   No. The only repository mutation is this document. Default `./aicli`,
   default `aigol next`, compatibility modes, internal APIs, development
   tooling, historical evidence, and CRO remain exactly as reachable as at
   G67-06. A future cutover must preserve every certified downstream owner and
   separately audit any legacy retirement.

4. Does the implementation create a parallel production path?

   No. G68-00 implements no runtime path. The specified future CLIA has exactly
   one successor, Canonical Human Entry, and the migration forbids a
   dual-canonical interval. Compatibility and development surfaces remain
   explicitly outside production.

5. Does the implementation decrease or increase the number of production paths?

   Neither in this generation: the production path count is unchanged because
   documentation alone changes no reachability. At the future atomic cutover,
   CLIA replaces the current CLI channel identities while preserving one
   canonical production lineage; it does not add a production path.

# 3. Constitutional Self-Assessment

## Verified

- The report contains exactly the six G48 top-level sections in the required
  order and all mandatory G48 Code Evidence responsibilities.
- The architecture defines CLIA as the sole future Canonical CLI Human
  Interaction Channel and CHE as its only production successor.
- The complete constitutional flow from Human through Certification is stated
  in exact owner order.
- CLIA is restricted to Human interaction, interactive session management,
  transport, CHE delegation, and response presentation.
- Workflow, semantic, Proposal, Commitment, Governance, Authorization, Worker,
  execution, Replay, CRO, repository, owner, and routing logic are excluded.
- Current `./aicli`, `aigol next`, `acli_next_conversational`, compatibility,
  historical, development, internal inspection, bridge, `sapianta`, and CRO
  CLI families have an authenticated present classification and intended
  future disposition.
- Natural Conversation is placed downstream of CHE under Conversation's
  proposal boundary and cannot become another channel.
- CRO observation is passive, owner-evidence-based, and unable to become a
  runtime predecessor.
- GUI, REST, Browser, Speech, and Agent-to-Agent adapters terminate at the same
  CHE and preserve channel-specific authority distinctions.
- Migration uses an atomic cutover and does not authorize a parallel canonical
  production interval.
- The five exact Reuse Impact Assessment questions are answered from
  authenticated G66/G67 evidence.
- No runtime, code, CLI, adapter, CRO, schema, owner, or production path changed.

## Not Verified

- CLIA is not implemented, invoked, or production-certified; G68-00 explicitly
  authorizes specification only.
- No CLIA executable name, package layout, public signature, transport schema,
  authentication mechanism, session persistence policy, or release manifest is
  selected.
- No end-to-end CLIA turn, continuation, Natural Conversation sequence, exact
  Human confirmation, Objective Commitment, Authorization, Worker execution,
  Replay, Certification, or CRO Journey was executed.
- No current CLI was deprecated, rerouted, removed, or made unreachable.
- No GUI, REST, Browser, Speech, or Agent-to-Agent adapter was implemented or
  validated.
- External consumers of current launchers and compatibility modes were not
  audited; retirement remains separately gated.

# 4. Validation Matrix

| Requirement | Evidence | Validation | Result |
|---|---|---|---|
| G48 structure | six exact top-level sections and seven mandatory Code Evidence subsections | deterministic heading review | `PASS` |
| authenticated baseline | Git commit/tree/subject/parent and clean initial worktree | exact Git inspection | `PASS` |
| Architectural Motivation | G66-15 entry audit, G66-19 Natural Conversation audit, G67 reports | cross-reference consistency review | `PASS` |
| Current Human Interaction Landscape | G66-15 E01-E34 plus G67-05 `cro` | caller/classification correlation | `PASS` |
| one canonical flow | Human -> CLIA -> CHE -> Conversation -> Certification | ordered-stage deterministic review | `PASS` |
| thin CLIA boundary | responsibilities and explicit never-list | architecture responsibility review | `PASS` |
| CHE Boundary | exact inbound/outbound and forbidden-edge rules | boundary consistency review | `PASS` |
| Legacy Classification | LC01-LC15, one permitted class per family | closed-matrix review against G66-15 and G67 | `PASS` |
| `./aicli` future status | present Canonical; Deprecated only at atomic cutover | classification/migration correlation | `PASS` |
| `acli_next_conversational` future status | Compatibility; future Deprecated | classification/migration correlation | `PASS` |
| additional CLI transports | `aigol`, bridge, operator, validation, `sapianta`, and `cro` families | authenticated inventory review | `PASS` |
| Natural Conversation integration | G66-19 proposal placement after CHE | topology consistency review | `PASS` |
| CRO integration | G67 passive evidence/query/composition boundaries | passivity consistency review | `PASS` |
| future adapters | GUI, REST, Browser, Speech, A2A converge on CHE | adapter boundary review | `PASS` |
| migration strategy | development -> certification -> atomic cutover -> retirement audit | no-parallel-path review | `PASS` |
| Reuse Impact Assessment | five exact required questions | deterministic question review | `PASS` |
| implementation non-authorization | repository diff contains only this specification | exact diff review | `PASS` |
| governance regression | `tests/test_governance_conformance.py` | focused pytest: 5 passed | `PASS` |
| governance conformance | read-only conformance engine | 20 passed, 0 failed, 0 warnings, 0 critical violations, `CONFORMANT` | `PASS` |
| document consistency | terms, classifications, future status, restrictions, and one verdict | deterministic content review | `PASS` |
| whitespace integrity | tracked diff plus added specification | `git diff --check`; no-index added-file check | `PASS` |

# 5. Repository Mutation Summary

Modified files:

- `docs/governance/G68_00_CANONICAL_CLIA_ARCHITECTURE_SPECIFICATION_V1.md`
  — added the bounded CLIA architecture specification.

Unchanged subsystems:

- all production and compatibility CLI implementations;
- Canonical Human Entry and every Conversation/execution owner;
- Natural Conversation/G61 proposal assistance;
- CRO core, query, transport, composition, visualization, and launcher;
- all runtime evidence, Replay, Governance, provider, Worker, repository,
  policy, schema, baseline, PCBV31, deployment, and tests.

API compatibility:

- No API, executable, parser, mode, import, schema, default, or return behavior
  changed. CLIA names in this report are specification roles only.

Boundary preservation:

- Present production reachability is unchanged. The future architecture has
  one CLIA-to-CHE edge, reuses the existing owner spine, retains passive CRO,
  and forbids a parallel CLI production route.

Unrelated pre-existing changes:

- None observed. The worktree was clean before this specification was added.

# 6. Certification Verdict

CANONICAL_CLIA_ARCHITECTURE_SPECIFICATION_ESTABLISHED
