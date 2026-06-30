# G4-08 PGSP Canonical Protocol And Session Specialization V1

Status: PGSP CANONICAL PROTOCOL FORMALIZED

Final verdict: PGSP_CANONICAL_READY

## 1. Objective

This artifact defines `PGSP`, Platform Governed Session Protocol, as the
canonical Platform Core session protocol and establishes the specialization
model used by Platform Core.

This is protocol formalization and naming alignment only. It does not introduce
new runtime behavior, redesign G4-02, redesign G4-04, redesign G4-05, invoke
providers, execute workers, create approvals, create authorization, deploy
software, mutate repositories, or change replay reconstruction semantics.

## 2. Canonical PGSP Architecture

PGSP is the interface-neutral Platform Core session protocol between interface
adapters and canonical Platform Services.

Canonical architecture:

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
-> Execution Intent
```

PGSP receives adapter-captured interaction, binds it to a governed session,
routes it through canonical Platform Services, preserves replay and governance
evidence, and returns bounded advisory or execution-intent state.

PGSP is not a new translation layer, communication layer, provider layer,
worker layer, governance engine, replay engine, product layer, or interface
adapter.

## 3. PGSP Responsibilities

PGSP owns:

- neutral governed session identity;
- session lifecycle state and evidence envelope;
- adapter-to-Platform-Core invocation boundary;
- specialization selection and declaration;
- canonical service sequence binding;
- response lineage continuity;
- replay-visible session summary;
- explicit non-authority flags for provider, worker, approval, authorization,
  mutation, and deployment boundaries.

PGSP does not own:

- semantic translation;
- canonical semantic representation;
- OCS proposal semantics;
- reusable human communication;
- interface rendering;
- provider execution;
- worker execution;
- approval creation;
- authorization creation;
- repository mutation;
- deployment;
- replay mutation.

## 4. Session Lifecycle

The canonical PGSP lifecycle is:

| Stage | Description | Canonical owner |
| --- | --- | --- |
| Session intake | Adapter submits raw human interaction and adapter metadata. | Interface Adapter / PGSP boundary |
| Session creation | PGSP creates neutral session identity and specialization declaration. | PGSP |
| Semantic translation | Human request is translated into Platform Core meaning. | UBTR |
| Structured intent | Translation is represented as a deterministic canonical semantic artifact. | CSA |
| Orchestration / proposal | Governed proposal, alternatives, risks, and advisory intent are prepared. | OCS |
| Governance checkpoint | Policy, approval, authorization, provider, worker, mutation, deployment, and replay boundaries are evaluated. | Governance |
| Human communication | Explanation, confirmation, guidance, transparency, risks, and recovery sections are produced. | UHCL |
| Adapter rendering | The interface renders UHCL output in modality-specific form. | Interface Adapter |
| Human response capture | The interface captures human response and maps it to canonical response classes. | Interface Adapter / UHCL response model |
| Replay binding | Session evidence, service evidence, response evidence, and hashes are reconstructable. | Replay |
| Execution intent | Advisory or governed execution intent is recorded with required gates. | OCS / Governance |

## 5. Specialization Hierarchy

PGSP is the root protocol. Specializations are scoped session categories that
declare the domain or workflow purpose while preserving the same Platform Core
ownership model.

```text
PGSP
├── LGDS: Live Governed Development Session
├── PGPS: Product Governed Platform Session
├── GRRS: Governance / Replay Review Session
├── DGMS: Diagnostic Governed Maintenance Session
├── BGWS: Business Governed Workflow Session
├── MGWS: Medical Governed Workflow Session
├── EGWS: Energy Governed Workflow Session
└── AGOS: Administrative Governed Operations Session
```

Specialization names are descriptive categories, not independent protocols.
They must not create duplicate translators, communication systems, replay
systems, governance systems, provider paths, worker paths, approval paths,
authorization paths, or mutation paths.

## 6. LGDS Specialization

LGDS means Live Governed Development Session.

LGDS is the first certified PGSP specialization. It covers governed
natural-language AiGOL development sessions, including the Generation 4 goal of
replacing ChatGPT/Codex copy-paste development workflow with governed
Platform-Core-mediated sessions.

Current implementation lineage:

- G4-02 provides the governed development loop execution scaffold.
- G4-04 provides the first executable governed self-development session.
- G4-05 provides the first live ACLI entrypoint into that session path.
- G4-06 verified reuse and rejected a new LGDS runtime.
- G4-07 established PGSP as the broader canonical name and LGDS as a
  specialization.

LGDS should remain a PGSP specialization, not the universal protocol name.

## 7. Future Session Categories

Future PGSP specializations may include:

| Category | Purpose | Boundary requirement |
| --- | --- | --- |
| Product sessions | Product workflows such as Product 1 AI Decision Validator. | Product remains consumer, not Platform Core owner. |
| Business sessions | Business process review, proposal, planning, and governed handoff. | Business domain does not own UBTR, UHCL, replay, or governance. |
| Medical sessions | Medical workflow support and evidence review. | Must preserve high-stakes governance and limitation visibility. |
| Energy sessions | Energy workflow support and operational evidence review. | Must preserve domain-specific policy and replay evidence. |
| Administration sessions | Controlled administrative requests and audit-bound operations. | Must preserve authorization and mutation boundaries. |
| Diagnostics sessions | Runtime diagnostics, failure analysis, and recovery guidance. | Diagnostics must not self-authorize repair or mutation. |
| Replay review sessions | Replay inspection, lineage review, and evidence continuity review. | Replay remains evidence-only. |
| Governance review sessions | Governance conformance and policy review. | Governance remains authority owner; communication cannot approve. |

## 8. Adapter Invocation Model

Interface adapters invoke PGSP. They do not implement PGSP.

Adapter responsibilities:

- capture raw input;
- provide adapter identity and modality metadata;
- render UHCL output in the target modality;
- capture human response;
- map response input to canonical UHCL response classes where applicable;
- preserve local session interaction evidence.

Adapters must not:

- translate semantics;
- generate reusable explanations or confirmations;
- own OCS proposal logic;
- own governance checks;
- own replay reconstruction;
- invoke providers as an adapter capability;
- execute workers as an adapter capability;
- approve, authorize, mutate, or deploy.

ACLI is the first adapter. Web, REST, Voice, Mobile, and future adapters should
call PGSP through their own adapter-specific capture and render surfaces.

## 9. Platform Service Integration

PGSP integrates Platform Services by invoking or binding to their canonical
contracts:

| Platform Service | PGSP integration role |
| --- | --- |
| UBTR | Provides semantic translation and UHCL communication model semantics. |
| CSA | Provides canonical structured intent representation and semantic hashes. |
| OCS | Provides orchestration, proposal, alternatives, risk, and advisory execution-intent preparation. |
| Governance | Provides checkpoints, policy, fail-closed behavior, approval and authorization separation, and authority boundaries. |
| UHCL | Provides reusable human communication, confirmation model, recovery guidance, transparency, and summaries. |
| Replay | Provides deterministic reconstruction, ordering, lineage, and evidence continuity. |
| Provider Services | Provide reusable cognition capabilities only through governed OCS/provider boundaries. |
| Worker Services | Provide reusable execution lifecycle capabilities only through governed worker boundaries. |
| Product Services | Consume PGSP/Platform Core evidence without owning Platform Core capabilities. |

PGSP composes these services. It does not absorb them.

## 10. Replay Model

PGSP replay must record:

- session identity;
- specialization identity;
- adapter capture evidence;
- UBTR translation hash/reference;
- CSA artifact hash/reference;
- OCS proposal hash/reference;
- governance checkpoint hash/reference;
- UHCL communication and confirmation hash/reference;
- adapter render and human response evidence;
- advisory or governed execution-intent hash/reference;
- explicit no-authority flags;
- deterministic reconstruction hash.

Existing G4-02, G4-04, and G4-05 replay models already provide the first
implementation lineage. Future PGSP facade artifacts should be additive and
must not rewrite existing replay artifacts or invalidate existing hashes.

## 11. Governance Model

PGSP governance must preserve:

- fail-closed semantics;
- approval boundary;
- authorization boundary;
- provider boundary;
- worker boundary;
- mutation boundary;
- deployment boundary;
- replay boundary;
- interface adapter boundary;
- product consumer boundary;
- limitation visibility.

PGSP session completion does not imply execution approval. Human confirmation
does not imply authorization. UHCL communication does not grant authority.
Adapter rendering does not create governance evidence beyond presentation and
response capture.

## 12. Ownership Matrix

| Layer | Owner | PGSP relationship |
| --- | --- | --- |
| Human | Human authority | Originates request and supplies response. |
| Interface Adapter | ACLI / Web / REST / Voice / Mobile / future adapters | Captures and renders; invokes PGSP. |
| PGSP | Platform Core session protocol | Owns neutral session envelope and specialization binding. |
| UBTR | Platform Core semantic layer | Owns translation and communication model semantics. |
| CSA | Platform Core semantic artifact layer | Owns structured intent. |
| OCS | Platform Core orchestration layer | Owns proposal and advisory execution-intent preparation. |
| Governance | Platform Core governance layer | Owns checkpoints, policy, approval and authorization boundaries. |
| UHCL | Platform Core human communication layer | Owns reusable explanations, confirmations, guidance, transparency, and recovery. |
| Replay | Platform Core evidence layer | Owns deterministic reconstruction and evidence continuity. |
| Provider Services | Platform Services | Provide governed cognition services when separately allowed. |
| Worker Services | Platform Services | Provide governed execution services when separately allowed. |
| Products | Platform consumers | Consume evidence and session outputs without owning Platform Core. |

## 13. Naming Conventions

Canonical naming:

- `PGSP`: Platform Governed Session Protocol.
- `PGSP session`: neutral governed Platform Core session.
- `PGSP specialization`: domain/workflow category using PGSP.
- `LGDS`: Live Governed Development Session, a PGSP specialization.
- `PGSP adapter entrypoint`: interface-specific entrypoint into PGSP.
- `PGSP facade`: additive neutral facade over existing G4-04/G4-02 behavior.

Naming constraints:

- existing G4 artifact names remain valid for lineage;
- PGSP names should be additive;
- LGDS names should remain development-specific;
- adapter names should include adapter identity, such as ACLI;
- specialization names must not imply independent Platform Service ownership.

## 14. Compatibility Strategy

Compatibility is preserved by:

- keeping G4-02 scaffold behavior unchanged;
- keeping G4-04 session behavior unchanged;
- keeping G4-05 ACLI entrypoint behavior unchanged;
- treating PGSP as a canonical facade and documentation layer before any
  runtime alias is added;
- adding facade artifacts only in future implementation batches;
- preserving old names as historical lineage;
- avoiding replay rewrites;
- avoiding behavioral migration before targeted facade tests exist.

## 15. Migration Recommendations

Recommended migration path:

1. Keep all current G4-02, G4-04, and G4-05 runtimes unchanged.
2. Add a future PGSP facade that delegates to the existing G4-04 runtime.
3. Add specialization metadata identifying LGDS as the development
   specialization.
4. Add adapter-specific entrypoint aliases only after the facade is documented
   and tested.
5. Add future adapter integrations through PGSP rather than copying G4-05.
6. Add future product/domain specializations as PGSP categories, not new
   protocols.

No migration should rename existing replay artifacts in place.

## 16. Recommended Implementation Batch

Recommended next implementation batch:

`G4_09_PGSP_CANONICAL_FACADE_RUNTIME_ALIAS_V1`

Scope:

- implement an additive PGSP facade over the existing G4-04 runtime;
- represent LGDS as specialization metadata;
- preserve G4-04 and G4-05 behavior;
- add targeted tests proving the facade delegates without enabling provider,
  worker, approval, authorization, mutation, deployment, or replay mutation
  paths;
- run `git diff --check` and targeted facade tests.

Non-scope:

- no new PGSP engine;
- no new translator;
- no new CSA builder;
- no new OCS proposal runtime;
- no new UHCL communication runtime;
- no new replay engine;
- no provider execution;
- no worker execution;
- no approval creation;
- no authorization creation;
- no repository mutation;
- no deployment.

## 17. Final Determination

PGSP is the canonical Platform Core session protocol.

LGDS is the first development-focused PGSP specialization, implemented through
the existing G4-02, G4-04, and G4-05 lineage.

Platform Services remain unchanged. Interface adapters invoke PGSP. Future
specializations should extend the PGSP naming and metadata model without
duplicating Platform Core services or creating new protocols.

Final verdict: PGSP_CANONICAL_READY
