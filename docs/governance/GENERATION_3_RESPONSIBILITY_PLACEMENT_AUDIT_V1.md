# Generation 3 Responsibility Placement Audit V1

Status: architectural responsibility audit.

Scope: Generation 3 workstream ownership review after G3-04 Phase 1.

This artifact does not modify runtime code, modify tests, invoke providers, invoke workers,
authorize execution, mutate repositories, or change constitutional authority.

## 1. Executive Summary

Platform Core Generation 2 is certified.

G3-02 certified ACLI as the first human-first development interface.

G3-03 certified Product 1, AI Decision Validator, in deterministic, replay-visible,
non-executing scope.

G3-04 Phase 1 established provider identity and credential-reference boundaries.

The audit confirms the core architectural concern:

```text
ACLI must remain the first human interface to AiGOL, not the owner of reusable platform capabilities.
```

The certified artifacts generally preserve this boundary. However, the Generation 3 roadmap
and G3-04 program language still assign some reusable capabilities to ACLI by name. These
capabilities should be implemented as shared Platform Core services and exposed through ACLI,
Web, Mobile, REST, Voice, and future interface adapters.

Generation 3 should continue, but the roadmap requires restructuring before deeper G3-04 and
G3-05 implementation.

## 2. Source Of Truth

This audit uses the certified Platform Core architecture and Generation 3 artifacts as source
material:

- Platform Core Generation 2 certification baseline;
- G3-02 ACLI Primary Development Interface certification;
- G3-03 Product 1 certification;
- G3-04 Real Provider Activation Program;
- G3-04 Phase 1 Provider Identity and Credential Boundaries;
- Generation 3 Master Execution Program.

Canonical long-term architecture:

```text
Human Interfaces
  - ACLI
  - Web
  - Mobile
  - REST API
  - Voice
  - Future adapters
    |
    v
UBTR
    |
    v
CSA
    |
    v
OCS
    |
    v
Provider Layer
    |
    v
Worker Layer
    |
    v
Replay
    |
    v
Platform Services
```

Interface rule:

```text
Interfaces render, collect input, and initiate governed platform workflows.
Interfaces do not own shared platform semantics, provider governance, worker execution,
approval authority, replay authority, or Product authority.
```

## 3. Responsibility Matrix

| Capability | Permanent Owner | Consumers / Adapters | Current Placement Assessment | Correction |
| --- | --- | --- | --- | --- |
| Natural-language semantic interpretation | UBTR | ACLI, Web, Mobile, REST, Voice, Product 1 | Correct after G2 | None |
| Canonical semantic representation | CSA | OCS, Product 1, Replay, interfaces | Correct after G2 | None |
| Cognition orchestration | OCS | Product 1, ACLI, future interfaces | Correct if provider invocation remains OCS-mediated | Keep provider invocation path under OCS / Provider Layer |
| Provider identity | Provider Layer / Platform Core | OCS, Product 1, ACLI, future interfaces | Correct in G3-04 Phase 1 | None |
| Provider registry | Provider Layer / Platform Core | OCS, Product 1, interfaces | Not yet implemented | Implement as shared platform registry |
| Credential references and lifecycle | Provider Layer / Platform Core | Provider policy gates, OCS | Correct in Phase 1 as reference-only | Extend as platform service, not ACLI |
| Provider activation policy | Provider Layer / Governance service | OCS, interfaces | Planned, not implemented | Implement as shared provider policy gate |
| Provider invocation | Provider Layer, orchestrated by OCS | ACLI, Product 1, future interfaces | G3-04 wording risks ACLI ownership | Implement as platform invocation substrate |
| Provider comparison | Provider Layer / OCS | Product 1, ACLI, future interfaces | Planned, ownership should be shared | Implement comparison substrate in Platform Core |
| Provider escalation | Provider Layer policy service | OCS, Product 1, interfaces | Planned, ownership should be shared | Implement deterministic escalation policy service |
| Provider rendering | Interface adapter rendering over platform view model | ACLI, Web, Mobile, REST, Voice | G3-04 says ACLI provider rendering | Split shared provider status view model from ACLI rendering |
| Product 1 provider usage | Product 1 consumes provider advisory evidence through OCS | Product 1 UI surfaces | Correct if Product 1 remains consumer | Keep Product 1 as consumer only |
| Worker registry | Worker Layer / Platform Core | OCS, Product 1, interfaces | Planned, not implemented | Implement as shared worker registry |
| Worker lifecycle | Worker Layer / Platform Core | ACLI, Web, Mobile, REST, Voice | Planned, not implemented | Implement as platform lifecycle service |
| Worker orchestration | Worker Layer, gated by approval/authorization | OCS, Product 1, interfaces | Planned, not implemented | Implement as shared orchestration service |
| Worker authorization | Approval / Authorization service | Worker Layer, interfaces | Existing G3-02 bridge evidence, future shared use required | Promote reusable authorization artifacts into platform service if not already shared |
| Worker execution | Worker Layer | Interfaces only initiate approved workflows | Planned | Keep outside ACLI and Product 1 |
| Worker replay | Replay service | Worker Layer, Product 1, interfaces | Planned | Implement in shared Replay / Worker Layer |
| Worker selection | Worker Layer policy service | OCS, interfaces | Planned | Implement as shared policy service |
| ACLI session lifecycle | ACLI adapter evidence plus shared session concepts | ACLI now, future adapters later | Certified as ACLI-specific first interface | Extract reusable session contract for future adapters |
| Conversational turn lineage | Platform conversation/session service plus interface adapter | ACLI now, future adapters later | Certified under ACLI | Promote shared conversation artifact model |
| Operator rendering | Interface adapter rendering from platform view models | ACLI, Web, Mobile, Voice | Certified under ACLI | Keep adapter-specific rendering; move shared response model to Platform Core |
| Confirmation classification | Shared human intent / confirmation service | ACLI, Web, Mobile, REST, Voice | Certified under ACLI runtime | Candidate for platform extraction before Web/Mobile |
| Proposal / approval bridge | Approval service / Platform Core | Interfaces, Product 1 | Certified through ACLI | Ensure reusable API exists outside ACLI |
| Authorization readiness bridge | Authorization service / Platform Core | Interfaces, Worker Layer | Certified through ACLI | Ensure reusable API exists outside ACLI |
| Product 1 workflow | Product 1 | Interfaces, OCS, Replay | Correct | None |
| Decision Packet | Product 1 | Interfaces, governance, audit | Correct as product artifact | None |
| OCS advisory attachment | Product 1 consumes OCS advisory | OCS, Product 1 | Correct if OCS owns cognition | None |
| Audit Packet | Product 1 | Governance, replay, enterprise review | Correct | None |
| Product 1 certification | Product 1 certification runtime | Governance/release | Correct | None |
| Deployment readiness | Release / Deployment platform service | Interfaces, Product 1 | Planned later | Keep outside ACLI and Product 1 |
| Replay integrity | Replay service | All subsystems | Correct as platform invariant | None |
| Governance checkpoints | Governance service | All subsystems | Correct as platform invariant | None |

## 4. G3-04 Ownership Findings

| G3-04 Capability | Correct Owner | ACLI Role | Product 1 Role | Finding |
| --- | --- | --- | --- | --- |
| Provider identity | Provider Layer / Platform Core | Display and initiate governed setup | Consume identity evidence if relevant | Correct in Phase 1 |
| Provider registry | Provider Layer / Platform Core | Query and render registry state | Query permitted Product 1 provider roles | Missing shared implementation |
| Provider activation | Provider Layer policy + Governance | Request activation, show approval state | Consume only after activation evidence | Must not be ACLI-owned |
| Provider invocation | Provider Layer, orchestrated by OCS | Initiate eligible workflow and render result | Consume OCS advisory evidence | Must be platform-owned |
| Provider comparison | Provider Layer / OCS comparison substrate | Display comparison result | Consume comparison evidence | Must be platform-owned |
| Escalation | Provider Layer policy service | Ask for human confirmation where required | Consume final advisory evidence | Must be platform-owned |
| Provider rendering | Shared provider view model + interface adapter rendering | Render ACLI-specific text | Render Product 1-specific evidence | Split ownership required |
| Product 1 provider usage | Product 1 consumes OCS/provider advisory evidence | Start/render Product 1 workflow | Own Product 1 artifacts only | Correct if provider layer remains owner |

G3-04 program currently includes "ACLI provider-assisted interaction rendering" as an
implementation step. That is acceptable only if it means ACLI adapter rendering. The shared
provider interaction model, provider status model, escalation state, comparison result, and
cost/failure evidence must belong to Platform Core provider services.

## 5. G3-05 Ownership Findings

| G3-05 Capability | Correct Owner | ACLI Role | Product 1 Role | Finding |
| --- | --- | --- | --- | --- |
| Worker registry | Worker Layer / Platform Core | Render available certified workers | Consume worker evidence only if Product 1 scenario needs it | Missing shared implementation |
| Worker lifecycle | Worker Layer | Show lifecycle status | Consume lifecycle evidence | Must not be ACLI-owned |
| Worker orchestration | Worker Layer with approval/authorization gates | Initiate governed workflow | Provide product context where applicable | Must be platform-owned |
| Worker authorization | Approval / Authorization service | Collect/display approval state | Consume authorization evidence | Should be shared, not ACLI-owned |
| Worker execution | Worker Layer | No execution ownership | No execution ownership | Must remain outside ACLI/Product 1 |
| Worker replay | Replay + Worker Layer | Render replay references | Consume replay evidence | Platform-owned |
| Worker selection | Worker policy service | Ask user only when policy requires | Consume selected worker evidence | Platform-owned |

G3-05 should not depend on ACLI as the worker orchestration substrate. ACLI may be the first
operator interface for worker workflows, but Web, REST, Mobile, Voice, and future adapters
must be able to initiate the same governed worker lifecycle through platform APIs.

## 6. G3-02 ACLI Re-Review

Certified G3-02 runtime scope:

- session lifecycle;
- conversational continuity;
- operator rendering;
- confirmation classification;
- proposal / approval bridge;
- authorization readiness bridge;
- runtime certification.

Audit result:

| ACLI Responsibility | Classification | Long-Term Placement |
| --- | --- | --- |
| Command input handling | ACLI interface | ACLI |
| Terminal/operator rendering | ACLI interface | ACLI |
| ACLI session id and local interface lineage | ACLI interface | ACLI |
| Human conversation turn capture | Shared platform session model plus ACLI adapter | Extract shared model |
| Confirmation classification | Shared human confirmation service | Platform Core candidate |
| Proposal creation bridge | Shared proposal service | Platform Core / Approval |
| Approval request tracking | Shared approval service | Platform Core / Approval |
| Authorization readiness evidence | Shared authorization service | Platform Core / Authorization |
| CSA display | Interface rendering | ACLI adapter over CSA |
| Provider unavailable handling | Provider policy/failure service plus ACLI rendering | Platform Core plus ACLI adapter |
| Worker unavailable handling | Worker policy/failure service plus ACLI rendering | Platform Core plus ACLI adapter |

Conclusion:

G3-02 certification remains valid. It certified ACLI as the first implementation of these
flows, not as permanent owner of all reusable lifecycle, confirmation, proposal, approval,
and authorization services.

Roadmap correction is required before additional interfaces are added: define shared
Platform Core contracts for session/conversation, confirmation, proposal, approval, and
authorization evidence that ACLI already exercises.

## 7. G3-03 Product 1 Re-Review

Certified G3-03 Product 1 scope:

- workflow foundation;
- Decision Packet runtime;
- advisory-only OCS integration;
- Audit Packet assembly;
- Product 1 certification.

Audit result:

| Product 1 Responsibility | Classification | Long-Term Placement |
| --- | --- | --- |
| AI Decision Validator workflow | Product 1 | Product 1 |
| Decision Packet | Product 1 | Product 1 |
| Product 1 advisory consumption | Product 1 consumer of OCS/provider evidence | Product 1 |
| Product 1 audit packet | Product 1 | Product 1 |
| Product 1 certification evidence | Product 1 | Product 1 / Governance |
| Provider identity | Platform capability | Provider Layer |
| Provider invocation | Platform capability | Provider Layer / OCS |
| Worker execution | Platform capability | Worker Layer |
| Human interface rendering | Interface adapters | ACLI/Web/Mobile/etc. |

Conclusion:

Product 1 remains a consumer of platform services and does not currently become a platform
owner. No Product 1 certified runtime should be moved before G3-04 continues.

## 8. Misplaced Responsibilities

Misplaced or at-risk responsibilities:

| Responsibility | Current Risk | Required Owner |
| --- | --- | --- |
| Provider-assisted interaction model | G3-04 language risks ACLI ownership | Provider Layer / Platform Core |
| Provider status rendering model | G3-04 names ACLI rendering directly | Shared provider view model plus adapters |
| Provider escalation state | Could be implemented inside ACLI if not corrected | Provider policy service |
| Provider comparison result | Could be Product 1 or ACLI-specific | OCS / Provider comparison substrate |
| Worker workflow initiation | G3 master program ties worker expansion to ACLI readiness | Platform worker orchestration API |
| Confirmation classification | Certified under ACLI | Shared human confirmation service |
| Proposal / approval bridge | Certified under ACLI | Shared proposal and approval service |
| Authorization readiness bridge | Certified under ACLI | Shared authorization service |
| Conversational session model | Certified under ACLI | Shared session/conversation substrate plus adapters |

## 9. Duplicate Responsibilities

Potential duplicates:

| Duplicate Area | Existing Owners / Candidates | Resolution |
| --- | --- | --- |
| Provider identity | Historical provider registry/vault artifacts and new G3-04 Phase 1 runtime | Establish G3-04 provider identity boundary as current canonical substrate or map legacy artifacts into it |
| Credential lifecycle | Provider vault certification and G3-04 credential reference runtime | Separate secret vault ownership from replay-visible credential reference ownership |
| Provider readiness | Historical live-provider prerequisites and G3-04 provider activation program | Convert historical evidence into compatibility/legacy certification evidence |
| Operator rendering | ACLI rendering and future Web/Mobile/Voice rendering | Define shared platform response/view models |
| Approval/authorization bridge | ACLI certified bridge and future worker authorization | Promote reusable bridge contracts into Platform Core |
| Replay explanation | Explanation layers and future interface rendering | Keep replay data in Replay service; adapters render only |

## 10. Platform Capabilities Incorrectly Owned By ACLI

The current certified runtime does not permanently assign these to ACLI, but the roadmap
risks doing so unless corrected:

- provider-assisted interaction state;
- provider status and failure view model;
- provider escalation state;
- provider comparison rendering source model;
- confirmation classification;
- proposal and approval bridge contracts;
- authorization readiness bridge contracts;
- shared conversational session and turn lineage;
- worker workflow initiation model;
- worker failure and recovery model.

These should be Platform Core capabilities exposed to ACLI as the first adapter.

## 11. Platform Capabilities Incorrectly Owned By Product 1

No certified Product 1 runtime currently owns shared platform capabilities incorrectly.

At-risk future areas:

- Product 1 provider usage must not become provider invocation ownership;
- Product 1 audit evidence must not become global replay ownership;
- Product 1 worker-assisted validation must not become worker orchestration ownership;
- Product 1 decision support must not become OCS or Provider Layer ownership.

Product 1 should remain a consumer and product-specific evidence assembler.

## 12. Missing Platform Capabilities

Missing or insufficiently explicit shared capabilities:

| Missing Capability | Required Before |
| --- | --- |
| Shared interface session/conversation substrate | Web, Mobile, REST, Voice adapters |
| Shared human confirmation classifier/service | Multi-interface approval/confirmation flows |
| Shared proposal service contract | Worker execution and Product 1 integrations |
| Shared approval service contract | Worker execution and provider activation |
| Shared authorization readiness service | Worker execution |
| Provider registry service | G3-04 provider activation |
| Provider policy gate | G3-04 provider invocation |
| Provider invocation substrate | G3-04 first real provider call |
| Provider comparison substrate | G3-04 comparison and escalation |
| Provider view model | ACLI/Web/Mobile rendering |
| Worker registry service | G3-05 |
| Worker lifecycle service | G3-05 |
| Worker orchestration service | G3-05 |
| Worker selection policy | G3-05 |
| Worker view model | ACLI/Web/Mobile rendering |

## 13. Recommended Ownership Corrections

Required corrections:

1. Reframe ACLI as "first interface adapter" in all remaining G3 roadmap language.
2. Define Platform Core interface contracts for session, conversation, confirmation,
   proposal, approval, and authorization evidence.
3. Implement G3-04 provider registry, policy, invocation, escalation, and comparison as
   Provider Layer / Platform Core services.
4. Implement ACLI provider rendering only as adapter rendering over shared provider view
   models.
5. Implement Product 1 provider usage only as Product 1 consumption of OCS/provider advisory
   evidence.
6. Define G3-05 worker registry, lifecycle, orchestration, authorization, execution, replay,
   and selection as Worker Layer services.
7. Implement ACLI worker interaction only as adapter rendering and operator input capture.
8. Record compatibility mapping between historical provider/vault certification artifacts
   and the G3-04 provider identity substrate.

## 14. Required Roadmap Changes

Current high-level order remains valid:

```text
G3-02 -> G3-03 -> G3-04 -> G3-05 -> G3-06 -> G3-07
```

Required internal restructuring:

```text
G3-04 Phase 1 Provider Identity And Credential Boundaries
  -> G3-04 Phase 1.5 Platform Service Ownership Refactor
    -> shared provider registry contract
    -> shared provider policy gate contract
    -> shared provider view model contract
    -> legacy provider/vault compatibility mapping
  -> G3-04 Phase 2 Provider Registry And Policy Gates
  -> G3-04 Phase 3 Advisory Provider Invocation Substrate
  -> G3-04 Phase 4 OCS Provider Invocation Path
  -> G3-04 Phase 5 ACLI Provider Adapter Rendering
  -> G3-04 Phase 6 Product 1 Provider Advisory Binding
  -> G3-04 Phase 7 Escalation And Comparison
  -> G3-04 Certification
  -> G3-05 Worker Layer Program
```

G3-05 should begin with a Worker Layer ownership program before implementation:

```text
G3-05 Worker Layer Responsibility And Interface Adapter Program
  -> worker registry
  -> worker lifecycle
  -> worker authorization
  -> worker orchestration
  -> worker execution
  -> worker replay
  -> worker selection
  -> ACLI worker adapter rendering
```

## 15. Migration Impact

Impact:

| Area | Impact |
| --- | --- |
| G3-02 certified runtime | Certification remains valid; later extraction contracts needed |
| G3-03 certified runtime | Certification remains valid; Product 1 remains consumer |
| G3-04 Phase 1 runtime | Certification remains valid; provider identity layer is correctly placed |
| G3-04 remaining phases | Must be reworded and implemented as Platform Core / Provider Layer first |
| G3-05 worker expansion | Must start with Worker Layer ownership specification |
| Future Web/Mobile/REST/Voice | Benefit from platform service extraction |
| Tests | Future tests should target shared platform contracts plus ACLI adapter behavior |
| Replay | Replay evidence must identify platform service owner and interface adapter separately |

No runtime rollback is required for completed G3-02, G3-03, or G3-04 Phase 1.

## 16. Certification Impact

Certification impact:

- G3-02 remains certified as first human interface runtime.
- G3-03 remains certified as Product 1 consumer runtime.
- G3-04 Phase 1 remains certifiable as Provider Layer identity substrate.
- G3-04 should not proceed to provider invocation until ownership corrections are documented
  and accepted.
- Generation 3 final certification must include an interface-adapter portability checkpoint.

New certification checkpoint:

```text
INTERFACE_ADAPTER_PORTABILITY_PRESERVED
```

This checkpoint passes only when any capability used by ACLI and reusable by Web, Mobile,
REST, Voice, or future adapters is implemented as Platform Core service or explicitly
documented as ACLI-only interface behavior.

## 17. Final Assessment

Generation 3 should not be abandoned.

Generation 3 should not continue unchanged.

The architectural objective remains correct:

```text
AiGOL must be developable through ACLI using natural language without ChatGPT/Codex
copy-paste workflows.
```

The responsibility placement needs restructuring:

```text
ACLI is the first interface adapter.
Platform Core owns reusable capabilities.
Product 1 is a consumer.
Provider Layer owns provider identity, policy, invocation, escalation, and comparison.
Worker Layer owns worker registry, lifecycle, orchestration, execution, replay, and selection.
```

## 18. Final Verdict

```text
GENERATION_3_RESPONSIBILITY_RESTRUCTURING_REQUIRED
```
