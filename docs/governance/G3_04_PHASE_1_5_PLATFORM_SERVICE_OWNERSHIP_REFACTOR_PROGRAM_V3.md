# G3-04 Phase 1.5 Platform Service Ownership Refactor Program V3

Status: Generation 3 architectural refactor program.

Scope: canonical Platform Services ownership model before continuing G3-04 provider
activation and G3-05 worker expansion.

This artifact does not modify runtime code, modify tests, invoke providers, invoke workers,
authorize execution, mutate repositories, deploy software, or redefine constitutional
authority.

## 1. Purpose

Platform Core Generation 2 is certified.

Generation 2 established the canonical semantic architecture:

```text
Human Intent
      |
      v
    UBTR
      |
      v
     CSA
      |
      v
     OCS
```

Generation 3 has certified:

- G3-02 ACLI Primary Development Interface;
- G3-03 Product 1, AI Decision Validator;
- G3-04 Phase 1 Provider Identity and Credential Boundaries.

The Generation 3 Responsibility Placement Audit concluded:

```text
GENERATION_3_RESPONSIBILITY_RESTRUCTURING_REQUIRED
```

This program formalizes the permanent Platform Services architecture so remaining
Generation 3 work implements reusable capabilities once inside Platform Core, while ACLI,
Web, Mobile, REST, Voice, and future adapters consume those capabilities.

## 2. Permanent Architectural Invariants

### Invariant 1: Canonical Semantic Entry

UBTR is the single canonical semantic entry point.

There must never be:

- ACLI semantic interpretation;
- Web semantic interpretation;
- Mobile semantic interpretation;
- REST semantic interpretation;
- Voice semantic interpretation;
- interface-specific semantic routing.

All interfaces consume the same UBTR and CSA lineage.

### Invariant 2: Platform Services

All reusable capabilities exist exactly once.

Platform Services are a permanent Platform Core layer.

Interfaces and products consume Platform Services. They do not implement copies of shared
platform behavior.

### Invariant 3: Interfaces Are Adapters

Interfaces include:

- ACLI;
- Web;
- Mobile;
- REST;
- Voice;
- future interfaces.

Interfaces own:

- user interaction;
- presentation;
- interface-local transport;
- interface-specific UX;
- adapter-local session references.

Interfaces must not own:

- semantic interpretation;
- provider orchestration;
- worker orchestration;
- governance;
- replay;
- shared policies;
- shared conversation logic;
- shared rendering models;
- shared platform capabilities.

### Invariant 4: Products Are Consumers

Product 1 and future products consume Platform Services.

Products may own product-specific workflow and evidence artifacts.

Products must not become Platform Core owners.

### Invariant 5: Providers Belong To OCS Cognition

Provider capabilities belong to OCS cognitive infrastructure and Provider Services.

Provider Services include:

- Provider Registry;
- Provider Identity;
- Credential References;
- Provider Selection;
- Provider Invocation;
- Escalation;
- Multi-provider Comparison;
- Cost Control;
- Rate-limit Control;
- Failure Handling.

OCS governs:

- whether provider cognition is needed;
- which provider identity is eligible;
- whether multiple providers are used;
- comparison of provider outputs;
- escalation strategy;
- provider failure handling.

Interfaces never implement provider logic.

## 3. Canonical Platform Services Architecture

Target architecture:

```text
Human Interfaces
  ACLI
  Web
  Mobile
  REST
  Voice
  Future Interfaces
        |
        v
==============================
      PLATFORM SERVICES
==============================

Semantic Services
  UBTR
  CSA
  Semantic Models

Cognition Services
  OCS

Provider Services
  Provider Registry
  Provider Identity
  Credential References
  Provider Selection
  Provider Invocation
  Escalation
  Comparison
  Cost Management
  Rate-limit Management
  Failure Handling

Execution Services
  Worker Registry
  Worker Authorization
  Worker Lifecycle
  Worker Orchestration
  Worker Execution

Governance Services
  Replay
  Audit
  Policies
  Certification

Shared Infrastructure
  Shared Conversation Models
  Shared Rendering Models
  Shared View Models
  Shared Evidence
  Shared Session Models

==============================
        |
        v
Products
  Product 1
  Product 2
  Future Products
```

This architecture preserves the project objective:

```text
AiGOL can be developed through ACLI using natural language without ChatGPT/Codex copy-paste.
```

ACLI achieves this as the first interface adapter over Platform Services.

## 4. Responsibility Matrix

| Capability | Platform Services Domain | Interface-Specific? | Product-Specific? | Permanent Owner |
| --- | --- | --- | --- | --- |
| Natural-language semantic entry | Semantic Services | No | No | UBTR |
| Canonical semantic artifact | Semantic Services | No | No | CSA |
| Semantic models | Semantic Services | No | No | Platform Core / UBTR / CSA |
| Cognition orchestration | Cognition Services | No | No | OCS |
| Provider need determination | Cognition Services | No | No | OCS |
| Provider registry | Provider Services | No | No | Provider Layer |
| Provider identity | Provider Services | No | No | Provider Layer |
| Credential references | Provider Services | No | No | Provider Layer |
| Credential secret storage | Provider Services / external vault | No | No | Provider Layer / credential vault |
| Provider selection | Provider Services under OCS | No | No | Provider Layer |
| Provider invocation | Provider Services under OCS | No | No | Provider Layer |
| Provider escalation | Provider Services under OCS | No | No | Provider policy service |
| Multi-provider comparison | Provider Services under OCS | No | No | Provider comparison service |
| Provider cost management | Provider Services | No | No | Provider policy service |
| Provider rate-limit management | Provider Services | No | No | Provider policy service |
| Provider failure handling | Provider Services | No | No | Provider failure service |
| Provider response normalization | Provider Services / OCS | No | No | Provider Layer / OCS |
| Provider status view model | Shared Infrastructure | Adapter renders only | No | Shared view model service |
| Worker registry | Execution Services | No | No | Worker Layer |
| Worker authorization | Execution Services / Governance | No | No | Authorization service |
| Worker lifecycle | Execution Services | No | No | Worker Layer |
| Worker orchestration | Execution Services | No | No | Worker Layer |
| Worker execution | Execution Services | No | No | Worker Layer |
| Worker selection | Execution Services | No | No | Worker policy service |
| Worker replay | Execution Services / Governance | No | No | Worker Layer / Replay |
| Replay | Governance Services | No | No | Replay service |
| Audit | Governance Services | No | Product artifacts may consume | Audit service / product audit artifacts |
| Policies | Governance Services | No | No | Governance policy service |
| Certification | Governance Services | No | Product certification may consume | Certification service |
| Shared session model | Shared Infrastructure | Adapter-local references only | No | Platform Core |
| Shared conversation model | Shared Infrastructure | Adapter-local rendering only | No | Platform Core |
| Shared rendering model | Shared Infrastructure | Adapter renders it | No | Platform Core |
| Shared view model | Shared Infrastructure | Adapter renders it | No | Platform Core |
| Shared evidence model | Shared Infrastructure / Governance | No | Product consumes | Platform Core |
| ACLI prompt capture | N/A | Yes | No | ACLI adapter |
| ACLI terminal rendering | N/A | Yes | No | ACLI adapter |
| ACLI command transport | N/A | Yes | No | ACLI adapter |
| Web rendering | N/A | Yes | No | Web adapter |
| Mobile rendering | N/A | Yes | No | Mobile adapter |
| REST transport | N/A | Yes | No | REST adapter |
| Voice capture/rendering | N/A | Yes | No | Voice adapter |
| Product 1 workflow | Product service | No | Yes | Product 1 |
| Product 1 Decision Packet | Product service | No | Yes | Product 1 |
| Product 1 Audit Packet | Product service / Governance consumer | No | Yes | Product 1 |
| Product 1 Certification | Product service / Certification consumer | No | Yes | Product 1 |

## 5. Ownership Corrections

Required corrections:

| Existing / Planned Placement | Correction |
| --- | --- |
| ACLI provider-assisted interaction model | Move shared interaction state to Provider Services and shared view models |
| ACLI provider rendering | Keep only ACLI-specific rendering; shared provider state belongs to Platform Services |
| ACLI provider fallback handling | Move fallback policy to Provider Services |
| ACLI provider escalation | Move escalation policy to Provider Services under OCS |
| ACLI provider comparison | Move comparison to Provider Services / OCS |
| ACLI confirmation classification | Move reusable classification contract to Shared Infrastructure |
| ACLI proposal / approval bridge ownership | Move reusable proposal and approval contracts to Governance / Platform Services |
| ACLI authorization readiness ownership | Move reusable authorization readiness contract to Execution / Governance Services |
| ACLI worker workflow initiation | Move worker orchestration to Execution Services |
| Product 1 provider advisory usage as invocation | Product 1 consumes OCS/provider advisory evidence only |
| Product 1 worker-assisted validation as orchestration | Product 1 consumes worker evidence only after Execution Services authorize and run |

Completed certifications remain valid. The correction is about future ownership, not
retroactive invalidation.

## 6. Revised Dependency Graph

Original high-level Generation 3 order remains valid:

```text
G3-02 ACLI Interface
  -> G3-03 Product 1
    -> G3-04 Provider Activation
      -> G3-05 Worker Expansion
        -> G3-06 Deployment Readiness
          -> G3-07 Production Certification
```

Corrected G3-04 internal order:

```text
G3-04 Phase 1 Provider Identity And Credential Boundaries
  -> G3-04 Phase 1.5 Platform Service Ownership Refactor
    -> G3-04 Phase 2 Provider Registry And Policy Gates
      -> G3-04 Phase 3 Provider Invocation Substrate
        -> G3-04 Phase 4 OCS Provider Invocation Path
          -> G3-04 Phase 5 Shared Provider View Models
            -> G3-04 Phase 6 ACLI Provider Adapter Rendering
              -> G3-04 Phase 7 Product 1 Provider Advisory Binding
                -> G3-04 Phase 8 Escalation And Multi-provider Comparison
                  -> G3-04 Phase 9 Failure / Fallback / Cost Certification
                    -> G3-04 Provider Activation Certification
```

Corrected G3-05 starting order:

```text
G3-05 Worker Layer Ownership Program
  -> Worker Registry
  -> Worker Authorization Contract
  -> Worker Lifecycle
  -> Worker Orchestration
  -> Worker Execution
  -> Worker Replay
  -> Worker Selection
  -> Shared Worker View Models
  -> ACLI Worker Adapter Rendering
  -> Product 1 Worker Evidence Consumption
  -> Worker Expansion Certification
```

## 7. Platform Services Implementation Roadmap

Platform Services implementation sequence:

| Step | Objective | Blocks |
| --- | --- | --- |
| PS-01 | Define shared service ownership contracts | All remaining G3-04/G3-05 |
| PS-02 | Define shared evidence and replay ownership model | Provider invocation, worker execution |
| PS-03 | Define shared session/conversation/view-model contracts | ACLI/Web/Mobile/REST/Voice parity |
| PS-04 | Map legacy provider/vault artifacts into G3-04 provider identity substrate | Provider activation |
| PS-05 | Define provider service APIs and artifacts | G3-04 Phase 2+ |
| PS-06 | Define worker service APIs and artifacts | G3-05 |
| PS-07 | Define interface adapter conformance rules | Web/Mobile/REST/Voice future work |
| PS-08 | Define Product consumer conformance rules | Product 2 and future products |

## 8. Semantic Services Roadmap

Semantic Services owner:

```text
UBTR / CSA
```

Roadmap:

1. Preserve UBTR as the single semantic entry point.
2. Preserve CSA as canonical semantic representation.
3. Prohibit interface-specific semantic routing.
4. Provide shared semantic service contracts for all future interfaces.
5. Require every interface prompt or command boundary fallback to reference UBTR/CSA.
6. Keep semantic replay lineage independent of interface adapter.

Certification criteria:

- no ACLI/Web/Mobile/REST/Voice semantic interpretation;
- CSA reference/hash present for semantic workflows;
- semantic fallback status replay-visible;
- UBTR remains canonical semantic authority.

## 9. Cognition Services Roadmap

Cognition Services owner:

```text
OCS
```

Roadmap:

1. Preserve OCS as cognition orchestration authority.
2. Route provider cognition requests through OCS.
3. Bind OCS cognition to CSA reference/hash.
4. Normalize provider output into advisory OCS artifacts.
5. Prevent provider output from becoming governance, approval, semantic, or execution authority.
6. Provide OCS advisory artifacts consumable by ACLI, Product 1, and future adapters.

Certification criteria:

- OCS decides if provider cognition is needed;
- OCS records provider cognition lineage;
- OCS output remains advisory;
- interface adapters render OCS evidence without owning cognition.

## 10. Provider Services Roadmap

Provider Services owner:

```text
Provider Layer under OCS governance
```

Roadmap:

1. Keep G3-04 Phase 1 provider identity and credential boundaries as the canonical identity
   substrate.
2. Implement provider registry service.
3. Implement credential-reference lifecycle service.
4. Implement provider policy gates for scope, cost, rate-limit, and human approval.
5. Implement provider invocation substrate.
6. Implement provider response normalization.
7. Implement provider failure and fallback handling.
8. Implement escalation policy.
9. Implement multi-provider comparison.
10. Implement shared provider view models.
11. Implement ACLI provider adapter rendering.
12. Implement Product 1 provider advisory binding.

Provider Services must never:

- store credential secrets in replay;
- select providers inside ACLI;
- invoke providers inside Product 1;
- authorize execution;
- invoke workers;
- mutate repositories;
- bypass OCS or governance.

## 11. Execution Services Roadmap

Execution Services owner:

```text
Worker Layer
```

Roadmap:

1. Create G3-05 Worker Layer ownership program.
2. Implement worker registry service.
3. Implement worker authorization contract.
4. Implement worker lifecycle service.
5. Implement worker orchestration service.
6. Implement worker execution service.
7. Implement worker replay service.
8. Implement worker selection policy.
9. Implement worker failure/fallback handling.
10. Implement shared worker view models.
11. Implement ACLI worker adapter rendering.
12. Implement Product 1 worker evidence consumption.

Execution Services must never:

- let ACLI execute workers directly;
- let Product 1 execute workers directly;
- let providers execute workers;
- bypass approval and authorization;
- bypass replay;
- mutate governance.

## 12. Governance Services Roadmap

Governance Services owner:

```text
Replay / Audit / Policies / Certification
```

Roadmap:

1. Preserve replay as platform-owned.
2. Preserve audit evidence as platform-governed.
3. Define policy gates for provider and worker services.
4. Define certification evidence for every service boundary.
5. Add interface-adapter portability checkpoint.
6. Add Product consumer conformance checkpoint.
7. Add provider and worker authority-denial checkpoints.

New certification checkpoints:

| Checkpoint | Meaning |
| --- | --- |
| `PLATFORM_SERVICE_OWNERSHIP_PRESERVED` | Reusable capability is owned by Platform Services |
| `INTERFACE_ADAPTER_PORTABILITY_PRESERVED` | Capability can be consumed by ACLI, Web, Mobile, REST, Voice, and future adapters |
| `PRODUCT_CONSUMER_BOUNDARY_PRESERVED` | Product consumes platform service without owning it |
| `PROVIDER_ADVISORY_BOUNDARY_PRESERVED` | Provider output remains advisory |
| `WORKER_EXECUTION_BOUNDARY_PRESERVED` | Worker execution remains approval/authorization-bound |

## 13. Shared Infrastructure Roadmap

Shared Infrastructure owner:

```text
Platform Core
```

Roadmap:

1. Shared session model.
2. Shared conversation model.
3. Shared confirmation classification contract.
4. Shared proposal view model.
5. Shared approval view model.
6. Shared authorization readiness view model.
7. Shared provider view model.
8. Shared worker view model.
9. Shared rendering model.
10. Shared evidence model.

Shared Infrastructure must provide interface-neutral artifacts. Interfaces may render them
differently, but must not redefine their meaning.

## 14. ACLI Adapter Model

ACLI owns:

- terminal input;
- command entry;
- operator-facing terminal rendering;
- local ACLI transport;
- ACLI-specific UX;
- ACLI adapter references to shared platform sessions.

ACLI consumes:

- UBTR/CSA semantic services;
- OCS cognition services;
- Provider Services;
- Worker Services;
- Governance Services;
- Shared Infrastructure;
- Product services.

ACLI must not own:

- semantics;
- provider logic;
- worker logic;
- governance logic;
- replay logic;
- shared conversation logic;
- shared rendering model;
- Product 1 logic.

ACLI remains the first and primary development interface because it exposes the complete
Platform Services stack to the human operator through natural language.

## 15. Product Consumer Model

Product 1 owns:

- AI Decision Validator workflow;
- Product 1 Decision Packet;
- Product 1 Audit Packet;
- Product 1 certification evidence;
- Product-specific product lifecycle.

Product 1 consumes:

- UBTR/CSA semantic evidence;
- OCS advisory evidence;
- Provider Services advisory evidence;
- Worker Services execution evidence where later approved;
- Governance Services;
- Shared Infrastructure view/evidence models.

Product 1 must not own:

- provider invocation;
- provider selection;
- worker orchestration;
- worker execution;
- replay service;
- governance service;
- interface rendering;
- shared platform policies.

Future products follow the same model.

## 16. Web / Mobile / REST / Voice Adapter Model

Future adapters own only adapter-specific interaction and transport:

| Adapter | Owns | Consumes |
| --- | --- | --- |
| Web | browser UX, web transport, web rendering | Platform Services |
| Mobile | mobile UX, mobile transport, mobile rendering | Platform Services |
| REST | API transport, request/response formatting | Platform Services |
| Voice | speech capture/rendering, voice UX | Platform Services |
| Future | adapter-specific UX/transport | Platform Services |

Adapters must pass the same service conformance tests where applicable.

No future adapter may introduce separate semantic routing, provider orchestration, worker
orchestration, governance, replay, or Product ownership.

## 17. Migration Impact

Completed work impact:

| Completed Work | Impact |
| --- | --- |
| G3-02 ACLI certification | Remains valid as first adapter certification |
| G3-03 Product 1 certification | Remains valid as product consumer certification |
| G3-04 Phase 1 provider identity | Remains valid as Provider Services identity substrate |

Future work impact:

| Future Work | Required Change |
| --- | --- |
| G3-04 Provider Registry | Implement as Provider Services |
| G3-04 Provider Invocation | Implement as Provider Services under OCS |
| G3-04 ACLI Provider Rendering | Implement after shared provider view model |
| G3-04 Product 1 Provider Binding | Consume OCS/provider advisory evidence only |
| G3-05 Worker Expansion | Start with Worker Layer ownership program |
| Future Web/Mobile/REST/Voice | Consume Platform Services through adapter contracts |

No completed runtime needs rollback.

## 18. Certification Impact

Certification impact:

- G3-02 remains certified.
- G3-03 remains certified.
- G3-04 Phase 1 remains certified as the provider identity boundary layer.
- G3-04 must not continue to provider invocation until Platform Services ownership is
  accepted.
- G3-05 must not begin worker execution until Worker Layer ownership is specified.
- Generation 3 final certification must prove Platform Services ownership and adapter
  portability.

G3-04 Phase 1.5 certification criteria:

- canonical Platform Services architecture documented;
- every remaining G3-04/G3-05 capability assigned to a Platform Services domain or adapter;
- ACLI adapter boundary documented;
- Product consumer boundary documented;
- future adapter model documented;
- corrected dependency graph documented;
- validation passes.

## 19. Rollback Impact

Rollback impact is low.

This is a governance refactor program only:

- no runtime code changes;
- no test changes;
- no provider activation;
- no worker activation;
- no credential mutation;
- no deployment.

Rollback would remove this document and return the roadmap to the previous audit state.

Because the audit already found restructuring required, rollback is not recommended unless a
replacement ownership program is created.

## 20. Next Implementation Batch

Next batch:

```text
G3_04_PHASE_2_PROVIDER_REGISTRY_AND_POLICY_GATES_V1
```

Required scope:

- Provider Services registry artifact;
- provider identity compatibility with G3-04 Phase 1;
- credential-reference lifecycle consumption;
- provider scope policy gates;
- cost/rate-limit policy gates;
- approval-required policy gates;
- replay-visible registry and policy evidence;
- no provider invocation.

This batch must implement Provider Services, not ACLI behavior.

## 21. Final Verdict

```text
G3_04_PHASE_1_5_PLATFORM_SERVICE_OWNERSHIP_REFACTOR_PROGRAM_READY
```
